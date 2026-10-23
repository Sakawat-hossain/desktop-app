#Requires -Version 5.1
<#
.SYNOPSIS
    Builds the unsigned LepidVPN installer on this PC (daemon + CLI + UI + NSIS).

.DESCRIPTION
    Run from "Developer PowerShell for VS 2022". The panel app key is read from
    the PANEL_APP_KEY environment variable or asked for (input hidden), so it
    never has to be written into a file or the command line.

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

if ([string]::IsNullOrWhiteSpace($PanelUrl)) { $PanelUrl = "${PanelScheme}://${PanelHost}" }

if ([string]::IsNullOrWhiteSpace($env:PANEL_APP_KEY)) {
    $secure = Read-Host -AsSecureString "Panel APP_FAST_API_KEY"
    $env:PANEL_APP_KEY = [System.Net.NetworkCredential]::new('', $secure).Password
}
if ([string]::IsNullOrWhiteSpace($env:PANEL_APP_KEY)) {
    Write-Host "[!] The panel app key is required."; exit 1
}

$env:PANEL_HOST     = $PanelHost
$env:PANEL_SCHEME   = $PanelScheme
$env:VITE_PANEL_URL = $PanelUrl

Write-Host "[*] Panel: $PanelUrl (API host: $PanelHost, scheme: $PanelScheme)"

foreach ($tool in @('go', 'node', 'npm', 'git', 'msbuild')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "[!] '$tool' not found in PATH. See docs/BUILD-WINDOWS.md for the requirements."
        exit 1
    }
}

Push-Location $PSScriptRoot
try {
    & cmd /c "build.bat $Arch"
    if ($LASTEXITCODE -ne 0) { Write-Host "[!] build.bat failed ($LASTEXITCODE)"; exit $LASTEXITCODE }

    & "$PSScriptRoot\package-release.ps1" -Arch $Arch
    if ($LASTEXITCODE -ne 0) { Write-Host "[!] package-release.ps1 failed ($LASTEXITCODE)"; exit $LASTEXITCODE }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "[*] Done. Installer: $PSScriptRoot\bin\"
