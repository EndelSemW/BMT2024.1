import os
import xml.etree.ElementTree as ET
from unidecode import unidecode
import csv
import re
import logging
import time 

path_config = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Config files\PC.CFG"
path_log = "processador_consultas_log.txt"
path_data = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Data"

logging.basicConfig(filename=path_log, level=logging.INFO, format="%(asctime)s - %(message)s")
logging.info("Iniciando execucao do Processador de Consultas.")

start_time = time.time()

def ler_config(path_config):
    logging.info(f"Abrindo o arquivo de configuracao: {path_config}")
    with open(path_config, 'r') as pc_cfg:
        instrucoes = {linha.split('=')[0]: linha.split('=')[1].strip() for linha in pc_cfg}
    logging.info(f"Lendo as instrucoes: {instrucoes}")
    return instrucoes

instrucoes = ler_config(path_config)

def normalizar_texto(texto):
    texto = unidecode(texto.strip().lower())
    texto = re.sub(r"[^a-z0-9\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.upper()

def processar_queries_e_esperados(arquivo_xml):
    logging.info(f"Iniciando leitura do arquivo XML: {arquivo_xml}")
    tree = ET.parse(arquivo_xml)
    raiz = tree.getroot()
    
    queries = [('QueryNumber', 'QueryText')]
    esperados = [('QueryNumber', 'DocNumber', 'DocVotes')]
    
    for query in raiz.findall('QUERY'):
        query_number = query.find('QueryNumber').text
        query_text = normalizar_texto(query.find('QueryText').text)
        queries.append((query_number, query_text))
        
        for item in query.find('Records').findall('Item'):
            doc_number = item.text
            s = sum(1 for x in item.get('score', '0') if x != '0')
            esperados.append((query_number, doc_number, str(s)))
    
    logging.info("Leitura e processamento do aquivo concluidas.")
    return queries, esperados

# Escrevendo os arquivos CSV
def escrever_csv(dados, nome_arquivo):
    logging.info(f"Escrevendo dados no arquivo CSV: {nome_arquivo}")
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo, delimiter=';')
        escritor.writerows(dados)
    logging.info("Dados escritos com sucesso.")
    
    end_time = time.time()
    total_time= end_time-start_time
    logging.info(f"Tempo de execucao: {total_time}")

# Obtendo o caminho completo dos arquivos
file_leia = os.path.join(path_data, instrucoes['LEIA'])
file_consultas = os.path.join(path_data, instrucoes['CONSULTAS'])
file_esperados = os.path.join(path_data, instrucoes['ESPERADOS'])

queries, esperados = processar_queries_e_esperados(file_leia)
escrever_csv(queries, file_consultas)
escrever_csv(esperados, file_esperados)

logging.info("A execucao do processador de consultas foi finalizada.")
