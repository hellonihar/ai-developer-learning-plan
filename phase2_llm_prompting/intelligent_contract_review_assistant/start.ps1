# Start the Intelligent Contract Review Assistant
Write-Host "Starting Contract Review Assistant..." -ForegroundColor Cyan

# Start backend
$backend = Start-Process -FilePath "C:\Python\python.exe" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory "$PSScriptRoot\backend" -NoNewWindow -PassThru
Write-Host "[Backend]   http://localhost:8000/api/health" -ForegroundColor Green

# Start frontend
$frontend = Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "$PSScriptRoot\frontend" -NoNewWindow -PassThru
Write-Host "[Frontend]  http://localhost:5173" -ForegroundColor Green

Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow

try {
    Wait-Process -Id $backend.Id, $frontend.Id
} finally {
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
}
