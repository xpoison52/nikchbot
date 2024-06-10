BOT_TOKEN = '7198899560:AAHBI0gC3Pj_Z6g12uwALM9tf2Zd7r_6TAo'
PAYMENTS_TOKEN = '1744374395:TEST:2fdbe490c3bc8f784334'
import mysql.connector

def get_database_connection():
    config = {
        'user': 'xpoison',
        'password': 'password',
        'host': 'localhost',
        'database': 'vpnBot',
        'raise_on_warnings': True
    }

    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("Connection to MySQL database was successful")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None