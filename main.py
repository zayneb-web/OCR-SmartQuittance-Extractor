from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import shutil
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION CLOUDINARY ===
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

from ocr_llm_extractor import preprocess_image, extract_all_fields, FIELD_BOXES

app = FastAPI()

@app.post("/extract_quittance/")
async def extract_quittance(file: UploadFile = File(...)):
    # Lire le contenu du fichier en mémoire
    contents = await file.read()
    # Uploader sur Cloudinary (en mémoire)
    result = cloudinary.uploader.upload(contents, resource_type="image")
    image_url = result['secure_url']
    # (Optionnel) Télécharger l'image depuis Cloudinary pour traitement local
    # processed_img = preprocess_image(image_url)  # Si preprocess_image accepte une URL
    # ... ou bien tu continues à traiter l'image en mémoire ...
    return {"cloudinary_url": image_url}