import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def connect_db():
    # Use the connection URL from your environment variables
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)