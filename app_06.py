"""
Web Scraper para Monitoramento de Preços do Mercado Livre
=======================================================

Este script realiza web scraping do Mercado Livre para monitorar preços de produtos específicos.
Ele extrai informações como nome do produto, preço antigo, preço atual e valor da parcela.

Dependências
-----------
- requests: Para fazer requisições HTTP
- beautifulsoup4: Para parsing do HTML
- time: Para controle de intervalo entre requisições

Funções
-------
"""

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import sqlite3

def fetch_page(url: str) -> str:
    """
    Realiza a requisição HTTP para obter o conteúdo da página.

    Args:
        url (str): URL completa do produto no Mercado Livre

    Returns:
        str: Conteúdo HTML da página

    Raises:
        requests.RequestException: Se houver erro na requisição HTTP
    """
    response = requests.get(url)
    return response.text

def parse_page(html: str) -> dict:
    """
    Analisa o HTML da página e extrai informações relevantes do produto.

    Args:
        html (str): Conteúdo HTML da página do produto

    Returns:
        dict: Dicionário contendo as seguintes informações:
            - product_name (str): Nome do produto
            - old_price (int): Preço antigo em centavos
            - new_price (int): Preço atual em centavos
            - installment_price (int): Valor da parcela em centavos

    Raises:
        AttributeError: Se algum elemento não for encontrado na página
    """
    soup = BeautifulSoup(html, 'html.parser')
    product_name = soup.find('h1', class_='ui-pdp-title').get_text()
    prices: list = soup.find_all('span', class_='andes-money-amount__fraction')
    old_price: int = int(prices[0].get_text().replace('.', ''))
    new_price: int = int(prices[1].get_text().replace('.', ''))
    installment_price: int = int(prices[2].get_text().replace('.', ''))
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'product_name': product_name,
        'old_price': old_price,
        'new_price': new_price,
        'installment_price': installment_price,
        'timestamp': timestamp
    }
def create_connection(db_name='iphone_price.db'):
    """ Criar uma conecção com o BD Sqlite """
    conn = sqlite3.connect(db_name)
    return conn

def setup_database(conn):
    """ Criar uma tabela de preços se não existir """
    cursor = conn.cursor()
    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS prices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            old_price INTEGER,
            new_price INTEGER,
            installment_price INTEGER,
            timestamp TEXT
          ) 
    """)
    conn.commit()

def save_to_database(conn, produto_info):
    """ Salvar uma linha de dados no BD SQlite usando pandas """
    new_row = pd.DataFrame([produto_info])
    new_row.to_sql('prices', conn, if_exists='append', index=False)

def get_max_venda(conn):
    """ Consulta o maior preço registrado até o momento """
    # Cria um cursor para interagir com o banco de dados
    cursor = conn.cursor()

    # Executa uma consulta SQL para encontrar o maior preço (new_price) 
    # e o timestamp correspondente
    cursor.execute("SELECT MAX(new_price), timestamp FROM prices")

    # Busca o primeiro resultado da consulta
    result = cursor.fetchone()

    # Verifica se existe um resultado e se o preço não é nulo
    if result and result[0] is not None:
        # Retorna uma tupla com o maior preço e seu timestamp
        return result[0], result[1]
    
    # Se não encontrar nenhum resultado, retorna None para preço e timestamp
    return None, None
    

if __name__ == "__main__":
    """
    Execução principal do script:
    1. Define a URL do produto a ser monitorado
    2. Realiza o scraping a cada 10 segundos
    3. Imprime as informações coletadas
    
    Importante:
    - O intervalo de 10 segundos é usado para evitar sobrecarga no servidor
    - Considere implementar tratamento de erros para requisições falhas
    - Verifique os termos de uso do site antes de usar em produção
    """
    conn = create_connection()
    setup_database(conn)


    while True:
        # Faz a requisição e persing da página
        url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-max-1-tb-titnio-natural-distribuidor-autorizado/p/MLB1040287867?pdp_filters=item_id:MLB3846015269#wid=MLB3846015269&sid=search&is_advertising=true&searchVariation=MLB1040287867&position=5&search_layout=stack&type=pad&tracking_id=84de19cc-05ee-4ed7-b75f-1bb31ae86928&is_advertising=true&ad_domain=VQCATCORE_LST&ad_position=5&ad_click_id=YTRkOTdiYWYtZjEwZS00ODRiLTgyNGEtMDg2OWNmODkzNjRm"
        page_content = fetch_page(url)
        produto_info = parse_page(page_content)
        current_price = produto_info['new_price']

        # Óbtem o maior preço já salvo
        max_price, max_price_timestamp = get_max_venda(conn)

        #comparação de preços

        if max_price is None or current_price > max_price:
            print(f"Preço maior detectado: {current_price}")
            max_price = current_price #atualiza o maior preço
            max_price_timestamp = produto_info['timestamp'] #atualiza timestamp do maior preço"
        else:
            print(f"O maior preço registrado é: {max_price} em e{max_price_timestamp}")
        
        #Salvar os dados no bd SQLite

        save_to_database(conn, produto_info)
        print("Dados salvos no banco:", produto_info)

        #aguardar 10 segundos
        time.sleep(10)
    
        conn.close
            

