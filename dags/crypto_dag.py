from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta, timezone
import requests
import mysql.connector

COINS = ["BTC", "ETH", "SOL", "BNB", "XRP"]

def fetch_and_store():
    conn_details = BaseHook.get_connection("crypto_mysql")
    conn = mysql.connector.connect(
        host=conn_details.host,
        user=conn_details.login,
        password=conn_details.password,
        database=conn_details.schema
    )
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)

    for coin in COINS:
        # 24h ticker — has price, volume, high, low
        ticker = requests.get(
            f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}USDT"
        ).json()

        price        = float(ticker["lastPrice"])
        volume_24h   = float(ticker["quoteVolume"])   # volume in USD
        high_24h     = float(ticker["highPrice"])
        low_24h      = float(ticker["lowPrice"])
        change_pct   = float(ticker["priceChangePercent"])

        # get previous price from db for % change validation
        cursor.execute(
            "SELECT price_usd FROM prices WHERE coin = %s ORDER BY fetched_at DESC LIMIT 1",
            (coin.lower(),)
        )
        row = cursor.fetchone()
        if row:
            prev_price = float(row[0])
            price_change_pct = ((price - prev_price) / prev_price) * 100
        else:
            price_change_pct = change_pct  # fallback to Binance 24h change on first run

        cursor.execute(
    """INSERT INTO prices 
       (coin, price_usd, volume_24h, high_24h, low_24h, price_change_pct)
       VALUES (%s, %s, %s, %s, %s, %s)""",
    (coin.lower(), price, volume_24h, high_24h, low_24h, price_change_pct)
)
        print(f"{coin}: ${price} | 24h High: {high_24h} | Low: {low_24h} | Change: {change_pct}% | Vol: ${volume_24h:,.0f}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"All prices stored at {now}")

with DAG(
    dag_id="crypto_price_tracker",
    start_date=datetime(2024, 1, 1),
    schedule_interval=timedelta(minutes=5),
    catchup=False,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=1)
    }
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_crypto_prices",
        python_callable=fetch_and_store
    )