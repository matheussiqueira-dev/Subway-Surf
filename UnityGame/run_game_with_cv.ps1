param(
    [ValidateSet("controller", "api", "all")]
    [string]$Mode = "all",

    [string]$GamePath = "",
    [string]$GameWindowTitle = "Subway Surfers",
    [string]$Profile = "easy",
    [int]$CameraIndex = 0,
    [string]$Python = "",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ControllerRoot = Split-Path -Parent $Root

function Resolve-PythonCommand {
    param([string]$Requested)

    if ($Requested) {
        return $Requested
    }

    if ($env:CV_PYTHON) {
        return $env:CV_PYTHON
    }

    $BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $BundledPython) {
        return $BundledPython
    }

    return "python"
}

function Assert-CompatiblePython {
    param([string]$PythonCommand)

    $VersionText = (& $PythonCommand -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
    $Version = [version]$VersionText
    if ($Version -lt [version]"3.10" -or $Version -ge [version]"3.13") {
        throw "Use Python 3.10, 3.11 or 3.12 for MediaPipe. Current Python is $VersionText."
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $ControllerRoot "main.py"))) {
    throw "Subway Surf controller root was not found at $ControllerRoot"
}

if ($GamePath) {
    if (-not (Test-Path -LiteralPath $GamePath)) {
        throw "Game executable was not found: $GamePath"
    }

    Start-Process -FilePath $GamePath -WorkingDirectory (Split-Path -Parent $GamePath)
    Start-Sleep -Seconds 2
}

$env:GAME_WINDOW_TITLE = $GameWindowTitle
$env:CAMERA_INDEX = "$CameraIndex"
$PythonCommand = Resolve-PythonCommand $Python
Assert-CompatiblePython $PythonCommand

Push-Location $ControllerRoot
try {
    if (-not $SkipInstall) {
        & $PythonCommand -m pip install -r requirements.txt
    }

    & $PythonCommand main.py --mode $Mode --camera-index $CameraIndex --profile $Profile
}
finally {
    Pop-Location
}
