# Navigate to project folder
Set-Location -Path "$PSScriptRoot\leaf-diseases-detect-main"

# Path to python in virtual environment
$python = ".\.venv\Scripts\python.exe"

Write-Host "Starting FastAPI Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\leaf-diseases-detect-main'; & '$python' -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "Starting Streamlit Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\leaf-diseases-detect-main'; & '$python' -m streamlit run main.py --server.port 8501"
