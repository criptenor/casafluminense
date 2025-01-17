from flask import Flask, request, jsonify, send_from_directory
import os
from flask_cors import CORS
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite CORS em todas as rotas

PASTA_TXT = "boletim_dc_txt"
PASTA_PDF = "boletim_dc"

# Mapeamento de meses em português para números
MES_MAP = {
    "Janeiro": 1,
    "Fevereiro": 2,
    "Março": 3,
    "Abril": 4,
    "Maio": 5,
    "Junho": 6,
    "Julho": 7,
    "Agosto": 8,
    "Setembro": 9,
    "Outubro": 10,
    "Novembro": 11,
    "Dezembro": 12
}

# Função para extrair a data do nome do arquivo e converter para timestamp
def extrair_data(nome_pdf):
    match = re.search(r'(\d+)_de_(\w+)_\d{4}', nome_pdf)
    if match:
        dia = int(match.group(1))
        mes = MES_MAP.get(match.group(2), 0)
        ano = int(re.search(r'\d{4}', nome_pdf).group(0))
        if mes:
            data = datetime(ano, mes, dia)
            return data.timestamp(), data.strftime("%Y-%m-%d %H:%M:%S")
    return None, None

# Função que procura nos arquivos TXT o termo e retorna os PDFs correspondentes com a quantidade de correspondências e datas
def encontrar_pdfs_correspondentes(termo_busca):
    pdfs_correspondentes = []

    # Procura nos arquivos TXT da pasta boletim_dc_txt
    for arquivo_txt in os.listdir(PASTA_TXT):
        if arquivo_txt.endswith(".txt"):
            caminho_arquivo_txt = os.path.join(PASTA_TXT, arquivo_txt)
            try:
                with open(caminho_arquivo_txt, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                    count = conteudo.lower().count(termo_busca.lower())
                    print(f"Lendo {arquivo_txt}: {count} correspondências encontradas para o termo '{termo_busca}'")
                    if count > 0:
                        # Substitui a extensão .txt por .pdf e verifica se o PDF existe
                        nome_pdf = arquivo_txt.replace(".txt", ".pdf")
                        caminho_pdf = os.path.join(PASTA_PDF, nome_pdf)
                        if os.path.isfile(caminho_pdf):
                            timestamp, data_formatada = extrair_data(nome_pdf)
                            pdfs_correspondentes.append({
                                "nome_pdf": nome_pdf,
                                "quantidade_correspondencias": count,
                                "timestamp": timestamp,
                                "data": data_formatada
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

    # Verifica se as pastas existem
    if not os.path.isdir(PASTA_TXT):
        return jsonify({"erro": f"A pasta de arquivos TXT '{PASTA_TXT}' não foi encontrada."}), 400

    if not os.path.isdir(PASTA_PDF):
        return jsonify({"erro": f"A pasta de arquivos PDF '{PASTA_PDF}' não foi encontrada."}), 400

    pdfs = encontrar_pdfs_correspondentes(termo_busca)

    return jsonify({"pdfs": pdfs})

# Endpoint para servir PDFs a partir do Flask
@app.route('/boletim_dc/<filename>')
def serve_pdf(filename):
    return send_from_directory(PASTA_PDF, filename)

if __name__ == '__main__':
    app.run(debug=True)