import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
        return

def create_table(connection, query):
    """Create a table from the create_table_sql statement."""
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        return "Table created"
    except Error as e:
        print(e)
        return
    
def insert_data(connection, query, data):
    """Insert data into the table using the insert_sql statement."""
    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        return "Data inserted"
    except Error as e:
        print(e)
        return