@echo off
echo ==============================================
echo  Starting Leaf Disease Detection System...
echo ==============================================

cd /d "%~dp0leaf-diseases-detect-main" 2>nul || cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Starting FastAPI Backend on http://localhost:8000 ...
start "Leaf Disease Backend (FastAPI)" cmd /k "title FastAPI Backend && uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo Starting Streamlit Web App on http://localhost:8501 ...
start "Leaf Disease Frontend (Streamlit)" cmd /k "title Streamlit Frontend && streamlit run main.py --server.port 8501"

echo ==============================================
echo  System is running!
echo  - Frontend: http://localhost:8501
echo  - Backend Docs: http://localhost:8000/docs
echo ==============================================
