import requests

token = "7695130745:AAGTHwKDmLKAVqZqYG94bvG2qbENLIBAWvU"
url = f"https://api.telegram.org/bot7695130745:AAGTHwKDmLKAVqZqYG94bvG2qbENLIBAWvU/getUpdates"
response = requests.get(url)
print(response.json())  # Isso vai retornar o CHAT_ID correto
