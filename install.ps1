# Windows 1-Line Terminal Installer for cli-agent
$ErrorActionPreference = "Stop"

$Repo = "Ayushsingh-02082004/ai-terminal-assistant"
$BinaryName = "cli-agent-windows-amd64.exe"
$InstallDir = Join-Path $HOME ".cli-agent\bin"
$ExePath = Join-Path $InstallDir "cli-agent.exe"

Write-Host "=== Installing CLI Agent (cli-agent) ===" -ForegroundColor Cyan

# Create installation directory if it does not exist
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}

# Fetch latest release URL from GitHub Releases
$LatestReleaseUrl = "https://github.com/$Repo/releases/latest/download/$BinaryName"

Write-Host "Downloading cli-agent executable from GitHub Releases..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $LatestReleaseUrl -OutFile $ExePath
} catch {
    Write-Host "Failed to download $BinaryName from GitHub Releases." -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Successfully installed cli-agent to $ExePath" -ForegroundColor Green

# Add to User PATH if not already present
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$InstallDir*") {
    Write-Host "Adding $InstallDir to User PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$InstallDir", "User")
    $env:PATH = "$env:PATH;$InstallDir"
}

Write-Host "`n=== Installation Complete! ===" -ForegroundColor Cyan
Write-Host "Open any new terminal window and type: cli-agent" -ForegroundColor Green
