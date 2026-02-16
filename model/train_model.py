import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

def train_model():
    print("="*70)
    print("TRAINING MEDICAL REPORT ANALYZER MODEL")
    print("="*70)
    print("\nLoading dataset...")
    
    # Use relative path (works on Windows and Linux)
    dataset_path = os.path.join('..', 'data', 'medical_dataset.csv')
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join('data', 'medical_dataset.csv')
    
    df = pd.read_csv(dataset_path)
    print(f"✓ Dataset loaded: {len(df)} samples")
    
    X = df[['hemoglobin', 'blood_sugar', 'cholesterol']]
    y = df['risk_level']
    
    print(f"\nClass distribution:")
    print(y.value_counts())
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100, 
        random_state=42, 
        max_depth=10,
        class_weight='balanced'  # This handles imbalance!
    )
    model.fit(X_train, y_train)
    
    # Test the model
    y_pred = model.predict(X_test)
    
    print("\n" + "="*70)
    print("MODEL PERFORMANCE")
    print("="*70)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nDetailed Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    model_path = 'risk_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\n✓ Model saved to: {model_path}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': ['hemoglobin', 'blood_sugar', 'cholesterol'],
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    print("\n" + "="*70)
    print("✓ MODEL TRAINING COMPLETE!")
    print("="*70)
    
    return model

if __name__ == '__main__':
    train_model()
