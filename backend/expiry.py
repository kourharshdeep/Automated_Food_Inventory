import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import os

# Base rule-based shelf life defaults (in days)
SHELF_LIFE_RULES = {
    "milk": 5,
    "bread": 7,
    "eggs": 21,
    "apple": 14,
    "banana": 5,
    "carrot": 14,
    "broccoli": 5,
    "orange": 21,
    "pizza": 3,
    "sandwich": 2,
    "cake": 4,
    "donut": 2,
    "hot dog": 3
}

DATASET_PATH = "synthetic_feedback.csv"

def generate_synthetic_data():
    if not os.path.exists(DATASET_PATH):
        data = {
            "food_type": ["apple", "banana", "pizza", "apple", "carrot", "broccoli", "sandwich", "donut"],
            "storage_condition": [1, 0, 1, 1, 1, 1, 1, 0], # 1 = fridge, 0 = pantry
            "days_since_added": [10, 4, 2, 15, 12, 4, 1, 1],
            "user_feedback_score": [-1, 0, 1, -2, 0, -1, 0, 1], # -1 = expired early, 0 = normal, 1 = still fresh
            "adjusted_expiry_days": [13, 5, 4, 12, 14, 4, 2, 3] # target variable
        }
        df = pd.DataFrame(data)
        df.to_csv(DATASET_PATH, index=False)

generate_synthetic_data()

# Initialize ML Model
rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
label_encoder = LabelEncoder()

# Fit initial label encoder on known classes
known_classes = list(SHELF_LIFE_RULES.keys())
label_encoder.fit(known_classes)

def train_model():
    """Train the model on accumulated feedback data."""
    if os.path.exists(DATASET_PATH):
        df = pd.read_csv(DATASET_PATH)
        
        # Handle unseen labels by adding them to classes
        unseen = set(df['food_type']) - set(label_encoder.classes_)
        if unseen:
            label_encoder.classes_ = np.append(label_encoder.classes_, list(unseen))
            
        df['food_type_encoded'] = label_encoder.transform(df['food_type'])
        
        X = df[['food_type_encoded', 'storage_condition', 'days_since_added', 'user_feedback_score']]
        y = df['adjusted_expiry_days']
        
        rf_model.fit(X, y)
        print("Model retrained successfully.")

train_model()

def predict_expiry(food_type: str, storage_condition: int = 1, days_since_added: int = 0, feedback_score: int = 0) -> int:
    """
    Hybrid expiry prediction.
    Returns predicted remaining days.
    """
    food_type_lower = food_type.lower()
    base_days = SHELF_LIFE_RULES.get(food_type_lower, 5) # default to 5 if unknown
    
    try:
        # ML prediction
        if food_type_lower in label_encoder.classes_:
            encoded_food = label_encoder.transform([food_type_lower])[0]
            X_new = pd.DataFrame([[encoded_food, storage_condition, days_since_added, feedback_score]], 
                                 columns=['food_type_encoded', 'storage_condition', 'days_since_added', 'user_feedback_score'])
            ml_prediction = rf_model.predict(X_new)[0]
            
            # Weighted average: 60% rule-based, 40% ML output
            final_prediction = 0.6 * base_days + 0.4 * ml_prediction
            return max(1, int(round(final_prediction)))
    except Exception as e:
        print(f"ML prediction failed: {e}")
        
    return base_days
