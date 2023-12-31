import random
import sqlite3
import pandas as pd
import openpyxl
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report

K_NEIGHBORS = 5  # Valor de k (número de vizinhos)
random.seed(42)

def load_data():
    """
    Load data from the SQLite database and return it as a Pandas DataFrame.
    """
    connection = sqlite3.connect('database/CompWinPredictor.db')
    
    query = """
    SELECT matches.match_id,CASE WHEN matches.match_rank = 'Challenger' THEN 1 ELSE 0 end AS match_rank, CASE WHEN match_champions.team = 'WIN' THEN 1 ELSE 0 END AS team, champions.champion_id
    FROM matches
    JOIN match_champions ON matches.match_id = match_champions.match_id
    JOIN champions ON match_champions.champion_id = champions.champion_id
    """
    data = pd.read_sql_query(query, connection)
    connection.close()
    return data

def preprocess_data(data):
    """
    Preprocess the data by creating columns for team compositions and filling them with champion IDs.
    """
    unique_match_ids = data['match_id'].unique()
    
    processed_data = []
    
    for match_id in unique_match_ids:
        match_data = data[data['match_id'] == match_id]
        
        # team champions
        team_1_champions = match_data['champion_id'][:5].values
        team_2_champions = match_data['champion_id'][5:].values
        
        order = random.randint(1,2)
        
        match_row = {'match_id': match_id, 'match_rank': match_data['match_rank'].values[0], 'result': 1 if order == 1 else 2}
        
        # Fill team composition columns
        if order == 1:
            for i in range(5):
                match_row[f'team_1_champion_{i+1}'] = team_1_champions[i] if i < len(team_1_champions) else None
            for i in range(5):
                match_row[f'team_2_champion_{i+1}'] = team_2_champions[i] if i < len(team_2_champions) else None
        else:
            for i in range(5):
                match_row[f'team_2_champion_{i+1}'] = team_1_champions[i] if i < len(team_1_champions) else None
            for i in range(5):
                match_row[f'team_1_champion_{i+1}'] = team_2_champions[i] if i < len(team_2_champions) else None
        
        processed_data.append(match_row)
    
    processed_data = pd.DataFrame(processed_data)
    
    return processed_data


def split_data(data):
    """
    Split the data into training and testing sets.
    """
    X = data.drop(['result','match_id'], axis=1)
    y = data['result']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def train_knn(X_train, y_train, k=K_NEIGHBORS):
    """
    Train a KNN model with the given number of neighbors.
    """
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    return knn

def evaluate_model(knn, X_test, y_test):
    """
    Evaluate the KNN model and print accuracy and classification report.
    """
    y_pred = knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Model Accuracy:", accuracy)
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

def make_predictions(knn, X_new):
    """
    Make predictions for new matches using the trained KNN model.
    """
    predictions = knn.predict(X_new)
    return predictions

def main():
    data = load_data()
    data = preprocess_data(data)
    X_train, X_test, y_train, y_test = split_data(data)
    
    knn = train_knn(X_train, y_train, k=K_NEIGHBORS)
    evaluate_model(knn, X_test, y_test)
    
    new_teams = pd.DataFrame({
    'match_rank' : [1],
    'team_1_champion_1': [84],
    'team_1_champion_2': [104],
    'team_1_champion_3': [147],
    'team_1_champion_4': [67],
    'team_1_champion_5': [267],
    'team_2_champion_1': [24],
    'team_2_champion_2': [163],
    'team_2_champion_3': [16],
    'team_2_champion_4': [202],
    'team_2_champion_5': [526],
    })
    
    new_predictions = make_predictions(knn, new_teams)
    print("Predictions for new matches:", new_predictions)

if __name__ == "__main__":
    main()