from flask import Flask, request, jsonify, send_from_directory
import os
from flask_cors import CORS
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite CORS em todas as rotas

# Mapeamento de cidades para suas pastas correspondentes
CIDADES = {
    "duque_de_caxias": {
        "txt": "boletim_dc_txt",
        "pdf": "boletim_dc"
    },
    "belford_roxo": {
        "txt": "boletim_blrx_txt",
        "pdf": "boletim_blrx"
    }
}

# Mapeamento de meses em português para números
MES_MAP = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12
}

# Expressão regular para capturar a data no formato "dd de mês de aaaa"
data_regex = re.compile(
    r'\b([1-9]|[12][0-9]|3[01]) de (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro) de (2000|20[01]\d|202[0-5])\b',
    re.IGNORECASE)


# Função para extrair a data do nome do arquivo e converter para timestamp
def extrair_data(nome_pdf):
    match = re.search(r'(\d+)_de_(\w+)_\d{4}', nome_pdf)
    if match:
        dia = int(match.group(1))
        mes = MES_MAP.get(match.group(2).lower(), 0)
        ano = int(re.search(r'\d{4}', nome_pdf).group(0))
        if mes:
            data = datetime(ano, mes, dia)
            return data.timestamp(), data.strftime("%Y-%m-%d %H:%M:%S")
    return None, None


# Função para extrair a data da quarta linha do arquivo de texto
def extrair_data_quarta_linha(arquivo_txt):
    try:
        with open(arquivo_txt, "r", encoding="utf-8") as f:
            linhas = f.readlines()
            if len(linhas) >= 4:
                quarta_linha = linhas[3].strip()
                match = data_regex.search(quarta_linha)
                if match:
                    dia = int(match.group(1))
                    mes = MES_MAP[match.group(2).lower()]
                    ano = int(match.group(3))
                    data = datetime(ano, mes, dia)
                    return data.timestamp(), data.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Erro ao extrair data da quarta linha do arquivo {arquivo_txt}: {e}")
    return None, None


# Função que procura nos arquivos TXT o termo e retorna os PDFs correspondentes com a quantidade de correspondências e datas
def encontrar_pdfs_correspondentes(termo_busca):
    pdfs_correspondentes = []

    for cidade, pastas in CIDADES.items():
        pasta_txt = pastas["txt"]
        pasta_pdf = pastas["pdf"]

        # Procura nos arquivos TXT da pasta específica da cidade
        for arquivo_txt in os.listdir(pasta_txt):
            if arquivo_txt.endswith(".txt"):
                caminho_arquivo_txt = os.path.join(pasta_txt, arquivo_txt)
                try:
                    with open(caminho_arquivo_txt, "r", encoding="utf-8") as f:
                        conteudo = f.read()
                        count = conteudo.lower().count(termo_busca.lower())
                        print(f"Lendo {arquivo_txt}: {count} correspondências encontradas para o termo '{termo_busca}'")
                        if count > 0:
                            # Substitui a extensão .txt por .pdf e verifica se o PDF existe
                            nome_pdf = arquivo_txt.replace(".txt", ".pdf")
                            caminho_pdf = os.path.join(pasta_pdf, nome_pdf)
                            if os.path.isfile(caminho_pdf):
                                # Extrai a data da quarta linha do arquivo de texto para Belford Roxo, ou do nome do arquivo para Duque de Caxias
                                if cidade == "belford_roxo":
                                    timestamp, data_formatada = extrair_data_quarta_linha(caminho_arquivo_txt)
                                else:
                                    timestamp, data_formatada = extrair_data(nome_pdf)

                                pdfs_correspondentes.append({
                                    "cidade": cidade.replace('_', ' ').title(),
                                    "nome_pdf": nome_pdf,
                                    "quantidade_correspondencias": count,
                                    "timestamp": timestamp,
                                    "data": data_formatada,
                                    "termo": termo_busca
                                })
                except Exception as e:
                    print(f"Erro ao ler o arquivo {arquivo_txt}: {e}")

    return pdfs_correspondentes


# Endpoint para buscar PDFs com base no termo de busca
@app.route('/encontrar-pdfs', methods=['POST'])
def encontrar_pdfs():
    dados = request.json
    termo_busca = dados.get("termo", "")

    if not termo_busca:
        return jsonify({"erro": "O termo de busca é obrigatório."}), 400

    pdfs = encontrar_pdfs_correspondentes(termo_busca)

    return jsonify({"pdfs": pdfs})


# Endpoint para servir PDFs a partir do Flask
@app.route('/<cidade>/<filename>')
def serve_pdf(cidade, filename):
    cidade = cidade.lower().replace(' ', '_')
    if cidade not in CIDADES:
        return jsonify({"erro": f"Cidade '{cidade}' não é suportada."}), 400

    pasta_pdf = CIDADES[cidade]["pdf"]
    return send_from_directory(pasta_pdf, filename)


if __name__ == '__main__':
    app.run(debug=True)