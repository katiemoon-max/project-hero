<#
  PROTOTYPE (2026-08-11): stand up a docling-serve host on a spare WINDOWS
  machine, for Project Hero corpus conversion.

  Run this ON THE SPARE MACHINE, in an ELEVATED PowerShell (admin is needed
  only for the firewall rule; skip that step with -NoFirewall to run unelevated).

      powershell -ExecutionPolicy Bypass -File remote_setup_windows.ps1

  It prints, at the end, the two things the laptop needs: the server URL and
  the API key.

  WHY THE PINS: the laptop's corpus was converted with docling-slim 2.107.0 /
  docling-core 2.85.0. A different version on this machine converts the same
  PDF differently, which silently forks the corpus mid-course. Do not relax
  these without reconverting everything.

  Removing it all afterwards:
      Remove-Item -Recurse -Force C:\docling-serve
      Remove-NetFirewallRule -DisplayName "docling-serve (Project Hero)"
#>
param(
  [string]$InstallDir = "C:\docling-serve",
  [int]$Port = 5001,
  [switch]$NoFirewall
)

$ErrorActionPreference = "Stop"

Write-Host "=== Project Hero :: docling-serve setup ===" -ForegroundColor Cyan

# --- 1. Python check -------------------------------------------------------
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { throw "python not found on PATH. Install Python 3.12 or 3.13 first." }
$ver = (& python -c "import sys;print('%d.%d'%sys.version_info[:2])").Trim()
Write-Host "Python $ver at $($py.Source)"
if ($ver -eq "3.14") {
  Write-Host "  NOTE: on 3.14 grpcio has no prebuilt wheel and cannot compile on" -ForegroundColor Yellow
  Write-Host "  Windows. This script works around it by installing the newest" -ForegroundColor Yellow
  Write-Host "  grpcio that does ship a 3.14 wheel, then pinning to it." -ForegroundColor Yellow
}

# --- 2. venv ---------------------------------------------------------------
if (-not (Test-Path $InstallDir)) { New-Item -ItemType Directory -Path $InstallDir | Out-Null }
$venv = Join-Path $InstallDir "venv"
if (-not (Test-Path $venv)) {
  Write-Host "Creating venv at $venv ..."
  & python -m venv $venv
}
$pip = Join-Path $venv "Scripts\pip.exe"
$serve = Join-Path $venv "Scripts\docling-serve.exe"

# --- 3. install (pinned) ---------------------------------------------------
Write-Host "Installing grpcio from a wheel (never build it from source) ..."
& $pip install --quiet --only-binary=:all: grpcio
$grpcVer = (& $pip show grpcio | Select-String '^Version:').ToString().Split(' ')[1]
Write-Host "  grpcio $grpcVer"

$constraints = Join-Path $InstallDir "constraints.txt"
"grpcio==$grpcVer" | Out-File -FilePath $constraints -Encoding utf8

Write-Host "Installing docling-serve (pinned to match the laptop) ..."
& $pip install -c $constraints "docling-serve==1.24.0" "docling-slim==2.107.0" "docling-core==2.85.0"
if ($LASTEXITCODE -ne 0) { throw "pip install failed - see output above" }

# --- 4. API key ------------------------------------------------------------
$keyFile = Join-Path $InstallDir "api-key.txt"
if (Test-Path $keyFile) {
  $apiKey = (Get-Content $keyFile -Raw).Trim()
  Write-Host "Reusing existing API key from $keyFile"
} else {
  $bytes = New-Object byte[] 24
  [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
  $apiKey = [Convert]::ToBase64String($bytes) -replace '[+/=]', ''
  $apiKey | Out-File -FilePath $keyFile -Encoding utf8 -NoNewline
  Write-Host "Generated API key -> $keyFile"
}

# --- 5. firewall (LAN only) ------------------------------------------------
if (-not $NoFirewall) {
  $ruleName = "docling-serve (Project Hero)"
  $existing = $null
  try { $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction Stop } catch {}
  if ($existing) {
    Write-Host "Firewall rule already present."
  } else {
    Write-Host "Adding inbound rule on TCP $Port (Private profile, LocalSubnet only) ..."
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP `
      -LocalPort $Port -Action Allow -Profile Private -RemoteAddress LocalSubnet | Out-Null
  }
}

# --- 6. launcher -----------------------------------------------------------
# PYTHONUTF8: without it docling-serve dies on startup printing its banner --
# it contains an emoji the Windows cp1252 console cannot encode.
$runner = Join-Path $InstallDir "run-server.ps1"
@"
`$env:PYTHONUTF8 = "1"
`$env:PYTHONIOENCODING = "utf-8"
`$env:DOCLING_SERVE_API_KEY = (Get-Content "$keyFile" -Raw).Trim()
Write-Host "docling-serve listening on 0.0.0.0:$Port  (Ctrl+C to stop)"
& "$serve" run --host 0.0.0.0 --port $Port
"@ | Out-File -FilePath $runner -Encoding utf8

# --- 7. report -------------------------------------------------------------
$ips = @(Get-NetIPAddress -AddressFamily IPv4 |
         Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } |
         Select-Object -ExpandProperty IPAddress)

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "Start the server with:"
Write-Host "    powershell -ExecutionPolicy Bypass -File $runner" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then on the laptop:" -ForegroundColor Green
foreach ($ip in $ips) { Write-Host "    --server http://${ip}:$Port" }
Write-Host "    set HERO_DOCLING_API_KEY=$apiKey"
Write-Host ""
Write-Host "First conversion is slower: it downloads ~500 MB of layout/table models once."
