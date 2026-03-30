import threading
import time
import json
import sys
from kafka import KafkaConsumer, TopicPartition
import mysql.connector

# =======================
# Database Configuration
# =======================
DB_CONFIG = {
    "host": "192.168.196.63",
    "user": "adminuser",
    "password": "adminpass",
    "database": "streaming"
}

KAFKA_BROKER = "192.168.196.62:9092"
stop_flag = threading.Event()
consumer_threads = []


# =======================
# Database Connection
# =======================
def get_db_connection():
    try:
        print("[DB] 🟢 Attempting to connect to database (5s timeout, SSL disabled)...")
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            connection_timeout=5,
            ssl_disabled=True
        )
        print("[DB] ✅ Database connection successful.")
        return conn
    except mysql.connector.Error as e:
        print(f"[DB] ❌ Database connection failed: {e}")
        return None


# =======================
# Database Operations
# =======================
def get_active_topics():
    conn = get_db_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT topic_name FROM topics WHERE status='active'")
    topics = [row[0] for row in cur.fetchall()]
    conn.close()
    return topics


def get_user_subscriptions(username):
    conn = get_db_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT t.topic_name
        FROM user_subscriptions u
        JOIN topics t ON u.topic_id = t.id
        WHERE u.user_name=%s
    """, (username,))
    subs = [row[0] for row in cur.fetchall()]
    conn.close()
    return subs


def subscribe_user(username, topic):
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT id FROM topics WHERE topic_name=%s", (topic,))
    topic_row = cur.fetchone()
    if not topic_row:
        print("[DB] ❌ Invalid topic.")
        conn.close()
        return
    topic_id = topic_row[0]
    cur.execute("""
        INSERT INTO user_subscriptions (user_name, topic_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE subscribed_at=NOW()
    """, (username, topic_id))
    conn.commit()
    conn.close()
    print(f"[DB] ✅ Subscribed to {topic}")


def unsubscribe_user(username, topic):
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM user_subscriptions 
        WHERE user_name=%s AND topic_id=(SELECT id FROM topics WHERE topic_name=%s)
    """, (username, topic))
    conn.commit()
    conn.close()
    print(f"[DB] ❌ Unsubscribed from {topic}")


# =======================
# Kafka Consumer Logic
# =======================
def consume_topic(topic, username):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            group_id=f"group_{username}{topic}{int(time.time())}",
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            
        )
        print(f"[Kafka] 🚀 Started consumer for topic: {topic}", flush=True)

        first_message_received = False  # <-- NEW FLAG

        while not stop_flag.is_set():
            msg_pack = consumer.poll(timeout_ms=1000)

            # No messages returned
            if not msg_pack:
                if not first_message_received:   # <-- ONLY print before first message
                    print(f"[Kafka] ⏳ Polling... no messages yet for topic {topic}", flush=True)
                time.sleep(1)
                continue

            # If messages exist → stop showing polling messages
            for tp, messages in msg_pack.items():
                for message in messages:
                    first_message_received = True  # <-- STOP future polling prints
                    print(f"[{topic}] {message.value}", flush=True)
                    consumer.commit()

            time.sleep(1)

    except Exception as e:
        print(f"[Kafka] ❌ Error in topic {topic}: {e}")
    finally:
        consumer.close()
        print(f"[Kafka] 🛑 Stopped consuming topic: {topic}", flush=True)




def start_consumer(username):
    stop_flag.clear()
    subs = get_user_subscriptions(username)
    if not subs:
        print("[System] ⚠ No active subscriptions found.")
        return

    print(f"[System] 📨 Starting consumers for: {subs}")
    for topic in subs:
        t = threading.Thread(target=consume_topic, args=(topic, username), daemon=True)
        consumer_threads.append(t)
        t.start()

    print("\n[System] 🟢 Consumers running... Press Ctrl+C or choose option 6 to stop.\n")

    try:
        while not stop_flag.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[System] 🛑 KeyboardInterrupt detected — stopping consumers...")
        stop_consumers()


def stop_consumers():
    stop_flag.set()
    print("[System] 🛑 Stopping all consumers...")
    for t in consumer_threads:
        t.join(timeout=3)
    consumer_threads.clear()
    print("[System] ✅ All consumers stopped.")


# =======================
# CLI Menu
# =======================
def menu(username):
    while True:
        print("\n====== Kafka Consumer Menu ======")
        print("1. Show all active topics")
        print("2. Subscribe to a topic")
        print("3. Unsubscribe from a topic")
        print("4. Show my subscriptions")
        print("5. Start consuming data")
        print("6. Stop consuming data")
        print("7. Exit")
        choice = input("\nSelect an option: ")

        if choice == "1":
            topics = get_active_topics()
            print("🟢 Active topics:" if topics else "⚠ No active topics found.", topics)

        elif choice == "2":
            topic = input("Enter topic name to subscribe: ").strip()
            subscribe_user(username, topic)

        elif choice == "3":
            topic = input("Enter topic name to unsubscribe: ").strip()
            unsubscribe_user(username, topic)

        elif choice == "4":
            subs = get_user_subscriptions(username)
            print(f"📜 Subscribed topics: {subs}" if subs else "⚠ No subscriptions found.")

        elif choice == "5":
            if any(t.is_alive() for t in consumer_threads):
                print("[Kafka] ⚠ Consumers already running.")
                continue
            start_consumer(username)

        elif choice == "6":
            stop_consumers()

        elif choice == "7":
            stop_consumers()
            print("👋 Exiting...")
            sys.exit(0)

        else:
            print("❌ Invalid option. Try again.")


# =======================
# Main Entry
# =======================
if _name_ == "_main_":
    print("=== Dynamic Kafka Consumer Node ===")
    username = input("Enter your username: ").strip()
    menu(username)