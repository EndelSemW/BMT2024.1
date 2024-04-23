import logging
import pandas as pd
import math
from collections import defaultdict
import time

logging.basicConfig(filename="indexador.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logging.info("Iniciando execucao do Indexador;")

path_config = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Config files\INDEX.CFG"

start_time = time.time()

logging.info(f"Lendo arquivo de configuracao: {path_config};")
with open(path_config, 'r') as index_cfg:
    instrucoes = {line.split('=')[0].strip(): line.split('=')[1].strip() for line in index_cfg if '=' in line}

path_leitura = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Results\lista_invertida.csv"
path_escrita = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Results\modelo_vetorial.csv"

logging.info(f"Arquivo a ser lido: {path_leitura};")

lista_invertida = pd.read_csv(path_leitura, sep=';', encoding="utf_8", header=None)
lista_invertida.columns = ['Word','Docs']

doc_total_termos = defaultdict(int)
palavra_info = {}
tfidf_dic = defaultdict(list)
colunas_csv = ["Word;DocNumber;TFIDF\n"]
num_docs = 0

logging.info("Iniciando indexacao.")

for index, row in lista_invertida.iterrows():
    word = row['Word']
    documentos = row['Docs'].strip("[]").split(",")
    num_docs = max(num_docs, int(documentos[-1]))
    doc_set = set()
    for doc_id in documentos:
        doc_total_termos[doc_id] += 1
        doc_set.add(doc_id)
    palavra_info[word] = len(doc_set)

logging.info(f"Total de documentos da colecao: {num_docs};")
logging.info("Iniciando calculo do TF/IDF de cada termo.")

# Cálculo do TF-IDF
for index, row in lista_invertida.iterrows():
    word = row['Word']
    documentos = row['Docs'].strip("[]").split(",")
    doc_freq = palavra_info[word]
    idf = math.log(num_docs / doc_freq)
    tfidf_dic[word] = defaultdict(int)
    for doc_id in documentos:
        tfidf_dic[word][doc_id] += 1
    for doc_id, term_freq in tfidf_dic[word].items():
        tf = term_freq / doc_total_termos[doc_id]
        tfidf = tf * idf
        colunas_csv.append(f"{word};{doc_id};{tfidf:.6f}\n")

logging.info(f"Iniciando input do arquivo do modelo vetorial {path_escrita};")
with open(path_escrita, 'w', newline='', encoding='utf-8') as escreva_csv:
    escreva_csv.writelines(colunas_csv)

end_time = time.time()
total_time= end_time-start_time
logging.info(f"Tempo de execucao: {total_time}")

logging.info(f"Input do modelo vetorial {path_escrita} finalizado;")
logging.info("Fim da execucao do Indexador.")