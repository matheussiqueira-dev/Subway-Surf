param(
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

$PythonCommand = Resolve-PythonCommand $Python
Assert-CompatiblePython $PythonCommand

$inputActionsPath = Join-Path $Root "Assets\SubwayOriginal\Scripts\InputControls.inputactions"
Get-Content -Raw -LiteralPath $inputActionsPath | ConvertFrom-Json | Out-Null

$requiredUnityPaths = @(
    "Assets\Scenes\Main.unity",
    "Assets\MergedGame\Scripts\MergedEndlessRunnerBootstrap.cs",
    "Assets\SubwayOriginal\Scripts\InputReader.cs",
    "Packages\manifest.json",
    "ProjectSettings\ProjectVersion.txt",
    "ProjectSettings\EditorBuildSettings.asset"
)

$requiredDashboardPaths = @(
    "dashboard\index.html",
    "dashboard\game.html",
    "dashboard\game.css",
    "dashboard\game.js"
)

foreach ($relativePath in $requiredUnityPaths) {
    $fullPath = Join-Path $Root $relativePath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        throw "Missing Unity project file: $relativePath"
    }
}

foreach ($relativePath in $requiredDashboardPaths) {
    $fullPath = Join-Path $ControllerRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        throw "Missing dashboard game file: $relativePath"
    }
}

$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCommand) {
    $bundledNode = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
    if (Test-Path -LiteralPath $bundledNode) {
        $nodeCommand = @{ Source = $bundledNode }
    }
}
if ($nodeCommand) {
    & $nodeCommand.Source --check (Join-Path $ControllerRoot "dashboard\game.js")
}

Get-Content -Raw -LiteralPath (Join-Path $Root "Packages\manifest.json") | ConvertFrom-Json | Out-Null

$sceneContent = Get-Content -Raw -LiteralPath (Join-Path $Root "Assets\Scenes\Main.unity")
if ($sceneContent -notmatch "018f93ae32794d91b0e6433e143f5a59") {
    throw "Main scene does not reference MergedEndlessRunnerBootstrap."
}

$buildSettings = Get-Content -Raw -LiteralPath (Join-Path $Root "ProjectSettings\EditorBuildSettings.asset")
if ($buildSettings -notmatch "Assets/Scenes/Main.unity") {
    throw "Main scene is not registered in EditorBuildSettings.asset."
}

$runtimeScripts = @()
$runtimeScripts += Get-ChildItem -LiteralPath (Join-Path $Root "Assets") -Filter "*.cs" -Recurse -File |
    Where-Object { $_.FullName -notmatch "\\Assets\\Editor\\" }

$editorImports = $runtimeScripts | Select-String -Pattern "using UnityEditor" -SimpleMatch
if ($editorImports) {
    throw "Runtime scripts still reference UnityEditor: $($editorImports -join ', ')"
}

Push-Location $ControllerRoot
try {
    if (-not $SkipInstall) {
        & $PythonCommand -m pip install -r requirements-dev.txt
    }

    & $PythonCommand -m pytest tests/
}
finally {
    Pop-Location
}
