import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from backend/.env or root .env
env_backend = Path(__file__).resolve().parent / '.env'
env_root = Path(__file__).resolve().parent.parent / '.env'

if env_backend.exists():
    load_dotenv(dotenv_path=env_backend)
elif env_root.exists():
    load_dotenv(dotenv_path=env_root)
else:
    load_dotenv()

# Read Database connection settings from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'weather_analysis')
}

def get_db_connection():
    """Create and return a connection to MySQL database."""
    try:
        # First ensure target database exists on MySQL server
        init_conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        init_cursor = init_conn.cursor()
        init_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        init_cursor.close()
        init_conn.close()

        # Connect to the target database
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[Database Error] Could not connect to MySQL: {e}")
        return None

def init_db():
    """Initialize MySQL table: weather_records."""
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        # Create weather_records table as specified in project context
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_records (
            record_id INT AUTO_INCREMENT PRIMARY KEY,
            observation_date DATE NOT NULL,
            location VARCHAR(100) NOT NULL,
            temperature FLOAT,
            humidity FLOAT,
            rainfall FLOAT
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and table initialized successfully.")
        return True
    except Error as e:
        print(f"[Database Error] Failed to initialize table: {e}")
        return False

def insert_weather_records(records):
    """
    Insert a list of valid weather records into the MySQL database.
    Each record is a tuple: (observation_date, location, temperature, humidity, rainfall)
    Uses ON DUPLICATE KEY UPDATE to handle re-uploads gracefully.
    """
    conn = get_db_connection()
    if conn is None:
        raise Exception("Could not connect to database")

    cursor = conn.cursor()
    query = """
    INSERT INTO weather_records (observation_date, location, temperature, humidity, rainfall)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        temperature = VALUES(temperature),
        humidity = VALUES(humidity),
        rainfall = VALUES(rainfall)
    """
    cursor.executemany(query, records)
    conn.commit()
    cursor.close()
    conn.close()
    return len(records)
