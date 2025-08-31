# Lorenz Formula
# RSI-MA Crossover
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt

def RSI_MA_Crossover(data_: pd.DataFrame) -> str:
    # Get indicators 
    rsi_prev, rsi_curr = data_["RSI"].tail(2)
    close = data_["close"].tail(1)
    ma40 = data_["MA40"].tail(1)
    ma80 = data_["MA80"].tail(1)
    # Buy
    if(rsi_prev < 30 and 
    rsi_curr >= 30 and 
    close > ma40 and
    close > ma80):
        return "Buy"
    # Sell
    elif(rsi_prev > 70 and rsi_curr <= 70 and
            (close < ma40 or close < ma80)):
        return "Sell"
    # Hold
    else: 
        return "Hold"
    
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

