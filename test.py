import requests

btc = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
eth = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT").json()

print("Bitcoin:", btc["price"])
print("Ethereum:", eth["price"])