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
# Counter-intuitively, 3.14 is the version that WORKS and 3.13 is the one that
# fails. docling-jobkit[ray] requires ray~=2.52 gated on python_version < "3.14",
# and ray ships no cp313 Windows wheel -- so 3.13 dies with ResolutionImpossible,
# while on 3.14 the marker drops ray entirely and the install resolves.
# (Learned the hard way, 2026-08-11 spare-machine test.)
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { throw "python not found on PATH. Install Python 3.14 first." }
$ver = (& python -c "import sys;print('%d.%d'%sys.version_info[:2])").Trim()
Write-Host "Python $ver at $($py.Source)"
if ($ver -eq "3.14") {
  Write-Host "  NOTE: on 3.14 grpcio has no prebuilt wheel and cannot compile on" -ForegroundColor Yellow
  Write-Host "  Windows. This script works around it by installing the newest" -ForegroundColor Yellow
  Write-Host "  grpcio that does ship a 3.14 wheel, then pinning to it." -ForegroundColor Yellow
} else {
  throw ("Python $ver will not resolve docling-serve on Windows. Install Python " +
         "3.14 and re-run.`n" +
         "  Why: docling-jobkit[ray] needs ray~=2.52 when python_version < '3.14', " +
         "and ray has no cp313 Windows wheel, so pip fails with " +
         "ResolutionImpossible.`n" +
         "  On 3.14 the dependency marker drops ray and the install succeeds.")
}

# --- 2. venv ---------------------------------------------------------------
if (-not (Test-Path $InstallDir)) { New-Item -ItemType Directory -Path $InstallDir | Out-Null }
$venv = Join-Path $InstallDir "venv"
if (-not (Test-Path $venv)) {
  Write-Host "Creating venv at $venv ..."
  & python -m venv $venv
} else {
  # A venv left by a different interpreter is otherwise reused in silence, so the
  # version reported above describes one Python while the install targets another.
  # Not cosmetic: docling-jobkit's ray dependency is gated on python_version <
  # "3.14", so a stale 3.13 venv fails to resolve while the log claims 3.14.
  $cfg = Join-Path $venv "pyvenv.cfg"
  $venvMinor = $null
  if (Test-Path $cfg) {
    $line = (Get-Content $cfg | Select-String '^\s*version\s*=' | Select-Object -First 1).Line
    if ($line) { $venvMinor = ((($line -split '=')[1]).Trim() -split '\.')[0..1] -join '.' }
  }
  if (-not $venvMinor) {
    throw "Cannot read a Python version from $cfg. Delete the venv and re-run: Remove-Item -Recurse -Force $venv"
  }
  if ($venvMinor -ne $ver) {
    throw "Existing venv at $venv is Python $venvMinor, but 'python' on PATH is $ver. Delete the venv and re-run: Remove-Item -Recurse -Force $venv"
  }
  Write-Host "Reusing existing venv (Python $venvMinor)"
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

  # A rule on the Private profile does NOTHING while the active adapter is
  # classified Public -- the rule reads as correct and enabled, and the port
  # stays shut. That cost a debugging session on 2026-08-11, so say it plainly
  # rather than reporting a success the network will not honour.
  $activeProfiles = @()
  try {
    $activeProfiles = @(Get-NetConnectionProfile -ErrorAction Stop |
                        Select-Object -ExpandProperty NetworkCategory -Unique)
  } catch {}
  if ($activeProfiles.Count -eq 0) {
    Write-Host "  Could not read the active network profile -- if the laptop cannot reach this box, check it is Private." -ForegroundColor Yellow
  } elseif ($activeProfiles -notcontains "Private" -and $activeProfiles -notcontains "DomainAuthenticated") {
    Write-Host ""
    Write-Host "  WARNING: the rule is on the Private profile, but this machine's" -ForegroundColor Yellow
    Write-Host "  network is currently: $($activeProfiles -join ', ')" -ForegroundColor Yellow
    Write-Host "  The rule will have NO EFFECT and the laptop will not reach port $Port." -ForegroundColor Yellow
    Write-Host "  Fix by reclassifying the adapter (elevated):" -ForegroundColor Yellow
    Write-Host "      Set-NetConnectionProfile -InterfaceAlias '<name>' -NetworkCategory Private" -ForegroundColor Cyan
    Write-Host "  List adapters with:  Get-NetConnectionProfile" -ForegroundColor Cyan
    Write-Host ""
  } else {
    Write-Host "  Active network profile is $($activeProfiles -join ', ') -- the rule applies."
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
# docling-serve 504s a synchronous /v1/convert/file that outruns this (default
# 120s), regardless of the client's own timeout. A spare machine is by
# definition the slow one: measured 135s for a 15-page mark scheme and 293s for
# a 28-page one, so the default fails every real conversion.
`$env:DOCLING_SERVE_MAX_SYNC_WAIT = "3600"
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
