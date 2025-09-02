# Lorenz Formula
# RSI-MA Crossover
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import joblib

    
def train_and_test_KNN(data_: pd.DataFrame, neighbors_: int) -> None:
    clean_data_ = data_.dropna() # Remove NaN
    clean_data_ = clean_data_[clean_data_['Higher/Lower'] != 0] # Remove no change 0 classifier 

    features = ['close', 'high', 'low', 'open', 'volume', 'ATR', 'RSI', 'MA40', 'MA80', 'MA160'] # Define what features to look at 
    # Separate data into X,y/train,test
    X = clean_data_[features]
    y = clean_data_['Higher/Lower']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .2, random_state=42)
    
    # Create KNN model
    knn = KNeighborsClassifier(n_neighbors=neighbors_)
    knn.fit(X_train, y_train)

    # Use KNN model to predict output
    y_pred = knn.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))
    


def train_and_test_RF(data_: pd.DataFrame) -> None:
    clean_data_ = data_.dropna() # Remove NaN
    clean_data_ = clean_data_[clean_data_['Higher/Lower'] != 0] # Remove no change 0 classifier 

    features = ['close', 'high', 'low', 'open', 'volume', 'ATR', 'RSI', 'MA40', 'MA80', 'MA160'] # Define what features to look at 
    # Separate data into X,y/train,test
    X = clean_data_[features]
    y = clean_data_['Higher/Lower']

    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    importances = rf_model.feature_importances_
    feature_importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': importances
    }).sort_values(by='Importance', ascending=False)

    # Plot
    plt.figure(figsize=(8,5))
    plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'])
    plt.xlabel("Importance")
    plt.title("Feature Importance in Random Forest")
    plt.gca().invert_yaxis()
    plt.show()

# Create new file just for training
def train_and_save_knn_model(data_: pd.DataFrame, neighbors_: int = 5, model_filename: str = "knn_model.pkl") -> None:
    """
    Train a KNN model and save it to disk.
    
    Args:
        data_: DataFrame containing the training data
        neighbors_: Number of neighbors for KNN (default: 5)
        model_filename: Filename to save the model (default: "knn_model.pkl")
    """
    # Clean the data
    clean_data_ = data_.dropna()  # Remove NaN
    clean_data_ = clean_data_[clean_data_['Higher/Lower'] != 0]  # Remove no change 0 classifier 

    # Define features
    features = ['close', 'high', 'low', 'open', 'volume', 'ATR', 'RSI', 'MA40', 'MA80', 'MA160']
    
    # Separate data into X, y
    X = clean_data_[features]
    y = clean_data_['Higher/Lower']
    
    # Split data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train KNN model
    knn = KNeighborsClassifier(n_neighbors=neighbors_)
    knn.fit(X_train, y_train)
    
    # Test the model
    y_pred = knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"KNN Model trained with {neighbors_} neighbors")
    print(f"Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    joblib.dump(knn, model_filename)
    print(f"Model saved as: {model_filename}")


def load_knn_model(model_filename: str = "knn_model.pkl") -> KNeighborsClassifier:
    """
    Load a saved KNN model from disk.
    
    Args:
        model_filename: Filename of the saved model (default: "knn_model.pkl")
        
    Returns:
        Loaded KNeighborsClassifier model
    """
    try:
        model = joblib.load(model_filename)
        print(f"Model loaded successfully from: {model_filename}")
        return model
    except FileNotFoundError:
        print(f"Error: Model file '{model_filename}' not found.")
        return None
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def predict_latest_candlestick(model, data_frame: pd.DataFrame) -> int:
    """
    Predict the expected output for the latest candlestick.
    
    Args:
        model: Trained KNN model
        data_frame: DataFrame with technical indicators
        
    Returns:
        Prediction (-1 for lower, 1 for higher)
    """
    # Define the features used in training
    features = ['close', 'high', 'low', 'open', 'volume', 'ATR', 'RSI', 'MA40', 'MA80', 'MA160']
    
    # Get the latest candlestick data (last row)
    latest_data = data_frame[features].iloc[-1:].values  # Keep as 2D array for prediction
    
    # Make prediction
    prediction = model.predict(latest_data)[0]  # Get the single prediction value
    
    return prediction
