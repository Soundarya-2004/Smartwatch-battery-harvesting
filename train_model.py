import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load and prepare data
df = pd.read_csv("kinetic_data.csv")
X = df[["KE_value"]].values
y = df["label"].values

# Split data with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42,
    stratify=y  # Ensure balanced split
)

# Create and train model with more trees
clf = RandomForestClassifier(
    n_estimators=100,  # Increased from 10
    max_depth=5,       # Prevent overfitting
    random_state=42    # Reproducibility
)
clf.fit(X_train, y_train)

# Evaluate model
y_pred = clf.predict(X_test)
print("\nModel Performance:")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(clf, "ke_model.pkl")
print("\n✅ Model saved to ke_model.pkl")