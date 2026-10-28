from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse, HTMLResponse
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

# Middleware to strip any Vercel subpath prefix
@app.middleware("http")
async def fix_path_middleware(request: Request, call_next):
    path = request.scope.get("path", "")
    for prefix in ["/api/index.py", "/api/index", "/api"]:
        if path == prefix:
            request.scope["path"] = "/"
            break
        elif path.startswith(prefix + "/"):
            request.scope["path"] = path[len(prefix):]
            break
    return await call_next(request)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leaf Disease Detection</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
        body { background: linear-gradient(135deg, #e3f2fd 0%, #f7f9fa 100%); min-height: 100vh; padding: 2.5rem 1rem; color: #333; }
        .container { max-width: 950px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 2rem; }
        .header .icon { font-size: 3rem; }
        .header h1 { color: #1565c0; font-size: 2.3rem; font-weight: 700; margin-top: 0.3rem; }
        .header p { color: #616161; font-size: 1.15rem; margin-top: 0.5rem; }
        .grid { display: grid; grid-template-columns: 1fr 1.4fr; gap: 2rem; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        .card { background: rgba(255, 255, 255, 0.98); border-radius: 18px; padding: 2rem; box-shadow: 0 4px 24px rgba(44, 62, 80, 0.10); }
        .upload-area { border: 2px dashed #90caf9; border-radius: 14px; padding: 2rem 1rem; text-align: center; cursor: pointer; background: #fafafa; transition: all 0.25s; }
        .upload-area:hover { border-color: #1976d2; background: #f0f7ff; }
        .upload-area input { display: none; }
        .upload-icon { font-size: 2.2rem; color: #1976d2; margin-bottom: 0.5rem; }
        .preview-container { margin-top: 1.2rem; text-align: center; display: none; }
        .preview-img { max-width: 100%; max-height: 280px; border-radius: 12px; box-shadow: 0 3px 12px rgba(0,0,0,0.12); object-fit: contain; }
        .btn { width: 100%; padding: 0.95rem; font-size: 1.1rem; font-weight: 600; color: white; background: #1976d2; border: none; border-radius: 10px; cursor: pointer; transition: background 0.2s; margin-top: 1.2rem; }
        .btn:hover { background: #1565c0; }
        .btn:disabled { background: #b0bec5; cursor: not-allowed; }
        .spinner { display: none; text-align: center; margin-top: 1.2rem; color: #1976d2; font-weight: 600; font-size: 1.05rem; }
        .result-card { display: none; margin-top: 1.5rem; }
        .disease-title { font-size: 2rem; font-weight: 700; color: #1b5e20; margin-bottom: 0.8rem; }
        .disease-title.invalid { color: #d32f2f; }
        .disease-title.healthy { color: #2e7d32; }
        .badges { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.2rem; }
        .badge { background: #e3f2fd; color: #1976d2; padding: 0.35rem 0.85rem; border-radius: 8px; font-size: 0.95rem; font-weight: 600; }
        .section-title { color: #1976d2; font-size: 1.2rem; font-weight: 600; margin-top: 1.2rem; margin-bottom: 0.4rem; }
        ul { padding-left: 1.4rem; margin-bottom: 0.8rem; color: #424242; line-height: 1.6; }
        .timestamp { color: #757575; font-size: 0.85rem; text-align: right; margin-top: 1.5rem; }
        .alert { background: #ffebee; color: #c62828; padding: 1rem; border-radius: 10px; margin-top: 1rem; display: none; border-left: 4px solid #d32f2f; }
        .api-link { text-align: center; margin-top: 2rem; font-size: 0.95rem; color: #757575; }
        .api-link a { color: #1976d2; text-decoration: none; font-weight: 600; }
        .api-link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">🌿</div>
            <h1>Leaf Disease Detection</h1>
            <p>Upload a leaf image to detect diseases and get expert recommendations.</p>
        </div>

        <div class="grid">
            <div class="card">
                <div class="upload-area" id="dropArea" onclick="document.getElementById('fileInput').click()">
                    <div class="upload-icon">📷</div>
                    <div style="font-weight: 600; color: #333; margin-bottom: 0.3rem;">Upload Leaf Image</div>
                    <div style="font-size: 0.9rem; color: #757575;">Click or drag and drop image here (JPG, PNG)</div>
                    <input type="file" id="fileInput" accept="image/*">
                </div>
                <div class="preview-container" id="previewContainer">
                    <img id="previewImg" class="preview-img" alt="Leaf Preview">
                </div>
                <button class="btn" id="detectBtn" disabled onclick="analyzeImage()">🔍 Detect Disease</button>
                <div class="spinner" id="spinner">⏳ Analyzing image with AI Vision...</div>
                <div class="alert" id="errorAlert"></div>
            </div>

            <div class="card" id="rightCard">
                <div id="placeholderText" style="text-align: center; color: #9e9e9e; padding: 3rem 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🍃</div>
                    <p style="font-size: 1.1rem;">Select a plant leaf image and click "Detect Disease" to view analysis.</p>
                </div>

                <div class="result-card" id="resultCard">
                    <div class="disease-title" id="diseaseTitle"></div>
                    <div class="badges" id="badgesContainer"></div>

                    <div id="symptomsSection">
                        <div class="section-title" id="symptomsTitle">Symptoms</div>
                        <ul id="symptomsList"></ul>
                    </div>

                    <div id="causesSection">
                        <div class="section-title">Possible Causes</div>
                        <ul id="causesList"></ul>
                    </div>

                    <div id="treatmentSection">
                        <div class="section-title" id="treatmentTitle">Treatment</div>
                        <ul id="treatmentList"></ul>
                    </div>

                    <div class="timestamp" id="timestamp"></div>
                </div>
            </div>
        </div>

        <div class="api-link">
            REST API Documentation: <a href="/docs" target="_blank">Swagger Docs</a> | <a href="/redoc" target="_blank">ReDoc</a>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const dropArea = document.getElementById('dropArea');
        const previewContainer = document.getElementById('previewContainer');
        const previewImg = document.getElementById('previewImg');
        const detectBtn = document.getElementById('detectBtn');
        const spinner = document.getElementById('spinner');
        const errorAlert = document.getElementById('errorAlert');
        const rightCard = document.getElementById('rightCard');
        const placeholderText = document.getElementById('placeholderText');
        const resultCard = document.getElementById('resultCard');

        let selectedFile = null;

        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFile(e.target.files[0]);
            }
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropArea.style.borderColor = '#1565c0';
                dropArea.style.background = '#e3f2fd';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropArea.style.borderColor = '#90caf9';
                dropArea.style.background = '#fafafa';
            }, false);
        });

        dropArea.addEventListener('drop', (e) => {
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        function handleFile(file) {
            selectedFile = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                previewContainer.style.display = 'block';
                detectBtn.disabled = false;
                errorAlert.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }

        async function analyzeImage() {
            if (!selectedFile) return;

            detectBtn.disabled = true;
            spinner.style.display = 'block';
            errorAlert.style.display = 'none';

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/disease-detection-file', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || `Server error ${response.status}`);
                }

                renderResult(data);
            } catch (err) {
                errorAlert.textContent = err.message || 'Analysis failed. Please try again.';
                errorAlert.style.display = 'block';
            } finally {
                detectBtn.disabled = false;
                spinner.style.display = 'none';
            }
        }

        function renderResult(res) {
            placeholderText.style.display = 'none';
            resultCard.style.display = 'block';

            const titleEl = document.getElementById('diseaseTitle');
            const badgesEl = document.getElementById('badgesContainer');
            const symptomsList = document.getElementById('symptomsList');
            const causesList = document.getElementById('causesList');
            const treatmentList = document.getElementById('treatmentList');
            const symptomsSection = document.getElementById('symptomsSection');
            const causesSection = document.getElementById('causesSection');
            const treatmentSection = document.getElementById('treatmentSection');
            const symptomsTitle = document.getElementById('symptomsTitle');
            const treatmentTitle = document.getElementById('treatmentTitle');
            const timestampEl = document.getElementById('timestamp');

            badgesEl.innerHTML = '';
            symptomsList.innerHTML = '';
            causesList.innerHTML = '';
            treatmentList.innerHTML = '';

            titleEl.className = 'disease-title';

            if (res.disease_type === 'invalid_image') {
                titleEl.textContent = '⚠️ Invalid Image';
                titleEl.classList.add('invalid');
                symptomsTitle.textContent = 'Issue';
                treatmentTitle.textContent = 'What to do';
                causesSection.style.display = 'none';
            } else if (res.disease_detected) {
                titleEl.textContent = `🦠 ${res.disease_name || 'Disease Detected'}`;
                badgesEl.innerHTML = `
                    <span class="badge">Type: ${res.disease_type || 'N/A'}</span>
                    <span class="badge">Severity: ${res.severity || 'N/A'}</span>
                    <span class="badge">Confidence: ${res.confidence || 0}%</span>
                `;
                symptomsTitle.textContent = 'Symptoms';
                treatmentTitle.textContent = 'Treatment Recommendations';
                causesSection.style.display = 'block';
            } else {
                titleEl.textContent = '✅ Healthy Leaf';
                titleEl.classList.add('healthy');
                badgesEl.innerHTML = `
                    <span class="badge">Status: Healthy</span>
                    <span class="badge">Confidence: ${res.confidence || 0}%</span>
                `;
                symptomsSection.style.display = 'none';
                causesSection.style.display = 'none';
                treatmentSection.style.display = 'none';
            }

            if (res.symptoms && res.symptoms.length > 0) {
                symptomsSection.style.display = 'block';
                res.symptoms.forEach(s => {
                    const li = document.createElement('li');
                    li.textContent = s;
                    symptomsList.appendChild(li);
                });
            }

            if (res.possible_causes && res.possible_causes.length > 0) {
                causesSection.style.display = 'block';
                res.possible_causes.forEach(c => {
                    const li = document.createElement('li');
                    li.textContent = c;
                    causesList.appendChild(li);
                });
            }

            if (res.treatment && res.treatment.length > 0) {
                treatmentSection.style.display = 'block';
                res.treatment.forEach(t => {
                    const li = document.createElement('li');
                    li.textContent = t;
                    treatmentList.appendChild(li);
                });
            }

            if (res.analysis_timestamp) {
                timestampEl.textContent = `🕒 Analyzed at: ${res.analysis_timestamp}`;
            }
        }
    </script>
</body>
</html>
"""

async def process_disease_detection(file: UploadFile):
    try:
        logger.info(f"Received image file: {file.filename} for disease detection")
        contents = await file.read()
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
                detail="Disease detection is not configured. Set GROQ_API_KEY in environment variables."
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

@app.post('/disease-detection-file')
@app.post('/api/disease-detection-file')
async def disease_detection_file(file: UploadFile = File(...)):
    """Endpoint to detect diseases in leaf images using direct image file upload."""
    return await process_disease_detection(file)

@app.get("/", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint serving the interactive web UI, or JSON if requested."""
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return JSONResponse(content={
            "message": "Leaf Disease Detection API",
            "version": "1.0.0",
            "endpoints": {
                "disease_detection_file": "/disease-detection-file (POST, file upload)",
                "docs": "/docs"
            }
        })
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api/info")
async def api_info():
    """Information endpoint returning JSON API status."""
    return {
        "message": "Leaf Disease Detection API",
        "version": "1.0.0",
        "endpoints": {
            "disease_detection_file": "/disease-detection-file (POST, file upload)",
            "docs": "/docs"
        }
    }
