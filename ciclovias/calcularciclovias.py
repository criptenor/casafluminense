import geopandas as gpd

# Lista com os caminhos dos arquivos GeoJSON
caminhos_geojson = [
    'geojson/Ciclovia_Nilopolis.geojson',
    'geojson/Ciclovia_Nova_Iguacu.geojson',
    'geojson/Ciclovia_Nova_Japeri.geojson'
]

# Loop para calcular o comprimento de cada ciclovia
for caminho in caminhos_geojson:
    # Carregar o arquivo GeoJSON
    ciclovias = gpd.read_file(caminho)

    # Reprojetar para um sistema de coordenadas apropriado para medir distâncias (EPSG:3857)
    ciclovias_metric = ciclovias.to_crs(epsg=3857)

    # Calcular o comprimento de cada ciclovia em metros
    ciclovias_metric['comprimento_metros'] = ciclovias_metric.geometry.length

    # Converter de metros para quilômetros
    ciclovias_metric['comprimento_km'] = ciclovias_metric['comprimento_metros'] / 1000

    # Somar o comprimento total em quilômetros
    comprimento_total_km = ciclovias_metric['comprimento_km'].sum()

    # Exibir o nome do arquivo e o comprimento total das ciclovias
    print(f"Arquivo: {caminho}")
    print(f"Comprimento total das ciclovias: {comprimento_total_km:.2f} km\n")
