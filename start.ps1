# Start the Precision Agriculture WebGIS Application

Write-Host "🌾 Starting Precision Agriculture WebGIS Application..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✓ Activating virtual environment..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠ Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✓ Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "✓ Environment ready!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🚀 Starting FastAPI Server" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 Access points:" -ForegroundColor Yellow
Write-Host "   Web Interface: http://localhost:8000/static/index.html" -ForegroundColor White
Write-Host "   API Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Root:          http://localhost:8000/" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the FastAPI application
python main.py
