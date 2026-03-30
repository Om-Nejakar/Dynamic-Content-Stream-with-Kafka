# producer_main.py
import threading
import queue
from topic_watcher import watch_topics
from publisher import start_publishing
from input_listener import start_input_listener  # ✅ Correct import


def main():
    data_queue = queue.Queue(maxsize=1000)

    # 🟢 Start the real API input listener (no interval argument needed now)
    listener_thread = threading.Thread(
        target=start_input_listener, args=(data_queue,), daemon=True
    )

    # 🟢 Watch for approved topics only
    watcher_thread = threading.Thread(target=watch_topics, args=(10,), daemon=True)

    # 🟢 Start publisher (publishes only approved/active topics)
    publisher_thread = threading.Thread(
        target=start_publishing, args=(data_queue, 1), daemon=True
    )

    listener_thread.start()
    watcher_thread.start()
    publisher_thread.start()

    print("🚀 Producer started. Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("🛑 Shutting down producer...")


if __name__ == "__main__":
    main()

