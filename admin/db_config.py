import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="adminuser",
        password="adminpass",
        database="streaming"
    )
    return conn

