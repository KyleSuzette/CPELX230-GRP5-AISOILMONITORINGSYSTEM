"""
Generate a synthetic demo dataset for the AI-Based Soil Monitoring System.

IMPORTANT:
This dataset is intended for software prototyping and classroom demonstration.
For a research-grade project, replace it with real measurements collected from
actual plants, soil, sensors, weather conditions, and expert/observed labels.
"""

from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_SAMPLES = 6000

OUTPUT = Path(__file__).resolve().parent / "soil_data.csv"


def generate_dataset(n_samples=N_SAMPLES, seed=SEED):
    rng = np.random.default_rng(seed)

    # Sensor-like ranges for a general prototype.
    soil_moisture = rng.uniform(5, 95, n_samples)
    temperature = np.clip(rng.normal(29.0, 5.0, n_samples), 15, 42)
    humidity = np.clip(rng.normal(65.0, 18.0, n_samples), 20, 98)

    # Convert readings into a continuous "watering demand" score.
    # The score intentionally depends on ALL THREE inputs and interactions.
    dryness = (100.0 - soil_moisture) / 100.0
    heat = np.clip((temperature - 18.0) / 24.0, 0, 1)
    air_dryness = (100.0 - humidity) / 100.0

    # Interaction terms make the relationship non-linear.
    score = (
        0.56 * dryness
        + 0.20 * heat
        + 0.14 * air_dryness
        + 0.18 * dryness * heat
        + 0.08 * dryness * air_dryness
    )

    # Small noise prevents perfectly clean, unrealistic boundaries.
    score += rng.normal(0, 0.035, n_samples)

    labels = np.where(
        score >= 0.69,
        "WATER_NOW",
        np.where(score >= 0.48, "WATER_SOON", "NO_WATER"),
    )

    df = pd.DataFrame(
        {
            "soil_moisture": np.round(soil_moisture, 2),
            "temperature": np.round(temperature, 2),
            "humidity": np.round(humidity, 2),
            "label": labels,
        }
    )

    # Shuffle rows so labels are not grouped.
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv(OUTPUT, index=False)

    print(f"Saved {len(df):,} rows to: {OUTPUT}")
    print("\nClass distribution:")
    print(df["label"].value_counts())
