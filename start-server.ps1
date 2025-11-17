# Script para arrancar el servidor desde la raíz del repo (PowerShell)
# Establece PYTHONPATH para que Python encuentre el paquete `app` que está dentro de `backend/`

$backendPath = Join-Path $PSScriptRoot 'backend'
Write-Host "Usando backend en: $backendPath"
$env:PYTHONPATH = $backendPath

# Lanza uvicorn usando el paquete `app`
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
