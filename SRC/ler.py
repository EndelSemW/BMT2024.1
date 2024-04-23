def ler_configuracoes(nome_arquivo_cfg):
    configuracoes = {}
    with open(nome_arquivo_cfg, 'r') as arquivo:
        for linha in arquivo:
            chave, valor = linha.strip().split('=')
            configuracoes[chave] = valor
    return configuracoes

# Uso da função
config = ler_configuracoes(r'C:\Users\en_de\OneDrive\Documentos\Facul\Mestrado\BMT 2024.1\Config files\PC.CFG')
print(config)
