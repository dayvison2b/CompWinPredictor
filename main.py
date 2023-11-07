import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from sklearn.metrics import accuracy_score, classification_report

# Preparing the data
def load_data():
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
    # Initialize encoders dictionary if not provided
    if encoders is None:
        encoders = {}

    # Encode 'match_rank' feature
    if 'match_rank' not in encoders:
        encoder = LabelEncoder()
        encoder.fit(data['match_rank'])
        encoders['match_rank'] = encoder
        data['match_rank'] = encoder.transform(data['match_rank'])

    # Save the encoders for future use
    joblib.dump(encoders, 'label_encoders.pkl')

    return data

def split_data(data):
    # Dividir os dados em conjuntos de treinamento e teste
    X = data[['match_rank', 'champion_id']]
    y = data['team']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

# Passo 2: Modelagem
def train_knn(X_train, y_train, k=5):
    # Treinar o modelo KNN
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    return knn

# Passo 3: Avaliação do Modelo
def evaluate_model(knn, X_test, y_test):
    # Fazer previsões
    y_pred = knn.predict(X_test)
    
    # Calcular a acurácia do modelo
    accuracy = accuracy_score(y_test, y_pred)
    print("Acurácia do modelo:", accuracy)
    
    # Exibir relatório de classificação
    print("Relatório de Classificação:")
    print(classification_report(y_test, y_pred))

# Passo 4: Previsões
def make_predictions(knn, X_new):
    # Fazer previsões para novas partidas
    predictions = knn.predict(X_new)
    return predictions

def main():
    data = load_data()
    data = preprocess_data(data)
    X_train, X_test, y_train, y_test = split_data(data)
    
    # Escolha o valor de k (número de vizinhos) - ajuste conforme necessário
    k = 5
    knn = train_knn(X_train, y_train, k)
    
    evaluate_model(knn, X_test, y_test)
    
    # Passo 5: Previsões
    # Substitua os valores abaixo pelos atributos das partidas futuras
    new_matches = pd.DataFrame({
        'match_rank': [0],  # Exemplo de valores para a patente da partida
        'champion_id': [64]  # Exemplo de IDs dos campeões
    })
    
    new_predictions = make_predictions(knn, new_matches)
    print("Previsões para as novas partidas:", new_predictions)

if __name__ == "__main__":
    main()