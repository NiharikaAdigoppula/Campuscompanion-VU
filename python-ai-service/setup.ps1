# Setup script for Python AI Service (Windows PowerShell)

Write-Host "🚀 Setting up CampusCompanion Python AI Service..." -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.([8-9]|1[0-9])\.") {
    Write-Host "✅ Python version OK: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python 3.8 or higher required. Current: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "⚙️  Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists" -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created from example" -ForegroundColor Green
    Write-Host "📝 Please edit .env and add your API keys!" -ForegroundColor Yellow
}

# Create logs directory
Write-Host ""
Write-Host "📁 Creating logs directory..." -ForegroundColor Yellow
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✅ Logs directory created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Logs directory already exists" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file and add your AI API keys (OpenAI, Gemini, or Anthropic)"
Write-Host "2. Ensure MongoDB is running (mongodb://localhost:27017)"
Write-Host "3. Run: python main.py"
Write-Host ""
Write-Host "🔗 The service will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API docs will be at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
