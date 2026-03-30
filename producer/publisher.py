import time
import json
from kafka import KafkaProducer
from db_config import get_db_connection

BROKER_IP = "192.168.196.62:9092"  # ⚠️ Update with your Kafka broker IP

def start_publishing(data_queue, publish_interval=1):
    producer = KafkaProducer(
        bootstrap_servers=[BROKER_IP],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retries=3
    )

    print("[Publisher] 🚀 Started publishing thread...")

    while True:
        try:
            if data_queue.empty():
                print("[Publisher] ⏳ Waiting for data...")
                time.sleep(publish_interval)
                continue

            # Get one message from queue
            data = data_queue.get()
            topic = data.get("topic")

            if not topic:
                print("[Publisher] ⚠️ No topic in message, skipping:", data)
                continue

            # Check if topic is active
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT topic_name FROM topics WHERE status='active' AND topic_name=%s", (topic,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                try:
                    producer.send(topic, value=data)
                    producer.flush()
                    print(f"[Publisher] ✅ Sent to {topic}: {data}")
                except Exception as e:
                    print(f"[Publisher] ❌ Send error to {topic}: {e}")
            else:
                print(f"[Publisher] ⛔ Topic '{topic}' not active yet, skipping message.")

        except Exception as e:
            print(f"[Publisher] ❗ Error: {e}")

        time.sleep(publish_interval)

