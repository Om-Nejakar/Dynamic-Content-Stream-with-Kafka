# topic_watcher.py
import time
from kafka.admin import KafkaAdminClient, NewTopic
from db_config import get_db_connection

BROKER_IP = "192.168.196.62:9092"

def watch_topics(poll_interval=10):
    admin = KafkaAdminClient(bootstrap_servers=[BROKER_IP], client_id='topic_watcher')

    while True:
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # 🟢 Fetch topics approved but not yet active
            cur.execute("SELECT id, topic_name FROM topics WHERE status='approved'")
            rows = cur.fetchall()

            for topic_id, topic_name in rows:
                try:
                    admin.create_topics([NewTopic(name=topic_name, num_partitions=1, replication_factor=1)])
                    print(f"[TopicWatcher] ✅ Created topic: {topic_name}")
                    cur.execute("UPDATE topics SET status='active' WHERE id=%s", (topic_id,))
                    conn.commit()
                except Exception as e:
                    if "TopicExistsError" in str(e) or "already exists" in str(e):
                        print(f"[TopicWatcher] ⚙️ Topic already exists: {topic_name}")
                        cur.execute("UPDATE topics SET status='active' WHERE id=%s", (topic_id,))
                        conn.commit()
                    else:
                        print(f"[TopicWatcher] ❌ Error creating topic {topic_name}: {e}")

            cur.close()
            conn.close()

        except Exception as e:
            print(f"[TopicWatcher] ❗ DB/Kafka error: {e}")

        time.sleep(poll_interval)

