# Setup script for StateSmith with Authentication
# Run this after installing dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  StateSmith Authentication Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "Error: Please run this script from the StateSmith directory" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing dependencies. Please check your Python environment." -ForegroundColor Red
    exit 1
}

Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Check if database exists
if (Test-Path "statesmith.db") {
    Write-Host "Database already exists: statesmith.db" -ForegroundColor Yellow
    $response = Read-Host "Do you want to delete it and start fresh? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-Item "statesmith.db"
        Write-Host "Database deleted." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application, run:" -ForegroundColor Yellow
Write-Host "  python app.py" -ForegroundColor White
Write-Host ""
Write-Host "Then open your browser to:" -ForegroundColor Yellow
Write-Host "  http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "The database will be created automatically on first run." -ForegroundColor Cyan
Write-Host ""
