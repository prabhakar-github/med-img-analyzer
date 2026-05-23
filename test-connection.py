
##### Install mysql package, using below command, if required.  

#  pip install mysql-connector-python


import mysql.connector
from mysql.connector import Error

def connect_to_database():
    connection = None
    try:
        # Initializing connection with your specified credentials
        connection = mysql.connector.connect(
            host="sql12.freesqldatabase.com",
            port=3306,
            user="sql12827989",
            password="mQVMS5b1lL",
            database="sql12827989"
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✔️ Successfully connected to MySQL Server version: {db_info}")
            
            # Create a cursor object to execute queries
            cursor = connection.cursor(dictionary=True) # returns rows as clean Python dicts
            
            # Sample Query: Let's fetch the registered medical clients
            cursor.execute("SELECT id, name, type FROM clients LIMIT 3;")
            rows = cursor.fetchall()
            
            print("\n--- Registered Clients ---")
            if not rows:
                print("No clients found in the database yet.")
            for row in rows:
                print(f"ID: {row['id']} | Facility: {row['name']} [{row['type']}]")

    except Error as e:
        print(f"❌ Error while connecting to MySQL over port 3307: {e}")
        
    finally:
        # Ensure the database connections are always closed safely
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔒 MySQL connection pool cleanly closed.")

if __name__ == "__main__":
    connect_to_database()

