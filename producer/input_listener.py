import requests
import time
import random
from queue import Queue
from threading import Thread
from db_config import get_db_connection

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
INTERVAL = 10  # base interval in seconds

# ✅ Reliable APIs
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=12.97&longitude=77.59&current_weather=true"
STOCK_API_URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo"
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"


# -------------------------------------------------
# DATABASE HELPER
# -------------------------------------------------
def ensure_topic_in_db(topic_name, created_by="producer"):
    """
    Insert the topic into the Admin DB if it doesn’t already exist.
    New topics start with 'pending' status, waiting for admin approval.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if topic already exists
        cur.execute("SELECT id FROM topics WHERE topic_name = %s", (topic_name,))
        result = cur.fetchone()

        if not result:
            cur.execute(
                "INSERT INTO topics (topic_name, created_by, status) VALUES (%s, %s, %s)",
                (topic_name, created_by, "pending"),
            )
            conn.commit()
            print(f"[DB] 🟢 Inserted new topic into Admin DB: '{topic_name}' (pending approval)")
        else:
            print(f"[DB] ⚙️ Topic already exists in Admin DB: '{topic_name}'")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"[DB] ❌ Error inserting topic '{topic_name}': {e}")


# -------------------------------------------------
# THREAD FUNCTIONS
# -------------------------------------------------
def weather_fetcher(q: Queue, interval: int):
    """Fetch weather data periodically and queue it."""
    topic_name = "weather"
    ensure_topic_in_db(topic_name)

    while True:
        try:
            res = requests.get(WEATHER_API_URL, timeout=5)
            res.raise_for_status()
            data = res.json()

            temp = data["current_weather"]["temperature"]
            wind = data["current_weather"]["windspeed"]

            msg = {
                "topic": topic_name,
                "source": "open-meteo",
                "temperature": temp,
                "wind_speed": wind,
                "timestamp": time.time(),
            }

            q.put(msg)
            print(f"[InputListener|Weather] queued: {msg}")

        except Exception as e:
            print(f"[InputListener|Weather] fetch error: {e}")

        time.sleep(interval + random.uniform(2, 5))


def stock_fetcher(q: Queue, interval: int):
    """Fetch stock data periodically and queue it."""
    topic_name = "stocks"
    ensure_topic_in_db(topic_name)

    while True:
        try:
            res = requests.get(STOCK_API_URL, timeout=5)
            res.raise_for_status()
            sdata = res.json()

            result = sdata.get("Global Quote", {})
            price = result.get("05. price")

            msg = {
                "topic": topic_name,
                "source": "alphavantage",
                "symbol": "IBM",
                "price": price,
                "timestamp": time.time(),
            }

            q.put(msg)
            print(f"[InputListener|Stocks] queued: {msg}")

        except Exception as e:
            print(f"[InputListener|Stocks] fetch error: {e}")

        time.sleep(interval + random.uniform(3, 6))


def crypto_fetcher(q: Queue, interval: int):
    """Fetch crypto data periodically and queue it."""
    topic_name = "crypto"
    ensure_topic_in_db(topic_name)

    while True:
        try:
            res = requests.get(CRYPTO_API_URL, timeout=5)
            res.raise_for_status()
            cdata = res.json()

            btc_price = cdata.get("bitcoin", {}).get("usd")
            eth_price = cdata.get("ethereum", {}).get("usd")

            msg = {
                "topic": topic_name,
                "source": "coingecko",
                "bitcoin_usd": btc_price,
                "ethereum_usd": eth_price,
                "timestamp": time.time(),
            }

            q.put(msg)
            print(f"[InputListener|Crypto] queued: {msg}")

        except Exception as e:
            print(f"[InputListener|Crypto] fetch error: {e}")

        time.sleep(interval + random.uniform(2, 5))


# -------------------------------------------------
# MAIN FUNCTION
# -------------------------------------------------
def start_input_listener(shared_queue: Queue):
    """Start all fetchers in parallel threads."""
    Thread(target=weather_fetcher, args=(shared_queue, INTERVAL), daemon=True).start()
    Thread(target=stock_fetcher, args=(shared_queue, INTERVAL), daemon=True).start()
    Thread(target=crypto_fetcher, args=(shared_queue, INTERVAL), daemon=True).start()

    print("🌍 InputListener started: Weather, Stocks, and Crypto data streams active.")


# Run standalone for testing
if __name__ == "__main__":
    q = Queue()
    start_input_listener(q)

    while True:
        msg = q.get()
        print("[Main] Got message:", msg)
        time.sleep(1)

