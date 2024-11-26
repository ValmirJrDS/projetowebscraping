import requests
from bs4 import BeautifulSoup
import time

def fetch_page(url):
	response = requests.get(url)
	return response.text

def parse_page(html):
	soup = BeautifulSoup(html, 'html.parser')
	product_name = soup.find('h1', class_='ui-pdp-title').get_text()
	prices: list = soup.find_all('span', class_='andes-money-amount__fraction')
	old_price: int = int(prices[0].get_text().replace('.', ''))
	new_price: int = int(prices[1].get_text().replace('.', ''))
	installment_price: int = int(prices[2].get_text().replace('.', ''))

	return{
		'product_name' : product_name,
		'old_price' : old_price,
		'new_price' : new_price,
		'installment_price' : installment_price
		
	}
	

if __name__ == "__main__":
	while True:
		url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-max-1-tb-titnio-natural-distribuidor-autorizado/p/MLB1040287867?pdp_filters=item_id:MLB3846015269#wid=MLB3846015269&sid=search&is_advertising=true&searchVariation=MLB1040287867&position=5&search_layout=stack&type=pad&tracking_id=84de19cc-05ee-4ed7-b75f-1bb31ae86928&is_advertising=true&ad_domain=VQCATCORE_LST&ad_position=5&ad_click_id=YTRkOTdiYWYtZjEwZS00ODRiLTgyNGEtMDg2OWNmODkzNjRm"
		page_content = fetch_page(url)
		produto_info = parse_page(page_content)
		print(produto_info)
		time.sleep(10)
	