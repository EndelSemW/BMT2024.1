import csv
import logging
import os
import numpy as np
from unidecode import unidecode
import re
import time
import pandas as pd


logging.basicConfig(filename="buscador.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info('Iniciando execucao do Buscador.')

start_time = time.time()

def similaridades(modelo, vetor, norma_matriz):
    norma_vetor = np.linalg.norm(vetor)
    if norma_vetor == 0:
        return np.zeros(modelo.shape[1])
    similaridades = []
    for documento in range(len(modelo[0])):
        similaridade = 0
        coluna = modelo[:, documento]
        norma_doc = norma_matriz[documento]
        if norma_doc != 0: 
            similaridade = np.dot(vetor, coluna) / (norma_vetor * norma_doc)
        similaridades.append(similaridade)
    return similaridades

# Normalização de texto
def normalizar_texto(texto):
    texto = unidecode(texto.strip().lower())
    texto = re.sub(r"[^a-z0-9\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.upper()


caminho_config = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Config files\BUSCA.CFG"

logging.info('Lendo arquivo .CFG')
configuracoes = {}
with open(caminho_config, 'r') as arquivo_cfg:
    for linha in arquivo_cfg:
        chave, valor = linha.strip().split('=')
        configuracoes[chave] = valor.strip()


modelo_arquivo = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Results\modelo_vetorial.csv"
consultas_arquivo = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Results\consultas.csv"
resultados_arquivo = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Results\resultados.csv"


logging.info('Carregando modelo vetorial')
modelo_vetorial = pd.read_csv(modelo_arquivo, delimiter=';', dtype={'DocNumber': str})


logging.info('Carregando consultas')
consultas_df = pd.read_csv(consultas_arquivo, delimiter=';')


palavras_index = {palavra: idx for idx, palavra in enumerate(modelo_vetorial['Word'].unique())}
doc_weights = {idx: float(w) for idx, w in enumerate(modelo_vetorial['TFIDF'].unique())}


modelo_matriz = np.zeros((len(palavras_index), len(doc_weights)))
normas_matriz = np.zeros(len(doc_weights))

for _, row in modelo_vetorial.iterrows():
    word_idx = palavras_index[row['Word']]
    doc_idx = int(row['DocNumber'])
    weight = row['TFIDF']
    modelo_matriz[word_idx, doc_idx] = weight
    normas_matriz[doc_idx] += weight ** 2

normas_matriz = np.sqrt(normas_matriz)


resultados = {}
for consulta in consultas_df.itertuples():
    texto_consulta = normalizar_texto(consulta.QueryText)
    vetor_consulta = np.zeros(len(palavras_index))
    
    for palavra in texto_consulta.split():
        palavra_idx = palavras_index.get(palavra)
        if palavra_idx is not None:
            vetor_consulta[palavra_idx] = 1
    
    similaridades_res = similaridades(modelo_matriz, vetor_consulta, normas_matriz)
    resultados[consulta.QueryNumber] = sorted(range(len(similaridades_res)), key=lambda i: similaridades_res[i], reverse=True)[:100]


logging.info('Escrevendo resultados no arquivo CSV')
with open(resultados_arquivo, 'w', newline='') as arquivo_res:
    escritor = csv.writer(arquivo_res, delimiter=';')
    escritor.writerow(['QueryNumber', 'DocRanking', 'DocNumber', 'Similarity'])
    
    for query_num, doc_indices in resultados.items():
        for rank, doc_idx in enumerate(doc_indices, start=1):
            escritor.writerow([query_num, rank, doc_idx, similaridades_res[doc_idx]])
          
end_time = time.time()
total_time= end_time-start_time
logging.info(f"Tempo de execucao: {total_time}")

logging.info('Fim da execucao do Buscador.')