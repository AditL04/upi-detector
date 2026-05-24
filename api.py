from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from cnn_backbone.backbone import UPIDetector

app = FastAPI()

# IMPORTANT: allow React frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = UPIDetector()


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    temp_path = "temp.png"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    prediction, score = detector.predict(temp_path)

    os.remove(temp_path)

    return {
        "prediction": prediction,
        "cnn_score": float(score)
    }