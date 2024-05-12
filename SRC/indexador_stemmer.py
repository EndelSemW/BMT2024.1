import logging
import pandas as pd
import math
from collections import defaultdict
import time
from nltk.stem import PorterStemmer
import csv

start_time = time.time()

# Configuração inicial do Logger e Stemmer
logging.basicConfig(filename="indexador.log", level=logging.INFO, format="%(asctime)s - %(message)s")
stemmer = PorterStemmer()

def apply_stemming(word):
    """Aplica stemming a uma palavra usando PorterStemmer."""
    word = str(word)
    return stemmer.stem(word.lower())

# Configuração de caminhos
path_config = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Config files\INDEX.CFG"
path_leitura = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Data\lista_invertida_stemmer.csv"
path_escrita = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Results\modelo_vetorial.csv"

logging.info("Iniciando execução do Indexador;")
logging.info(f"Lendo arquivo de configuração: {path_config};")

# Leitura da lista invertida
lista_invertida = pd.read_csv(path_leitura, sep=';', encoding="utf_8", header=None)
lista_invertida.columns = ['Word', 'Docs']

# Inicialização de estruturas de dados
doc_total_termos = defaultdict(int)
palavra_info = {}
tfidf_dic = defaultdict(lambda: defaultdict(float))
num_docs = 0

logging.info("Iniciando indexação.")

# Processamento dos dados
for index, row in lista_invertida.iterrows():
    stemmed_word = apply_stemming(row['Word'])
    documentos = row['Docs'].strip("[]").split(",")
    num_docs = max(num_docs, int(documentos[-1]))
    doc_set = set()
    for doc_id in documentos:
        doc_total_termos[doc_id] += 1
        doc_set.add(doc_id)
    palavra_info[stemmed_word] = len(doc_set)

logging.info(f"Total de documentos da coleção: {num_docs};")
logging.info("Iniciando cálculo do TF/IDF de cada termo.")

# Cálculo do TF-IDF
for index, row in lista_invertida.iterrows():
    word = str(row['Word'])
    stemmed_word = apply_stemming(word)
    documentos = row['Docs'].strip("[]").split(",")
    doc_freq = palavra_info[stemmed_word]
    idf = math.log(num_docs / doc_freq)
    for doc_id in documentos:
        tfidf_dic[stemmed_word][doc_id] += 1 / doc_total_termos[doc_id]
    for doc_id, tf in tfidf_dic[stemmed_word].items():
        tfidf = tf * idf
        logging.info(f"Word: {stemmed_word}, DocID: {doc_id}, TFIDF: {tfidf:.6f}")

# Escrita do arquivo de saída
with open(path_escrita, 'w', newline='', encoding='utf-8') as escreva_csv:
    writer = csv.writer(escreva_csv, delimiter=';')
    writer.writerow(['Word', 'DocNumber', 'TFIDF'])
    for word, docs in tfidf_dic.items():
        for doc_id, tfidf in docs.items():
            writer.writerow([word, doc_id, f"{tfidf:.6f}"])

end_time = time.time()
total_time = end_time - start_time
logging.info(f"Tempo de execução: {total_time}")
logging.info(f"Input do modelo vetorial {path_escrita} finalizado;")
logging.info("Fim da execução do Indexador.")
