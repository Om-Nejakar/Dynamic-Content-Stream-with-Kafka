# test_db_connection.py
import mysql.connector
from db_config import get_db_connection

def test_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        print("✅ Successfully connected to Admin DB!")

        # Step 1: List all tables in the database
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("\n📋 Tables available in Admin DB:")
        for t in tables:
            print("-", t[0])

        # Step 2: Try to fetch data from 'topics' table (if exists)
        if any("topics" in t for t in tables):
            cursor.execute("SELECT * FROM topics;")
            rows = cursor.fetchall()
            print("\n🟩 Data from 'topics' table:")
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No data found in 'topics' table.")

        # Step 3: Try to fetch data from 'user_subscriptions' (optional)
        if any("user_subscriptions" in t for t in tables):
            cursor.execute("SELECT * FROM user_subscriptions;")
            rows = cursor.fetchall()
            print("\n🟦 Data from 'user_subscriptions' table:")
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No data found in 'user_subscriptions' table.")

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    test_connection()

