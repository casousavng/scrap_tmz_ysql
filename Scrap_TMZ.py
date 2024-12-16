import mysql.connector
import sys
import urllib.request
import requests
import json
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import os

# Este script tem como objetivo extrair dados de notícias do site TMZ.com, com base numa lista de nomes de pesquisa.
# O script irá extrair os dados das notícias encontradas e armazená-los numa base de dados MySQL na cloud em www.aiven.io/.

# Para executar o script, é necessário instalar as seguintes bibliotecas:
# pip install mysql-connector-python
# pip install requests
# pip install beautifulsoup4

# Configuração inicial da base de dados online a partir da maquina virtual criada no site https://console.aiven.io/
# (na falha de conexao, verificar se a maquina esta online e se o user e password estao corretos)
nomeBD = 'defaultdb'
user_pass_host = {
    'user': '',
    'password': '',
    'host': '',
    'port': 11682
}

def conexao_base_dados(nome_pesquisa):
    try:
        conn = mysql.connector.connect(**user_pass_host)
        cursor = conn.cursor()
        cursor.execute(f"USE {nomeBD}")
        
        # Verificar se a tabela com o nome de pesquisa fornecido já existe na base de dados
        cursor.execute(f"SHOW TABLES LIKE '{nome_pesquisa}'")
        if cursor.fetchone():
            print(f"Base de dados corretamente acedida. A tabela com o nome '{nome_pesquisa}' já existe. \nA verificar atualizações nas noticias...")
        else:
            # Cria a tabela na base de dados para armazenar as notícias com o nome de pesquisa fornecido e os respetivos dados
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {nome_pesquisa} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome_pesquisa TEXT NOT NULL,
                tipo TEXT NOT NULL,
                link TEXT NOT NULL,
                titulo TEXT NOT NULL,
                data_criacao TEXT,
                data_publicacao TEXT,
                data_modificacao TEXT,
                texto_noticia TEXT
            )
            """)
            print(f"Base de dados corretamente acedida. A tabela com nome '{nome_pesquisa}' foi criada com sucesso.")

    except mysql.connector.Error as e:
        print(f"Erro ao configurar ou conectar com a base de dados: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def inserir_dados_noticias(nome_pesquisa, tipo, link, titulo, data_criacao, data_publicacao, data_modificacao, texto_noticia):
    try:
        conn = mysql.connector.connect(**user_pass_host)
        cursor = conn.cursor()
        cursor.execute(f"USE {nomeBD}")

        # Verificar se o link já existe na base de dados
        cursor.execute(f"SELECT data_modificacao FROM {nome_pesquisa} WHERE link = %s", (link,))
        resultado = cursor.fetchone()

        if resultado is None:
            # Se o link não existe, insere a notícia
            cursor.execute(f"""
            INSERT INTO {nome_pesquisa} (nome_pesquisa, tipo, link, titulo, data_criacao, data_publicacao, data_modificacao, texto_noticia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome_pesquisa, tipo, link, titulo, data_criacao, data_publicacao, data_modificacao, texto_noticia))
            conn.commit()
            # print("Dados inseridos com sucesso.") -> Para debug

        elif resultado[0] != data_modificacao:
            # Se o link existe mas a data de modificação é diferente, atualiza os dados
            cursor.execute(f"""
            UPDATE {nome_pesquisa}
            SET nome_pesquisa = %s,
                tipo = %s,
                titulo = %s,
                data_criacao = %s,
                data_publicacao = %s,
                data_modificacao = %s,
                texto_noticia = %s
            WHERE link = %s
            """, (nome_pesquisa, tipo, titulo, data_criacao, data_publicacao, data_modificacao, texto_noticia, link))
            conn.commit()
            # Para debug
            print("-> Alguns dados foram atualizados...continuando a extração de novos dados...")

        else:
            # Se o link e a data de modificação já existem e são iguais, não faz nada
            return 0

    # tratamento de exceções
    except mysql.connector.Error as e:
        print(f"Erro ao inserir dados na base de dados: {e}")
    finally:
        if conn:
            conn.close()

