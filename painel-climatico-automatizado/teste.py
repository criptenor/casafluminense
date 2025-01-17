import os

def encontrar_arquivos_com_plano_diretor(pasta_txt, termo_busca="Duque de Caxias"):
    """Procura por arquivos que contenham o termo de busca na pasta especificada."""
    arquivos_correspondentes = []

    for arquivo in os.listdir(pasta_txt):
        if arquivo.endswith(".txt"):
            caminho_arquivo = os.path.join(pasta_txt, arquivo)
            try:
                with open(caminho_arquivo, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                    if termo_busca.lower() in conteudo.lower():
                        arquivos_correspondentes.append(arquivo)
            except Exception as e:
                print(f"Erro ao ler o arquivo {arquivo}: {e}")

    # Exibir os arquivos encontrados
    if arquivos_correspondentes:
        print("Arquivos que contêm o termo 'Plano Diretor':")
        for arquivo in arquivos_correspondentes:
            print(f"- {arquivo}")
    else:
        print("Nenhum arquivo contém o termo 'Plano Diretor'.")

# Caminho para a pasta com os arquivos TXT
pasta_txt = "boletim_dc_txt"
encontrar_arquivos_com_plano_diretor(pasta_txt)
