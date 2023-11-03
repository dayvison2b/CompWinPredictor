import sqlite3
from sqlite3 import Error
import json
import os

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
        return

def drop_existing_database(database_name):
    database_name = database_name.split('/')[-1]
    try:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, database_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Database '{file_path}' exists and has been deleted.")
    except Exception as e:
        print(e)
        return e

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
    
def insert_match_data(connection, match_date, match_duration, match_rank, winner_champions, loser_champions):
    with open('utils/champions.json') as json_file:
        champions_data = json.load(json_file)
    cursor = connection.cursor()
    cursor.execute('''
                   INSERT INTO matches (match_date, match_duration, match_rank)
                   VALUES(?,?,?)
                   ''', (match_date, match_duration, match_rank))
    connection.commit()
    
    match_id = None
    champion_id = None
    match_id = cursor.lastrowid  # Obtém o ID da partida inserida
    
    # Inserir campeões do time vencedor
    for champion_name in winner_champions:
        # Insere a relação entre a partida e o campeão
        for champ_id, champ_name in champions_data.items():
            if champ_name == champion_name.replace("'",'').replace(" ",''):
                champion_id = champ_id
                break
        cursor.execute('''
        INSERT INTO match_champions (match_id, champion_id, team)
        VALUES (?, ?, ?)
        ''', (match_id, champion_id, 'WIN'))
        connection.commit()

    # Inserir campeões do time perdedor
    for champion_name in loser_champions:
        # Insere a relação entre a partida e o campeão
        for champ_id, champ_name in champions_data.items():
            if champ_name == champion_name:
                champion_id = champ_id
                break
        cursor.execute('''
        INSERT INTO match_champions (match_id, champion_id, team)
        VALUES (?, ?, ?)
        ''', (match_id, champion_id, 'LOSE'))
        connection.commit()
    
def main():
    database_name = 'database/CompWinPredictor.db'
    try:
        drop_existing_database(database_name)
    except Exception as e:
        print(e)
        return e
    
    connection = create_connection(database_name)
    cursor = connection.cursor()
    
    # Tabela de Partidas (matches)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY,
        match_date VARCHAR,
        match_duration VARCHAR,
        match_rank VARCHAR
    )
    ''')

    # Tabela de Campeões (champions)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS champions (
        champion_id INTEGER PRIMARY KEY,
        champion_name TEXT
    )
    ''')

    # Tabela de Escolha de Campeões (match_champions)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_champions (
        match_id INTEGER,
        champion_id INTEGER,
        team VARCHAR,
        FOREIGN KEY (match_id) REFERENCES matches (match_id),
        FOREIGN KEY (champion_id) REFERENCES champions (champion_id)
    )
    ''')

    connection.commit()
    connection.close()
    
if __name__ == '__main__':
    main()