from nltk.stem.porter import PorterStemmer
import logging
import csv
import xml.etree.ElementTree as ET
from unidecode import unidecode
import re
import os
import nltk
from nltk.corpus import stopwords
import time 

path_config = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Config files\GLI.CFG" 

with open(path_config, 'r') as file:
    config_lines = file.readlines()
stemming_enabled = [line.split('=')[1].strip() for line in config_lines if line.startswith('STEMMER')][0] == 'YES'

# Configurando o stemmer se necessário
if stemming_enabled:
    stemmer = PorterStemmer()

def apply_stemming(word):
    """Aplica o stemming à palavra se o stemming estiver habilitado."""
    return stemmer.stem(word) if stemming_enabled else word


path_config = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Config files\GLI.CFG" 
stopwords = set(stopwords.words('english'))

logging.basicConfig(filename="gerador_lista_invertida.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Iniciando execucao do gerador de lista invertida.")

# Função para ler o arquivo de configuração
def ler_arquivo_config(nome_arquivo_cfg):
    configuracoes = {'LEIA': [], 'ESCREVA': None}
    with open(nome_arquivo_cfg, 'r') as arquivo_cfg:
        for linha in arquivo_cfg:
            chave, valor = linha.strip().split('=')
            if chave == 'LEIA':
                configuracoes['LEIA'].append(valor)
            elif chave == 'ESCREVA':
                configuracoes['ESCREVA'] = valor
    return configuracoes

start_time = time.time()

# Função para processar os arquivos XML e retornar um gerador que produz tuplas contendo o numero do documento e uma lista de palavras extraidas 
#do campo ABSTRACT (ou EXTRACT dependendo do arquivo) e SE eles estiverem presentes. Caso nao, um aviso será emitido.
def processar_arquivos_xml(lista_arquivos_xml, nome_arquivo_saida):
    lista_invertida = {}
    
    for arquivo_xml in lista_arquivos_xml:
        logging.info(f"Processando arquivo XML: {arquivo_xml}")
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()

        for record in root.findall('.//RECORD'):
            record_num = record.find('RECORDNUM').text
            record_num = int(record_num)
            abstract_element = record.find('ABSTRACT') if record.find('ABSTRACT') is not None else record.find('EXTRACT')
            
            if abstract_element is not None and abstract_element.text:
                abstract = abstract_element.text
                abstract = unidecode(abstract.lower())
                abstract = re.sub(r'[^\w\s]', '', abstract)
                
                words = [word for word in re.findall(r'\b[a-zA-Z]+\b', abstract) if word not in stopwords]

                for palavra in words:
                    palavra_norm = palavra.upper()
                    if not palavra_norm.isdigit():
                        record_num_str = str(record_num)
                    if palavra_norm not in lista_invertida:
                        lista_invertida[palavra_norm] = [record_num_str]
                    elif record_num_str not in lista_invertida[palavra_norm]:
                        lista_invertida[palavra_norm].append(record_num_str)
            else:
                logging.warning(f"Opa meu guerreiro o documento {record_num} esta vazio. Sinto muito")

    with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv, delimiter=';')
        for palavra, lista_record_nums in lista_invertida.items():
            escritor.writerow([palavra, f"[{','.join(map(str, lista_record_nums))}]"])

    logging.info("Lista invertida criada com sucesso.")

def main():
    configuracoes = ler_arquivo_config(path_config)
    path_data = r"C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Data" 
    arquivos_xml = [os.path.join(path_data, nome_arquivo) for nome_arquivo in configuracoes['LEIA']]
    nome_arquivo_saida = os.path.join(path_data, configuracoes['ESCREVA'])

    processar_arquivos_xml(arquivos_xml, nome_arquivo_saida)

    logging.info("Execucao do gerador finalizada.")

    end_time = time.time()
    total_time= end_time-start_time
    logging.info(f"Tempo de execucao: {total_time}")

if __name__ == "__main__":
    main()
