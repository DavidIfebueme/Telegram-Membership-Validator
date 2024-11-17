import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_db():
    db_url = os.getenv("DATABASE_URL") 
    try:
        # Connect to the database
        connection = psycopg2.connect(db_url)
        cursor = connection.cursor()
        
        # Define the table creation query
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(50),
            paid BOOLEAN DEFAULT FALSE
        );
        """

        create_payments_list_query = """
        CREATE TABLE payments_list (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT UNIQUE NOT NULL,
         account_details TEXT NOT NULL
        );
        """
        
        # Execute the query
        cursor.execute(create_table_query)
        cursor.execute(create_payments_list_query)
        connection.commit()  # Save changes
        print("Database initialized successfully!")
    
    except Exception as e:
        print("Error initializing the database:", e)
    
    finally:
        # Close the connection
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    initialize_db()
