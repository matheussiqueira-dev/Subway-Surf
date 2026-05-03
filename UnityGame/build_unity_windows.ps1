param(
    [string]$UnityPath = "",
    [string]$LogPath = "Builds\unity-build.log"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Resolve-UnityPath {
    param([string]$Requested)

    if ($Requested) {
        return $Requested
    }

    $Command = Get-Command Unity.exe -ErrorAction SilentlyContinue
    if ($Command) {
        return $Command.Source
    }

    $HubEditors = Join-Path ${env:ProgramFiles} "Unity\Hub\Editor"
    if (Test-Path -LiteralPath $HubEditors) {
        $Candidate = Get-ChildItem -LiteralPath $HubEditors -Recurse -Filter Unity.exe -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending |
            Select-Object -First 1
        if ($Candidate) {
            return $Candidate.FullName
        }
    }

    throw "Unity.exe was not found. Install Unity 2022.3 LTS or pass -UnityPath."
}

$Unity = Resolve-UnityPath $UnityPath
$ResolvedLog = Join-Path $Root $LogPath
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ResolvedLog) | Out-Null

& $Unity `
    -batchmode `
    -quit `
    -nographics `
    -projectPath $Root `
    -executeMethod BuildProject.BuildWindows `
    -logFile $ResolvedLog

if ($LASTEXITCODE -ne 0) {
    throw "Unity build failed with exit code $LASTEXITCODE. See $ResolvedLog"
}

Write-Host "Build complete: $Root\Builds\Windows\SubwaySurfVisionRunner.exe"
