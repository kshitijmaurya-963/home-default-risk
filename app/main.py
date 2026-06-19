from fastapi import FastAPI
import joblib
import pandas as pd
import random
from app.schemas import PredictionRequest
from pathlib import Path


app = FastAPI(
    title="Loan Default Risk API",
    description="Hybrid LightGBM Loan Default Predictor",
    version="1.0"
)


# -----------------------------
# Load artifacts
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "hybrid_pipeline.pkl"

FEATURES_PATH = BASE_DIR / "models" / "hybrid_features.pkl"

DEMO_PATH = BASE_DIR / "data" / "demo_cases.csv"


model = joblib.load(MODEL_PATH)

features = joblib.load(FEATURES_PATH)

demo_df = pd.read_csv(DEMO_PATH)


print("Model Loaded")

print("Features:", len(features))

print("Demo Cases:", demo_df.shape)


# -----------------------------
# Health Endpoint
# -----------------------------

@app.get("/")
def health_check():

    return {

        "status": "healthy",

        "model": "Hybrid LightGBM",

        "auc": 0.7471

    }


# -----------------------------
# Sample Endpoint
# -----------------------------

@app.get("/sample")

def get_sample():

    row = demo_df.sample(1).iloc[0]

    sample = {}

    for col in features:

        value = row[col]

        sample[col] = (

            None

            if pd.isna(value)

            else float(value)

        )

    case_id = int(row.name)

    actual_target = int(
        row["actual_target"]
    )


    actual_label = (

        "Default"

        if actual_target == 1

        else "Safe"

    )


    return {

        "case_id": case_id,

        "features": sample,

        "actual_target": actual_target,

        "actual_label": actual_label

    }

@app.get("/metrics")

def metrics():

    return {

        "model": "Hybrid LightGBM",

        "auc": 0.7471,

        "accuracy": 0.7497,

        "precision": 0.1817,

        "recall": 0.5996,

        "f1": 0.2789,

        "features": 25,

        "training_rows": 246008

    }

@app.post("/predict")

def predict(
    request: PredictionRequest
):

    input_data = pd.DataFrame(

        [request.model_dump()]

    )


    probability = model.predict_proba(

        input_data

    )[0][1]


    probability = float(probability)

    prediction = int(
        probability >= 0.5
    )


    risk_label = (

        "High Risk"

        if prediction == 1

        else "Low Risk"

    )


    # Risk Band

    if probability < 0.30:

        risk_band = "Low"

    elif probability < 0.60:

        risk_band = "Medium"

    else:

        risk_band = "High"


    risk_score = round(
        probability * 100,
        2
    )


    return {

        "risk_score": risk_score,

        "prediction": prediction,

        "risk_label": risk_label,

        "risk_band": risk_band

    }