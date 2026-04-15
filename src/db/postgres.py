import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

connection = None

def get_connection():
    global connection
    if connection is None or connection.closed:
        try:
            connection = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    return connection

def test_connection():
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        return False
    except:
        return False

def execute_query(query, params=None):
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"Query execution error: {e}")
        return None