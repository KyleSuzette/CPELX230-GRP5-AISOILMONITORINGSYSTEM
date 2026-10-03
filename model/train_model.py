"""
Train the Random Forest model used by the soil monitoring demo.
"""

from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "dataset" / "soil_data.csv"
MODEL_PATH = ROOT / "model" / "soil_model.joblib"
METRICS_PATH = ROOT / "model" / "metrics.json"

FEATURES = ["soil_moisture", "temperature", "humidity"]
TARGET = "label"


def train():
    df = pd.read_csv(DATASET_PATH)

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "classification_report": classification_report(
            y_test, predictions, output_dict=True
        ),
        "confusion_matrix": confusion_matrix(
            y_test, predictions, labels=list(model.classes_)
        ).tolist(),
        "classes": list(model.classes_),
        "features": FEATURES,
        "feature_importances": {
            feature: round(float(importance), 4)
            for feature, importance in zip(FEATURES, model.feature_importances_)
        },
        "train_rows": len(X_train),
        "test_rows": len(X_test),
    }

    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print("Feature importances:", metrics["feature_importances"])


if __name__ == "__main__":
    train()