# Função auxiliar para extrair texto de um elemento, tratando o caso de NoneType
def extrair_texto(dado_extraido):
    if not dado_extraido:
        return None

    partes_texto = [] 
    for elemento in dado_extraido.children:
        if elemento.name == 'a':
            partes_texto.append(elemento.get_text(strip=True) + "")
        elif elemento.name in ['strong', 'em']:
            partes_texto.append(elemento.get_text(strip=True))
        elif isinstance(elemento, str):
            partes_texto.append(elemento)
    return ''.join(partes_texto).strip()

# Função para percorrer a página de uma notícia e extrair os dados
def scrap_pagina_noticia(url, nome_pesquisa, tipo):

    resposta = requests.get(url)
    conteudo = BeautifulSoup(resposta.content, 'html.parser')

    titulo = conteudo.find('h1', class_='article__header--headline-title') or conteudo.find('h1', class_='article__header--title')
    titulo_texto = extrair_texto(titulo) if titulo else 'Título não encontrado'

    json_ld = conteudo.find('script', type='application/ld+json')
    if json_ld:
        dados_json = json.loads(json_ld.string)
        data_criada = dados_json.get('dateCreated', 'Data não encontrada')
        data_publicada = dados_json.get('datePublished', 'Data não encontrada')
        data_modificada = dados_json.get('dateModified', 'Data não encontrada')
    else:
        data_publicada = data_criada = data_modificada = 'Datas não encontradas'

    conteudo_div = conteudo.find('div', class_='article__blocks clearfix')

    texto_noticia = ""
    if conteudo_div:
        paragrafos = conteudo_div.find_all('p')
        texto_noticia = " ".join([extrair_texto(p) for p in paragrafos])
    else:
        texto_noticia = 'Texto não encontrado'
    
    # Inserir os dados extraidos na base de dados com o nome de pesquisa formatado com '_' em vez de '+'
    inserir_dados_noticias(nome_pesquisa.replace('+', '_'), tipo, url, titulo_texto, formatar_data(data_criada), formatar_data(data_publicada), formatar_data(data_modificada), texto_noticia)

# Função para formatar a data no formato desejado (dd-mm-aaaa hh:mm:ss) incluindo o fuso horário (-7h Portugal)
def formatar_data(data):
    try:
        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M:%S%z')
        # Subtrair 7 horas ao fuso horário
        data_formatada = data_formatada - timedelta(hours=7)
        return data_formatada.strftime('%d-%m-%Y %H:%M:%S')
    except ValueError:
        return data

# Função para verificar se a primeira página de pesquisa não contém conteúdo
def verificar_primeira_pagina_vazia(url, nome_pesquisa):
    try:
        with urllib.request.urlopen(url) as resposta:
            resposta_conteudo = resposta.read()

        conteudo = BeautifulSoup(resposta_conteudo, 'html.parser')

        # Verificar se a página não contém conteúdo. Se tiver inicializa a construçao da tabela com o respetivo 'nome_pesquisa' na base de dados
        if conteudo.find(string="No Content Found"):
            return 0
        else:
            conexao_base_dados(nome_pesquisa.replace('+', '_'))
            print("A iniciar a extração de dados...")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return 0

# Função para obter os links das notícias das diversas páginas de pesquisa
def scrap_obter_todas_noticias(url, nome_pesquisa, tipo):
    try:
        with urllib.request.urlopen(url) as resposta:
            resposta_conteudo = resposta.read()

        conteudo = BeautifulSoup(resposta_conteudo, 'html.parser')
        links = conteudo.find_all('a', href=True)
            
        qtd_links = 0
        links_encontrados = set()

        for link in links:
            if 'https://www.tmz.com/20' in link['href'] and link['href'] not in links_encontrados:
                links_encontrados.add(link['href'])
                scrap_pagina_noticia(link['href'], nome_pesquisa.replace('+', '_'), tipo)
                qtd_links += 1
                # Adiciona um temporizador aleatório entre 1 e 3 segundos para evitar ser bloqueado
                time.sleep(random.uniform(1, 3))
                #print(link['href']) -> Para debug
        return qtd_links

    # tratamento de exceções
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return 0

