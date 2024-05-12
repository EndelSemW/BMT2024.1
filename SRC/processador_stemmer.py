import logging
import os
import xml.etree.ElementTree as ET
from unidecode import unidecode
import csv
import re
import time
from nltk.stem import PorterStemmer

# Configuração inicial
path_config = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Config files\PC.CFG"
path_data = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Data"
logging.basicConfig(filename="processador_consultas_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")
logging.info("Iniciando execução do Processador de Consultas.")

# Leitura da configuração de stemming
with open(path_config, 'r') as file:
    config_lines = file.readlines()
stemming_enabled = 'YES' == [line.split('=')[1].strip() for line in config_lines if line.startswith('STEMMER')][0]

# Instância do stemmer, se necessário
stemmer = PorterStemmer() if stemming_enabled else None

def process_query(query):
    """Normaliza e aplica stemming à consulta se necessário."""
    query = unidecode(query.lower())
    words = re.findall(r"\b\w+\b", query)
    if stemming_enabled:
        words = [stemmer.stem(word) for word in words]
    return ' '.join(words).upper()

def ler_config(path_config):
    """Lê o arquivo de configuração e retorna um dicionário com as instruções."""
    instrucoes = {}
    with open(path_config, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                instrucoes[key.strip()] = value.strip()
    return instrucoes

def processar_queries(arquivo_xml):
    """Lê e processa cada consulta do arquivo XML especificado."""
    tree = ET.parse(arquivo_xml)
    root = tree.getroot()
    queries = []

    for query in root.findall('.//QUERY'):
        query_number = query.find('QueryNumber').text
        query_text = query.find('QueryText').text
        processed_query = process_query(query_text)
        queries.append((query_number, processed_query))

    return queries

# Processamento principal
start_time = time.time()
instrucoes = ler_config(path_config)
arquivo_queries = os.path.join(path_data, instrucoes['LEIA'])
processed_queries = processar_queries(arquivo_queries)

# Salvando as consultas processadas
output_file = os.path.join(path_data, instrucoes['CONSULTAS'])
with open(output_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['QueryNumber', 'QueryText'])
    for query in processed_queries:
        writer.writerow(query)

end_time = time.time()
logging.info(f"Tempo de execução: {end_time - start_time}")
logging.info("A execução do processador de consultas foi finalizada.")
