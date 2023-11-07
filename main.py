import joblib
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

K_NEIGHBORS = 5  # Valor de k (número de vizinhos)

def load_data():
    """
    Load data from the SQLite database and return it as a Pandas DataFrame.
    """
    connection = sqlite3.connect('database/CompWinPredictor.db')
    
    query = """
    SELECT matches.match_rank, CASE WHEN match_champions.team = 'WIN' THEN 1 ELSE 0 END AS team, champions.champion_id
    FROM matches
    JOIN match_champions ON matches.match_id = match_champions.match_id
    JOIN champions ON match_champions.champion_id = champions.champion_id
    """
    data = pd.read_sql_query(query, connection)
    connection.close()
    return data

def preprocess_data(data, encoders=None):
    """
    Preprocess the data by encoding 'match_rank' and save the encoders for future use.
    """
    if encoders is None:
        encoders = {}
    
    if 'match_rank' not in encoders:
        encoder = LabelEncoder()
        encoder.fit(data['match_rank'])
        encoders['match_rank'] = encoder
        data['match_rank'] = encoder.transform(data['match_rank'])
        joblib.dump(encoders, 'label_encoders.pkl')

    return data

def split_data(data):
    """
    Split the data into training and testing sets.
    """
    X = data[['match_rank', 'champion_id']]
    y = data['team']
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
    
    new_matches = pd.DataFrame({
        'match_rank': [0],  # Example values for match rank
        'champion_id': [64]  # Example champion IDs
    })
    
    new_predictions = make_predictions(knn, new_matches)
    print("Predictions for new matches:", new_predictions)

if __name__ == "__main__":
    main()