import os
import requests
import pdfplumber
from selenium import webdriver
from selenium.webdriver.common.by import By

class PegarBoletimDeCaxias:
    def __init__(self, url_base, download_folder, txt_folder, inicio=2022, fim=2025):
        self.url_base = url_base
        self.download_folder = download_folder
        self.txt_folder = txt_folder
        self.inicio = inicio
        self.fim = fim
        self.driver = webdriver.Chrome(options=self.get_chrome_options())

        # Cria as pastas de download e TXT se não existirem
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
        if not os.path.exists(self.txt_folder):
            os.makedirs(self.txt_folder)

    def get_chrome_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Executa sem abrir a interface gráfica
        return options

    def pegar_pdfs(self):
        for ano in range(self.inicio, self.fim + 1):
            url = f"{self.url_base}{ano}.html"
            print(f"Acessando página: {url}")
            self.driver.get(url)

            # Encontrar todos os links na página
            links = self.driver.find_elements(By.TAG_NAME, 'a')

            # Filtrar links que possuem ".pdf" no href
            pdf_links = [link.get_attribute('href') for link in links if '.pdf' in link.get_attribute('href')]

            print(f"Número de arquivos PDF encontrados para {ano}: {len(pdf_links)}")

            # Baixar os arquivos PDF
            for link in pdf_links:
                self.baixar_pdf(link)

        # Fechar o navegador
        self.driver.quit()

    def baixar_pdf(self, link):
        # Obter o nome do arquivo a partir da URL
        nome_arquivo = link.split('/')[-1]
        caminho_arquivo_pdf = os.path.join(self.download_folder, nome_arquivo)

        # Verificar se o arquivo já existe antes de baixar
        if os.path.exists(caminho_arquivo_pdf):
            print(f"Arquivo {nome_arquivo} já existe. Pulando download.")
        else:
            try:
                response = requests.get(link)
                with open(caminho_arquivo_pdf, 'wb') as f:
                    f.write(response.content)
                print(f"Arquivo {nome_arquivo} baixado com sucesso.")
            except Exception as e:
                print(f"Erro ao baixar {link}: {e}")

        # Converter o PDF em TXT após o download
        self.converter_pdf_para_txt(caminho_arquivo_pdf, nome_arquivo)

    def converter_pdf_para_txt(self, caminho_arquivo_pdf, nome_arquivo):
        """Converte o PDF baixado em um arquivo de texto."""
        caminho_arquivo_txt = os.path.join(self.txt_folder, f"{os.path.splitext(nome_arquivo)[0]}.txt")

        if os.path.exists(caminho_arquivo_txt):
            print(f"Arquivo TXT {os.path.basename(caminho_arquivo_txt)} já existe. Pulando conversão.")
            return

        try:
            with pdfplumber.open(caminho_arquivo_pdf) as pdf:
                texto_completo = ""
                for pagina in pdf.pages:
                    texto_completo += pagina.extract_text() or ""

                with open(caminho_arquivo_txt, "w", encoding="utf-8") as txt_file:
                    txt_file.write(texto_completo)
                print(f"Arquivo TXT {os.path.basename(caminho_arquivo_txt)} criado com sucesso.")
        except Exception as e:
            print(f"Erro ao converter {caminho_arquivo_pdf} para TXT: {e}")

# Uso da classe
url_base = 'https://duquedecaxias.rj.gov.br/portal/'
pasta_download = 'boletim_dc'
pasta_txt = 'boletim_dc_txt'

boletim = PegarBoletimDeCaxias(url_base, pasta_download, pasta_txt)
boletim.pegar_pdfs()
