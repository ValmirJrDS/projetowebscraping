import requests
from bs4 import BeautifulSoup
import time
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()

# Configuração do Bot Telegram
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TOKEN)

# Configuração do PostgreSQL
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)

def fetch_page(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

def parse_page(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    product_name = soup.find('h1', class_='ui-pdp-title').get_text()
    prices = soup.find_all('span', class_='andes-money-amount__fraction')
    return {
        'product_name': product_name,
        'old_price': int(prices[0].get_text().replace('.', '')),
        'new_price': int(prices[1].get_text().replace('.', '')),
        'installment_price': int(prices[2].get_text().replace('.', '')),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

from sqlalchemy import text

def setup_database(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS prices (
                id SERIAL PRIMARY KEY,
                product_name TEXT,
                old_price INTEGER,
                new_price INTEGER,
                installment_price INTEGER,
                timestamp TIMESTAMP
            )
        """))
        conn.commit()


def save_to_database(engine, produto_info):
    new_row = pd.DataFrame([produto_info])
    new_row.to_sql('prices', engine, if_exists='append', index=False)

from sqlalchemy import text

def get_max_price(engine):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT new_price, timestamp 
            FROM prices 
            WHERE new_price = (SELECT MAX(new_price) FROM prices);
        """))
        row = result.fetchone()
        if row:
            return row[0], row[1]
        else:
            print("Aviso: Nenhum dado encontrado na tabela 'prices'.")
            return None, None



async def send_telegram_message(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

async def main():
    setup_database(engine)

    try:
        while True:
            url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-max-1-tb-titnio-natural-distribuidor-autorizado/p/MLB1040287867"
            page_content = fetch_page(url)
            if not page_content:
                await asyncio.sleep(10)
                continue

            produto_info = parse_page(page_content)
            current_price = produto_info['new_price']

            max_price, max_price_timestamp = get_max_price(engine)
            if max_price is None or current_price > max_price:
                print(f"Novo maior preço detectado: {current_price}")
                await send_telegram_message(f"Novo maior preço: R${current_price / 100}")
            else:
                message = f"O maior preço registrado é R${max_price / 100} em {max_price_timestamp}"
                print(message)
                await send_telegram_message(message)

            save_to_database(engine, produto_info)
            print("Dados salvos:", produto_info)

            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("Parando a execução...")
    finally:
        print("Conexão finalizada!")

asyncio.run(main())
