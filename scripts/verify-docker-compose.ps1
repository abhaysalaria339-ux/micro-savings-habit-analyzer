[CmdletBinding()]
param(
    [int]$BackendTimeoutSeconds = 90,
    [int]$FrontendTimeoutSeconds = 90,
    [switch]$TearDown
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendHealthUrl = "http://127.0.0.1:8000/api/v1/health"
$BackendDatabaseHealthUrl = "http://127.0.0.1:8000/api/v1/health/db"
$FrontendUrl = "http://127.0.0.1:5173"
$DockerAvailable = $false

function Assert-CommandExists {
    param([string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. Install Docker Desktop and restart the terminal."
    }
}

function Invoke-DockerCompose {
    param([string[]]$Arguments)

    Push-Location $ProjectRoot
    try {
        & docker compose @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "docker compose $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

function Wait-ForHttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastError = $null

    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
                return
            }

            $lastError = "Unexpected status code $($response.StatusCode)."
        }
        catch {
            $lastError = $_.Exception.Message
        }

        Start-Sleep -Seconds 2
    }

    throw "Timed out waiting for $Url. Last error: $lastError"
}

try {
    Assert-CommandExists "docker"
    $DockerAvailable = $true

    Write-Host "Validating Docker Compose configuration..."
    Invoke-DockerCompose @("config", "--quiet")

    Write-Host "Building and starting the full stack..."
    Invoke-DockerCompose @("up", "--build", "-d")

    Write-Host "Waiting for backend health..."
    Wait-ForHttpOk -Url $BackendHealthUrl -TimeoutSeconds $BackendTimeoutSeconds

    Write-Host "Waiting for backend database readiness..."
    Wait-ForHttpOk -Url $BackendDatabaseHealthUrl -TimeoutSeconds $BackendTimeoutSeconds

    Write-Host "Waiting for frontend..."
    Wait-ForHttpOk -Url $FrontendUrl -TimeoutSeconds $FrontendTimeoutSeconds

    Write-Host "Full-stack Docker Compose verification passed."
    Write-Host "Frontend: $FrontendUrl"
    Write-Host "Backend health: $BackendHealthUrl"
}
catch {
    Write-Error $_.Exception.Message
    Write-Host "Useful diagnostics:"
    Write-Host "  docker compose ps"
    Write-Host "  docker compose logs backend"
    Write-Host "  docker compose logs backend-migrate"
    Write-Host "  docker compose logs frontend"
    exit 1
}
finally {
    if ($TearDown -and $DockerAvailable) {
        Write-Host "Stopping the full stack because -TearDown was provided..."
        Invoke-DockerCompose @("down")
    }
}
