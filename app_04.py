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

def save_to_dataframe(produto_info, df):
    new_row = pd.DataFrame([produto_info])
    df = pd.concat([df, new_row], ignore_index=True)
    return df

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
    df = pd.DataFrame()

    while True:
        url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-max-1-tb-titnio-natural-distribuidor-autorizado/p/MLB1040287867?pdp_filters=item_id:MLB3846015269#wid=MLB3846015269&sid=search&is_advertising=true&searchVariation=MLB1040287867&position=5&search_layout=stack&type=pad&tracking_id=84de19cc-05ee-4ed7-b75f-1bb31ae86928&is_advertising=true&ad_domain=VQCATCORE_LST&ad_position=5&ad_click_id=YTRkOTdiYWYtZjEwZS00ODRiLTgyNGEtMDg2OWNmODkzNjRm"
        page_content = fetch_page(url)
        produto_info = parse_page(page_content)
        df = save_to_dataframe(produto_info, df)
        print(df)
        time.sleep(10)