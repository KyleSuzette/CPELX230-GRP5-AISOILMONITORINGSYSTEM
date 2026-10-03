from pathlib import Path
from datetime import datetime, timezone
import math

from flask import Flask, jsonify, render_template, request
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "model" / "soil_model.joblib"

FEATURES = ["soil_moisture", "temperature", "humidity"]

app = Flask(__name__, template_folder=str(ROOT / "app" / "templates"), static_folder=str(ROOT / "app" / "static"))
model = joblib.load(MODEL_PATH)

latest_reading = {
    "soil_moisture": None,
    "temperature": None,
    "humidity": None,
    "prediction": None,
    "confidence": None,
    "timestamp": None,
}


def validate_readings(data):
    if not isinstance(data, dict):
        return None, "Expected a JSON object."
    missing = [field for field in FEATURES if field not in data]
    if missing:
        return None, f"Missing field(s): {', '.join(missing)}"

    try:
        soil_moisture = float(data["soil_moisture"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
    except (TypeError, ValueError):
        return None, "All sensor readings must be numeric."

    if not all(math.isfinite(v) for v in (soil_moisture, temperature, humidity)):
        return None, "Sensor readings must be finite."

    if not 0 <= soil_moisture <= 100:
        return None, "soil_moisture must be between 0 and 100."
    if not -10 <= temperature <= 60:
        return None, "temperature must be between -10 and 60 °C."
    if not 0 <= humidity <= 100:
        return None, "humidity must be between 0 and 100."

    return {
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity,
    }, None


def make_prediction(readings):
    X = pd.DataFrame([[readings[f] for f in FEATURES]], columns=FEATURES)
    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]
    probability_map = {
        class_name: round(float(prob), 4)
        for class_name, prob in zip(model.classes_, probabilities)
    }

    confidence = probability_map[str(prediction)]
    return str(prediction), confidence, probability_map


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model": "Scaled RBF SVM",
            "features": FEATURES,
        }
    )


@app.post("/api/sensor")
def sensor():
    """Endpoint intended for ESP32 sensor uploads."""
    global latest_reading

    data = request.get_json(silent=True) or {}
    readings, error = validate_readings(data)
    if error:
        return jsonify({"error": error}), 400

    prediction, confidence, probabilities = make_prediction(readings)

    latest_reading = {
        **readings,
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": probabilities,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return jsonify(latest_reading)


@app.get("/api/latest")
def latest():
    return jsonify(latest_reading)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
