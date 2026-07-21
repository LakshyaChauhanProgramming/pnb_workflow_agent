# =============================================================================
# One-command setup for Windows (PowerShell).
# Clone karne ke baad project root se chalao:   .\setup.ps1
#
# HAR STEP PEHLE CHECK karta hai — jo pehle se hai use SKIP, sirf jo missing hai
# wahi karta hai. Isliye dobara chalana safe + fast hai (idempotent).
# (Policy error aaye to:  Set-ExecutionPolicy -Scope Process Bypass)
# =============================================================================
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Py = "venv\Scripts\python.exe"
$ModelCfg = "app\rag\models\paraphrase-multilingual-MiniLM-L12-v2\config.json"
$ChromaDb = "chroma_db\chroma.sqlite3"

# --- [0/5] python maujood hai? ---
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: 'python' nahi mila. Pehle Python 3.12+ install karo."
    exit 1
}

Write-Host "==> [1/5] Virtual environment (venv\)"
if (Test-Path $Py) {
    Write-Host "    venv pehle se hai - skip."
} else {
    python -m venv venv
    Write-Host "    venv banaya."
}

Write-Host "==> [2/5] Dependencies"
# Check: zaroori packages import ho jaate hain? Ho to pip bilkul mat chalao.
& $Py -c "import chromadb, sentence_transformers, fastapi, uvicorn" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "    Dependencies pehle se installed - skip."
} else {
    Write-Host "    Kuch missing hai - installing..."
    & $Py -m pip install --upgrade pip | Out-Null
    & $Py -m pip install -r requirements.txt
}

Write-Host "==> [3/5] .env file"
if (Test-Path ".env") {
    Write-Host "    .env pehle se hai - skip."
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "    .env banaya (.env.example se). ISME apni OPENROUTER_API_KEY daalna!"
}

Write-Host "==> [4/5] Embedding model (~470MB)"
if (Test-Path $ModelCfg) {
    Write-Host "    Model pehle se maujood - skip."
} else {
    Write-Host "    Model missing - downloading (open internet chahiye)..."
    & $Py download_model.py
}

Write-Host "==> [5/5] RAG index (ChromaDB)"
if (Test-Path $ChromaDb) {
    Write-Host "    Index pehle se bana hai - skip. (Rebuild: Remove-Item -Recurse chroma_db; $Py -m app.rag.ingest)"
} else {
    & $Py -m app.rag.ingest
}

Write-Host ""
Write-Host "Setup complete. Test: $Py -m app.rag.retriever"
