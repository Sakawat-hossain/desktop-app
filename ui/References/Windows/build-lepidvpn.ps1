#Requires -Version 5.1
<#
.SYNOPSIS
    Builds the unsigned LepidVPN installer on this PC (daemon + CLI + UI + NSIS).

.DESCRIPTION
    Works from a normal PowerShell window: the script reloads PATH (tools
    installed after the window was opened) and enters the Visual Studio build
    environment itself. The panel app key is read from the PANEL_APP_KEY
    environment variable or asked for (input hidden), so it never has to be
    written into a file or the command line. Output is saved to build.log.

.EXAMPLE
    .\build-lepidvpn.ps1 -PanelHost panel.example.com

.EXAMPLE
    # test panel without HTTPS
    .\build-lepidvpn.ps1 -PanelHost 141.11.76.19 -PanelScheme http
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$PanelHost,
    [ValidateSet('https', 'http')]
    [string]$PanelScheme = 'https',
    [string]$PanelUrl = '',
    [ValidateSet('x86_64', 'arm64')]
    [string]$Arch = 'x86_64'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$LogFile = Join-Path $PSScriptRoot 'build.log'

function Add-MissingPathEntries {
    # Tools installed after this window was opened are only in the registry PATH.
    $current = $env:Path -split ';' | Where-Object { $_ }
    foreach ($scope in 'Machine', 'User') {
        foreach ($p in ([Environment]::GetEnvironmentVariable('Path', $scope) -split ';')) {
            if ($p -and ($current -notcontains $p)) { $env:Path += ";$p"; $current += $p }
        }
    }
}

function Enter-VisualStudioEnvironment {
    if ($env:VSCMD_VER -and (Get-Command msbuild -ErrorAction SilentlyContinue)) { return }

    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    if (-not (Test-Path $vswhere)) {
        Write-Host "[!] Visual Studio 2022 (Build Tools) not found. See docs/BUILD-WINDOWS.md."; exit 1
    }
    $vsPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if ([string]::IsNullOrWhiteSpace($vsPath)) {
        Write-Host "[!] Visual Studio is installed without the C++ build tools. See docs/BUILD-WINDOWS.md."; exit 1
    }
    $devShell = Join-Path $vsPath 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll'
    Import-Module $devShell
    $vsArch = if ($Arch -eq 'arm64') { 'arm64' } else { 'amd64' }
    Write-Host "[*] Visual Studio build environment: $vsPath ($vsArch)"
    Enter-VsDevShell -VsInstallPath $vsPath -SkipAutomaticLocation -DevCmdArguments "-arch=$vsArch -host_arch=amd64" | Out-Null
}

if ([string]::IsNullOrWhiteSpace($PanelUrl)) { $PanelUrl = "${PanelScheme}://${PanelHost}" }

Add-MissingPathEntries
Enter-VisualStudioEnvironment

$missing = @()
foreach ($tool in @('git', 'go', 'node', 'npm', 'cmake', 'gcc', 'msbuild')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { $missing += $tool }
}
if (-not (Test-Path 'C:\Program Files (x86)\NSIS\makensis.exe')) { $missing += 'NSIS' }
if ($missing.Count -gt 0) {
    Write-Host "[!] Missing tools: $($missing -join ', '). See docs/BUILD-WINDOWS.md."
    exit 1
}

if ([string]::IsNullOrWhiteSpace($env:PANEL_APP_KEY)) {
    Write-Host ""
    $secure = Read-Host -AsSecureString "Paste the panel APP_FAST_API_KEY and press Enter (input is hidden)"
    $env:PANEL_APP_KEY = [System.Net.NetworkCredential]::new('', $secure).Password
}
if ([string]::IsNullOrWhiteSpace($env:PANEL_APP_KEY)) {
    Write-Host "[!] The panel app key is required."; exit 1
}

$env:PANEL_HOST     = $PanelHost
$env:PANEL_SCHEME   = $PanelScheme
$env:VITE_PANEL_URL = $PanelUrl

Write-Host "[*] Panel: $PanelUrl (API host: $PanelHost, scheme: $PanelScheme)"
Write-Host "[*] Build log: $LogFile"
Set-Content -Path $LogFile -Value "LepidVPN build $(Get-Date -Format s) panel=$PanelUrl arch=$Arch"

# native tools write progress to stderr; don't treat it as a failure
$ErrorActionPreference = 'Continue'

Push-Location $PSScriptRoot
try {
    & cmd /c "build.bat $Arch 2>&1" | Tee-Object -FilePath $LogFile -Append
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Host "[!] build.bat failed ($code). Send the end of build.log: Get-Content build.log -Tail 60"
        exit $code
    }

    & "$PSScriptRoot\package-release.ps1" -Arch $Arch *>&1 | Tee-Object -FilePath $LogFile -Append
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Host "[!] package-release.ps1 failed ($code). Send the end of build.log: Get-Content build.log -Tail 60"
        exit $code
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "[*] Done. Installer:"
Get-ChildItem (Join-Path $PSScriptRoot 'bin') -Filter 'LepidVPN-*.exe' | ForEach-Object { Write-Host "    $($_.FullName)" }
