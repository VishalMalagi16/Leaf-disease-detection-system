from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded
for env_path in [
    Path.cwd() / ".env",
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parent.parent / ".env",
]:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        if os.getenv("GROQ_API_KEY"):
            break
load_dotenv()

from utils import convert_image_to_base64_and_test

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Leaf Disease Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/disease-detection-file')
async def disease_detection_file(file: UploadFile = File(...)):
    """
    Endpoint to detect diseases in leaf images using direct image file upload.
    Accepts multipart/form-data with an image file.
    """
    try:
        logger.info(f"Received image file: {file.filename} for disease detection")
        
        # Read uploaded file into memory
        contents = await file.read()
        
        # Process file directly from memory
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded image is empty")

        result = convert_image_to_base64_and_test(contents)
        logger.info("Disease detection completed successfully")
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except ValueError as e:
        if "GROQ_API_KEY" in str(e):
            logger.exception("Disease detection is not configured")
            raise HTTPException(
                status_code=503,
                detail="Disease detection is not configured. Set GROQ_API_KEY in the API server environment or .env file."
            ) from e
        logger.exception("Disease analysis returned invalid data")
        raise HTTPException(
            status_code=502,
            detail=f"Could not analyze image: {str(e)}"
        ) from e
    except Exception as e:
        logger.exception(f"Disease analysis failed: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Disease analysis failed: {str(e)}"
        ) from e


@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "Leaf Disease Detection API",
        "version": "1.0.0",
        "endpoints": {
            "disease_detection_file": "/disease-detection-file (POST, file upload)"
        }
    }