# Função para percorrer as páginas de pesquisa e obter os links das notícias
def scrap_paginas(nome_pesquisa, tipo):

    paginas = 1
    total_links = 0

    url_noticias = 'https://www.tmz.com/search/?q=' + nome_pesquisa + '&page=' + str(paginas)

    # Verificar se a primeira página de pesquisa não contém conteúdo
    if verificar_primeira_pagina_vazia(url_noticias, nome_pesquisa) == 0:
        print("Nenhum link util encontrado para o nome de pesquisa escolhido!")
        return 0, 0

    # Percorrer as páginas de pesquisa até à página 20 (da 21 para a frente sao repetidas)
    while True and paginas <= 20:
        url_noticias = 'https://www.tmz.com/search/?q=' + nome_pesquisa + '&page=' + str(paginas)
        qtde_links = scrap_obter_todas_noticias(url_noticias, nome_pesquisa, tipo)
        if qtde_links == 0:
            print("Mais nenhum link util encontrado! Encerrando a extração.")
            break

        total_links += qtde_links
        paginas += 1
        time.sleep(1)
    return paginas,total_links

# Ficheiro JSON com os nomes a pesquisar
def carregar_lista_nomes():
    caminho_ficheiro = os.path.join(os.path.dirname(__file__), 'nomes.json')
    try:
        with open(caminho_ficheiro, 'r', encoding='utf-8') as ficheiro:
            return json.load(ficheiro)
    except Exception as e:
        print(f"Erro ao carregar o ficheiro com os nomes a pesquisar: {e}")
        sys.exit(1)

# Função principal adaptada para iterar automaticamente sobre o dicionário de celebridades
def main():

    tempo_total = time.time()  # Para medir o tempo total de execução
    total_links_geral = 0  # Contador total de links encontrados para todas as celebridades

    # Carregar a lista de celebridades a partir de um ficheiro JSON
    celebridades = carregar_lista_nomes()

    for tipo, nomes in celebridades.items():
        print(f"\n--- Iniciando a extração de dados para o tipo: {tipo} ---\n")
        
        for nome_pesquisa in nomes:
            # Formatar o nome de pesquisa para usar no URL (nao pode conter espaços)
            nome_formatado = nome_pesquisa.replace(' ', '+')

            print(f"A pesquisar dados sobre: {nome_pesquisa} [Tipo: {tipo}]")
            tempo = time.time()  # Para medir o tempo de execução por nome

            # Obter os links das notícias e extrair os dados
            paginas, total_links = scrap_paginas(nome_formatado, tipo)
            total_links_geral += total_links  # Atualizar o contador geral de links

            if total_links > 0:
                print(f"Total de páginas encontradas: {paginas-1}")
                print(f"Total de links úteis encontrados: {total_links}")
                # Calcular e exibir o tempo de execução em segundos ou minutos
                tempo_execucao = time.time() - tempo
                if tempo_execucao > 60:
                    minutos, segundos = divmod(tempo_execucao, 60)
                    print(f"Tempo de execução para '{nome_pesquisa}': {int(minutos)} minutos e {segundos:.2f} segundos")
                else:
                    print(f"Tempo de execução para '{nome_pesquisa}': {tempo_execucao:.2f} segundos")
                print(f"Extração de dados para '{nome_pesquisa}' concluída com sucesso!")
                print(f"---\n")
            else:
                print(f"Cancelando extração de dados para '{nome_pesquisa}' (nenhum link útil encontrado).")
                print(f"---\n")

    print(f"\n--- Extração de dados concluída para todos os tipos e celebridades ---")
    
    # Calcular e exibir o tempo total de execução
    tempo_total_execucao = time.time() - tempo_total
    if tempo_total_execucao > 3600:
        horas, resto = divmod(tempo_total_execucao, 3600)
        minutos, segundos = divmod(resto, 60)
        print(f"Tempo total de execução: {int(horas)} horas, {int(minutos)} minutos e {segundos:.2f} segundos")
    elif tempo_total_execucao > 60:
        minutos, segundos = divmod(tempo_total_execucao, 60)
        print(f"Tempo total de execução: {int(minutos)} minutos e {segundos:.2f} segundos")
    else:
        print(f"Tempo total de execução: {tempo_total_execucao:.2f} segundos")
    print(f"Total de links úteis encontrados no geral: {total_links_geral}")

# Executar a função principal
if __name__ == '__main__':
    main()