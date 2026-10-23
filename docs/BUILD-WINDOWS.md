# Build and test LepidVPN on Windows

## 1. Install the tools (once)

* [Git](https://git-scm.com/download/win)
* [Go 1.26+](https://go.dev/dl/)
* [Node.js 22](https://nodejs.org/) (includes npm)
* [NSIS 3](https://nsis.sourceforge.io/Download) (default folder `C:\Program Files (x86)\NSIS`)
* [Visual Studio 2022](https://visualstudio.microsoft.com/) (Community is fine) with:
  * workload **Desktop development with C++**
  * MSVC v143 C++ x64 build tools
  * C++ ATL for latest v143 build tools
  * Windows 10 SDK 10.0.19041.0 and Windows 11 SDK 10.0.22000.0
* gcc for Go/cgo, e.g. [MSYS2](https://www.msys2.org/) → in the MSYS2 UCRT64 shell:
  `pacman -S mingw-w64-ucrt-x86_64-gcc`, then add `C:\msys64\ucrt64\bin` to PATH.
* [CMake](https://cmake.org/download/) (used by the KEM helper build; also part of VS "C++ CMake tools")

## 2. Get the code

```powershell
git clone https://github.com/Sakawat-hossain/desktop-app.git
cd desktop-app
git checkout claude/new-session-3l5u10
```

## 3. Build the installer

Open **Developer PowerShell for VS 2022**, then:

```powershell
cd desktop-app\ui\References\Windows
.\build-lepidvpn.ps1 -PanelHost panel.example.com
# test panel without HTTPS:
# .\build-lepidvpn.ps1 -PanelHost 141.11.76.19 -PanelScheme http
```

The script asks for the panel's `APP_FAST_API_KEY` (input hidden). The first
build downloads and compiles WireGuard, obfs4proxy, v2ray, dnscrypt-proxy and
the KEM helper, so it takes a while; later builds reuse them.

Result: `ui\References\Windows\bin\LepidVPN-v<version>.exe` (unsigned; Windows
SmartScreen: More info → Run anyway).

If PowerShell refuses to run scripts:
`Set-ExecutionPolicy -Scope Process Bypass`

## 4. Test checklist

1. Install, then check *Services*: **LepidVPN** is running.
2. Start LepidVPN, log in with a panel user's e-mail + password.
3. Server list shows the panel's *Panel-managed OpenVPN* servers.
4. Connect → the panel's *Devices* page lists this PC; browse the web; check
   the public IP.
5. Disconnect, log out; wrong password shows an error.
6. Optional: enable the firewall (kill switch), connect/disconnect.

Logs if something fails: `C:\Program Files\LepidVPN\log\` (service) and
`%APPDATA%\LepidVPN\logs\` (app).
