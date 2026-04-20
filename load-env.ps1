# Загружает переменные из .env в текущую сессию PowerShell.
# Использование (dot-sourcing обязательно):
#   . .\load-env.ps1

$envFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path $envFile)) {
    Write-Host ".env not found at $envFile" -ForegroundColor Red
    return
}

$loaded = 0
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq "" -or $line.StartsWith("#")) { return }
    if ($line -match '^\s*([^=\s]+)\s*=\s*(.*)\s*$') {
        $name = $matches[1]
        $value = $matches[2].Trim('"').Trim("'")
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        $loaded++
    }
}

Write-Host "Loaded $loaded variables from .env" -ForegroundColor Green
