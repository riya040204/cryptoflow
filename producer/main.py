import json
import time

import requests
from kafka import KafkaProducer


API_URL = "https://api.binance.com/api/v3/ticker/24hr"

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


def fetch_crypto_data(symbol):
    response = requests.get(
        API_URL,
        params={"symbol": symbol},
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    return {
        "symbol": symbol,
        "price": float(data["lastPrice"]),
        "volume": float(data["volume"]),
        "price_change_percent": float(data["priceChangePercent"]),
        "timestamp": int(time.time())
    }


if __name__ == "__main__":
    print("🚀 CryptoFlow Kafka Producer Started")

    while True:
        try:
            data = fetch_crypto_data("BTCUSDT")

            producer.send("crypto-prices", data)
            producer.flush()

            print(f"📤 Sent: {data}")

            time.sleep(5)

        except Exception as error:
            print(f"❌ Error: {error}")
            time.sleep(5)