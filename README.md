# 🌿 Leaf Disease Detection System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg?style=flat&logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776ab.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/Groq-Vision%20AI-orange.svg?style=flat)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](LICENSE)

An enterprise-grade, AI-powered plant leaf disease detection system featuring a dual-interface architecture: a **FastAPI backend REST service** and a modern, interactive **Streamlit web application**.

Powered by **Groq Vision AI** (`qwen/qwen3.8-27b`), the system provides instant disease classification, severity scoring, confidence assessments, observed symptom breakdown, and actionable agricultural treatment recommendations.

---

## 🎯 Key Features

- **🔍 Vision-AI Disease Detection**: Analyzes plant foliage images to identify hundreds of fungal, bacterial, viral, and pest-related diseases.
- **🛡️ Plant & Leaf Validation**: Automatically detects if an uploaded image is non-plant/invalid and prompts the user for a valid sample.
- **📊 Precision Severity Assessment**: Categorizes affliction severity into *Mild*, *Moderate*, or *Severe*.
- **🎯 Confidence Scoring**: Delivers calibrated AI confidence percentages (0–100%).
- **📋 Symptoms & Causes Breakdown**: Explains biological factors, pathogens, and observable visual markers.
- **💡 Actionable Treatment Protocols**: Provides chemical, biological, and cultural management practices to protect crops.
- **⚡ Dual Architecture**:
  - RESTful FastAPI backend for programmatic integrations and API consumers.
  - Sleek Streamlit UI with real-time image preview and responsive diagnosis cards.
- **🔄 Smart Offline Fallback**: The Streamlit interface automatically falls back to direct AI detection even if the FastAPI backend server is offline.

---

## 🏗️ Repository Structure

```
Leaf-disease-detection-system/
├── Leaf Disease/
│   ├── config.py             # Application configuration dataclass
│   └── main.py               # Core LeafDiseaseDetector engine & Groq client
├── Media/                    # Sample test images
│   ├── brown-spot-4 (1).jpg
│   └── ...
├── .streamlit/
│   └── config.toml           # Streamlit UI theme and styling configuration
├── app.py                    # FastAPI backend REST service
├── main.py                   # Streamlit interactive frontend application
├── utils.py                  # Image processing and base64 helper utilities
├── test_api.py               # Automated test script for API endpoints
├── run.bat                   # One-click Windows batch launcher
├── run.ps1                   # One-click PowerShell startup script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore configuration
├── vercel.json               # Cloud deployment configuration
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+** (Python 3.10+ recommended)
- **Groq API Key**: Obtain a free API key from [Groq Console](https://console.groq.com/).

---

### 1. Clone the Repository

```bash
git clone https://github.com/VishalMalagi16/Leaf-disease-detection-system.git
cd Leaf-disease-detection-system
```

---

### 2. Set Up Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root (you can copy `.env.example`):

```bash
cp .env.example .env
```

Add your Groq API key inside `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=qwen/qwen3.8-27b
MODEL_TEMPERATURE=0.3
MAX_COMPLETION_TOKENS=1024
LOG_LEVEL=INFO
LOG_FILE=disease_detection.log
```

---

## 💻 Running the Application

### Option A: One-Click Launcher (Windows)
Double-click `run.bat` or run:
```powershell
.\run.ps1
```
This automatically starts both the FastAPI backend (`http://localhost:8000`) and the Streamlit frontend (`http://localhost:8501`).

---

### Option B: Run Services Manually

#### 1. Start the FastAPI Backend:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative Docs (ReDoc): [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### 2. Start the Streamlit Web UI:
```bash
streamlit run main.py --server.port 8501
```
- Open browser at: [http://localhost:8501](http://localhost:8501)

*(Note: If you run only Streamlit, the app automatically runs direct local inference even if the FastAPI backend is not active.)*

---

## 📡 API Endpoints

### `GET /`
Returns API status and version information.

### `POST /disease-detection-file`
Upload an image (`multipart/form-data`) under the `file` field.

**Sample JSON Response:**
```json
{
  "disease_detected": true,
  "disease_name": "Rice Blast",
  "disease_type": "fungal",
  "severity": "moderate",
  "confidence": 92.0,
  "symptoms": [
    "Distinct spindle-shaped or diamond-shaped lesions",
    "Lesions with grey or tan centers with dark margins"
  ],
  "possible_causes": [
    "Infection by the fungus Magnaporthe oryzae",
    "High humidity and excessive nitrogen application"
  ],
  "treatment": [
    "Apply recommended fungicides (e.g., Tricyclazole, Azoxystrobin)",
    "Improve field drainage and reduce excessive nitrogen fertilizer",
    "Remove and dispose of infected plant debris"
  ],
  "analysis_timestamp": "2026-10-28T16:06:09.383956+05:30"
}
```

---

## 🧪 Testing

Run the automated test script to verify API functionality:
```bash
python test_api.py
```

---

## 👤 Author

**Vishal Malagi**
- GitHub: [@VishalMalagi16](https://github.com/VishalMalagi16)
- Repository: [Leaf-disease-detection-system](https://github.com/VishalMalagi16/Leaf-disease-detection-system)

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).
