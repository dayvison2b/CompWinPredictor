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
    
def main():
    try:
        connection = create_connection('CompWinPredictor.db')
        cursor = connection.cursor()
        
        table_name = 'matches'
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = cursor.fetchone()
        
        if result:
            cursor.execute(f"DROP TABLE {table_name}")
    except Exception as e:
        print(e)
        return e
    
    cursor.execute(f"""
        CREATE TABLE "{table_name}" (
            id INTEGER PRIMARY KEY,
            champion_names TEXT,
            result VARCHAR,
            match_date DATE,
            match_rank VARCHAR,
            match_duration TIME
        )
    """)

    connection.commit()
    connection.close()
    
if __name__ == '__main__':
    main()