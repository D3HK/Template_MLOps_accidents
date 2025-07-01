import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
import logging
import mlflow.pyfunc
from prometheus_client import make_asgi_app, Counter, Histogram
from fastapi.responses import RedirectResponse

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Accidents Prediction API",
    description="API for predicting accidents with MLflow and Prometheus",
    version="1.0.0"
)

# Prometheus метрики
metrics_app = make_asgi_app()
app.mount("/metrics/", metrics_app)
PREDICT_COUNTER = Counter("predict_requests_total", "Total /predict calls")
PREDICT_LATENCY = Histogram("predict_latency_seconds", "Prediction latency")
ERROR_COUNTER = Counter("predict_errors_total", "Total prediction errors")

# Конфигурация модели
MODEL_NAME = os.getenv("MODEL_NAME", "Accidents_Prediction")
MODEL_VERSION = os.getenv("MODEL_VERSION", "3")
# MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000") # Для Docker
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000") # Для локального теста

# Глобальная переменная для модели
model = None

class Features(BaseModel):
    features: List[float]

class PredictionResponse(BaseModel):
    model: str
    version: str
    prediction: float

@app.on_event("startup")
async def load_model():
    """Загрузка модели из MLflow при старте"""
    global model
    try:
        logger.info(f"Подключение к MLflow: {MLFLOW_TRACKING_URI}")
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_VERSION}")
        logger.info("✅ Модель успешно загружена")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки модели: {str(e)}")
        model = None

@app.get("/")
async def root():
    return {
        "message": "Accidents Prediction API",
        "status": "healthy" if model else "model not loaded"
    }

@app.get("/health")
async def health_check():
    if not model:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(data: Features):
    """Предсказание с метриками Prometheus"""
    if not model:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    
    with PREDICT_LATENCY.time():
        PREDICT_COUNTER.inc()
        try:
            features = np.array(data.features).reshape(1, -1)
            prediction = model.predict(features)
            return PredictionResponse(
                model=MODEL_NAME,
                version=MODEL_VERSION,
                prediction=float(prediction[0])
            )
        except Exception as e:
            ERROR_COUNTER.inc()
            logger.error(f"Ошибка предсказания: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/metrics")
async def redirect_metrics():
    return RedirectResponse(url="/metrics/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)