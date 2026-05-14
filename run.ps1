# ============================================================
# WinHub Web Launcher
# Run this via: iex (irm https://raw.githubusercontent.com/ricinuss/winhub/main/run.ps1)
# ============================================================

$ErrorActionPreference = "Stop"

# 1. Ensure Administrator Privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Requesting Administrator privileges..." -ForegroundColor Yellow
    # If launched via iex, $PSCommandPath is empty, so we must relaunch the web command
    $cmd = "-NoProfile -ExecutionPolicy Bypass -Command `"iex (irm https://raw.githubusercontent.com/ricinuss/winhub/main/run.ps1)`""
    Start-Process powershell.exe -ArgumentList $cmd -Verb RunAs
    exit
}

Write-Host "Preparing WinHub Environment..." -ForegroundColor Cyan

# 2. Check for Python
$pythonInstalled = $false
try {
    $null = Get-Command "python" -ErrorAction Stop
    $pythonInstalled = $true
} catch {
    Write-Host ""
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "WinHub requires Python 3.11+ to run." -ForegroundColor Yellow
    Write-Host "Please download it from: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

# 3. Download and Extract
$WinHubDir = "$env:TEMP\WinHubTemp"

if (Test-Path $WinHubDir) {
    Remove-Item -Path $WinHubDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $WinHubDir -Force | Out-Null

$ZipPath = "$WinHubDir\winhub.zip"
$RepoUrl = "https://github.com/ricinuss/winhub/archive/refs/heads/main.zip"

Write-Host "Downloading WinHub repository..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri $RepoUrl -OutFile $ZipPath
} catch {
    Write-Host "Failed to download WinHub from GitHub. Are you connected to the internet?" -ForegroundColor Red
    exit
}

Write-Host "Extracting files..." -ForegroundColor Cyan
Expand-Archive -Path $ZipPath -DestinationPath $WinHubDir -Force
Remove-Item $ZipPath

# The zip usually extracts to a folder with "-main" appended to the repo name
$SourceDir = "$WinHubDir\winhub-main"

if (-not (Test-Path $SourceDir)) {
    # Fallback just in case the folder name inside zip is different
    $dirs = Get-ChildItem -Path $WinHubDir -Directory
    if ($dirs.Count -eq 1) {
        $SourceDir = $dirs[0].FullName
    }
}

Set-Location $SourceDir

# 4. Launch WinHub
Write-Host "Launching WinHub..." -ForegroundColor Green
Start-Process "cmd.exe" -ArgumentList "/c winhub.bat" -Wait

# 5. Cleanup
Set-Location $env:TEMP
Write-Host "Cleaning up temporary files..." -ForegroundColor DarkGray
Remove-Item -Path $WinHubDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Done!" -ForegroundColor Green
