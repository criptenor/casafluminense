import os
import requests
import pdfplumber
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configurações do WebDriver usando WebDriverManager
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Diretórios onde os PDFs e os TXT serão salvos
pdf_directory = 'boletim_blrx'
txt_directory = 'boletim_blrx_txt'

# Cria os diretórios se eles não existirem
if not os.path.exists(pdf_directory):
    os.makedirs(pdf_directory)
if not os.path.exists(txt_directory):
    os.makedirs(txt_directory)


# Função para baixar o PDF
def download_pdf(pdf_url, pdf_directory, txt_directory):
    filename = os.path.basename(pdf_url)
    pdf_path = os.path.join(pdf_directory, filename)
    txt_path = os.path.join(txt_directory, f"{os.path.splitext(filename)[0]}.txt")

    # Verifica se o arquivo PDF já existe
    if os.path.exists(pdf_path):
        print(f"Arquivo {filename} já existe. Pulando download.")
        return

    response = requests.get(pdf_url)

    if response.status_code == 200:
        with open(pdf_path, 'wb') as file:
            file.write(response.content)
        print(f"PDF salvo em: {pdf_path}")

        # Converte o PDF para TXT
        convert_pdf_to_txt(pdf_path, txt_path)
    else:
        print(f"Falha ao baixar o PDF. URL: {pdf_url}, Status code: {response.status_code}")


# Função para converter PDF para TXT
def convert_pdf_to_txt(pdf_path, txt_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() or ''

            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
        print(f"Arquivo TXT salvo em: {txt_path}")
    except Exception as e:
        print(f"Erro ao converter {pdf_path} para TXT: {e}")


# Função para percorrer as páginas e baixar os PDFs
def process_pages(start_page, end_page, base_url, pdf_directory, txt_directory):
    for page in range(start_page, end_page + 1):
        url = f"{base_url}{page}"
        print(f"Acessando página: {url}")
        driver.get(url)

        # Aguarda até que os elementos da página sejam carregados
        driver.implicitly_wait(10)

        # Encontra o link que aponta para o arquivo PDF
        try:
            pdf_link = driver.find_element(By.XPATH, "//a[contains(@href, '.pdf')]").get_attribute('href')
            download_pdf(pdf_link, pdf_directory, txt_directory)
        except Exception as e:
            print(f"Nenhum PDF encontrado na página {url}. Pulando para a próxima página.")


# URL base da página a ser analisada
base_url = 'https://portal.cmbr.rj.gov.br/diariooficial/'

# Intervalo de páginas a serem processadas
start_page = 4
end_page = 350

# Processa as páginas e baixa os PDFs
process_pages(start_page, end_page, base_url, pdf_directory, txt_directory)

# Fecha o navegador
driver.quit()