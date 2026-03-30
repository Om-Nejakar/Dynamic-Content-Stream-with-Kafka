# db_config.py
import mysql.connector

def get_db_connection():
    """
    Connects to the Admin's MySQL database over the network.
    Update the host, user, password, and database fields
    with the values provided by the Admin.
    """
    try:
        connection = mysql.connector.connect(
            host="192.168.196.63",        # 🔹 Admin’s ZeroTier IP address
            user="adminuser",      # 🔹 MySQL username provided by Admin
            password="adminpass",  # 🔹 MySQL password
            database="streaming"   # 🔹 Admin’s database name
        )
        return connection
    except mysql.connector.Error as err:
        print(f"[DB_CONFIG] Database connection failed: {err}")
        raise

