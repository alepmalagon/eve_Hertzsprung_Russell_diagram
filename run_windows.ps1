# EVE Online H-R Diagram Generator - Windows PowerShell Runner
# This script provides an easy way to run the H-R diagram generator on Windows

param(
    [switch]$NoCache,
    [string]$CacheFile = "data\stellar_data.json",
    [string]$OutputDir = "output",
    [int]$SampleSize = 0,
    [switch]$Help
)

# Display help information
if ($Help) {
    Write-Host "EVE Online Hertzsprung-Russell Diagram Generator" -ForegroundColor Cyan
    Write-Host "=================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\run_windows.ps1 [OPTIONS]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Green
    Write-Host "  -NoCache        Force fresh data fetch (ignore cache)"
    Write-Host "  -CacheFile      Path to cache file (default: data\stellar_data.json)"
    Write-Host "  -OutputDir      Output directory (default: output)"
    Write-Host "  -SampleSize     Limit to N stars for testing"
    Write-Host "  -Help           Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\run_windows.ps1                    # Run with default settings"
    Write-Host "  .\run_windows.ps1 -NoCache           # Force fresh data fetch"
    Write-Host "  .\run_windows.ps1 -SampleSize 1000   # Test with 1000 stars"
    Write-Host "  .\run_windows.ps1 -OutputDir results # Custom output directory"
    exit 0
}

# Check if Python is available
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python not found. Please install Python 3.8+ and add it to PATH." -ForegroundColor Red
        Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if requirements are installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
if (!(Test-Path "requirements.txt")) {
    Write-Host "❌ requirements.txt not found. Make sure you're in the project directory." -ForegroundColor Red
    exit 1
}

# Try to import required packages
$packagesOk = $true
$requiredPackages = @("requests", "pandas", "matplotlib", "tqdm", "aiohttp", "asyncio_throttle")

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $packagesOk = $false
            break
        }
    } catch {
        $packagesOk = $false
        break
    }
}

if (!$packagesOk) {
    Write-Host "⚠️  Some dependencies are missing. Installing..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "✅ All dependencies are available." -ForegroundColor Green
}

# Build the command arguments
$args = @()
if ($NoCache) { $args += "--no-cache" }
if ($CacheFile -ne "data\stellar_data.json") { $args += "--cache-file", $CacheFile }
if ($OutputDir -ne "output") { $args += "--output-dir", $OutputDir }
if ($SampleSize -gt 0) { $args += "--sample-size", $SampleSize }

# Run the main script
Write-Host ""
Write-Host "🚀 Starting EVE Online H-R Diagram Generator..." -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

try {
    if ($args.Count -gt 0) {
        python main.py @args
    } else {
        python main.py
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Generation completed successfully!" -ForegroundColor Green
        Write-Host "📁 Check the '$OutputDir' directory for your H-R diagram and analysis files." -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "❌ Generation failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "❌ An error occurred: $_" -ForegroundColor Red
    exit 1
}
