# One-time machine setup for the motion-reel skill (Windows PowerShell, no bash needed).
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1
# 1) node, ffmpeg, python on PATH (installs missing ones with winget)  2) Python packages from requirements.txt
# Playwright + Chromium are installed per film project (SKILL.md step 0).
$ids = [ordered]@{ node = 'OpenJS.NodeJS.LTS'; ffmpeg = 'Gyan.FFmpeg'; python = 'Python.Python.3.12' }
$missing = @($ids.Keys | Where-Object { -not (Get-Command $_ -ErrorAction SilentlyContinue) })
if ($missing.Count -gt 0) {
    Write-Host "MISSING: $($missing -join ', ') -- installing"
    foreach ($m in $missing) { winget install -e --id $ids[$m] --accept-source-agreements --accept-package-agreements }
    Write-Host 'Installed. Open a NEW terminal (PATH refresh) and run this script again.'
    exit 1
}
Write-Host "OK: node $(node -v), $((ffmpeg -version | Select-Object -First 1) -replace ' Copyright.*',''), $(python --version)"
python -m pip install -r "$PSScriptRoot\requirements.txt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Setup done. Ask your agent for a motion reel; it follows SKILL.md.'
