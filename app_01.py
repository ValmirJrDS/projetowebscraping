import requests

def fetch_page(url):
	response = requests.get(url)
	return response.text

if __name__ == "__main__":
	url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-max-1-tb-titnio-natural-distribuidor-autorizado/p/MLB1040287867?pdp_filters=item_id:MLB3846015269#wid=MLB3846015269&sid=search&is_advertising=true&searchVariation=MLB1040287867&position=5&search_layout=stack&type=pad&tracking_id=84de19cc-05ee-4ed7-b75f-1bb31ae86928&is_advertising=true&ad_domain=VQCATCORE_LST&ad_position=5&ad_click_id=YTRkOTdiYWYtZjEwZS00ODRiLTgyNGEtMDg2OWNmODkzNjRm"
	page_content = fetch_page(url)
	print(page_content)