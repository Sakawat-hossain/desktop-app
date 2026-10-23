# Connecting the app to our admin panel

This app is a fork of the IVPN desktop client. Instead of `api.ivpn.net` it
talks to our Laravel admin panel (`Vpn-Admin-Panel`), which serves an
IVPN-compatible client API under `/api/client`:

| App request                  | Panel route                              |
|------------------------------|------------------------------------------|
| log in (e-mail + password)   | `POST /api/client/v4/session/new`        |
| session status / log out     | `POST /api/client/v4/session/status`, `/delete` |
| server list                  | `GET /api/client/v5/servers.json` (`x-api-key`) |
| geo lookup                   | `GET /api/client/v4/geo-lookup`          |

Only OpenVPN is used for now. The server list carries the panel's CA
certificate and tls-auth key (`config.openvpn`), so the same app build works
with any panel install; no `.ovpn` import is needed. The daemon connects with
the per-device VPN username/password the panel returns at login, and each
VPN server checks them with the panel.

## Build settings

The daemon reads the panel address at build time (Go `-ldflags -X`). The
build scripts pass these environment variables when they are set:

| Variable            | Meaning                                                        |
|---------------------|----------------------------------------------------------------|
| `PANEL_HOST`        | panel host, optionally with port: `panel.example.com`           |
| `PANEL_SCHEME`      | `https` (default); `http` only for local tests                  |
| `PANEL_APP_KEY`     | the panel's `APP_FAST_API_KEY` (sent as `x-api-key`)            |
| `PANEL_CERT_HASHES` | optional: comma-separated base64 SHA-256 hashes of the panel's certificate public keys (key pinning). Empty: normal CA validation |

The UI needs the panel URL for links (sign-up, account, devices):

| Variable          | Meaning                                  |
|-------------------|------------------------------------------|
| `VITE_PANEL_URL`  | `https://panel.example.com`              |

Example (Windows):

```bat
set PANEL_HOST=panel.example.com
set PANEL_APP_KEY=...
set VITE_PANEL_URL=https://panel.example.com
cd ui\References\Windows
build.bat
```

Never commit the real app key; keep it in the CI secrets.

## Windows installer from GitHub Actions

The **Windows installer** workflow (`.github/workflows/windows-installer.yml`)
builds the unsigned installer `LepidVPN-v<version>.exe` on demand (Actions ->
Windows installer -> Run workflow). To build on your own PC see
[BUILD-WINDOWS.md](BUILD-WINDOWS.md). Download it from the run page under **Artifacts**.

Before building, set in the repository settings (Settings -> Secrets and
variables -> Actions):

* Variables: `PANEL_HOST`, `PANEL_URL` (and `PANEL_SCHEME=http` only for a test
  panel without HTTPS)
* Secret: `PANEL_APP_KEY`

The installer is not code-signed yet, so Windows SmartScreen shows "Unknown
publisher" (More info -> Run anyway).

## Panel side

* Add OpenVPN servers in the panel as **Panel-managed OpenVPN** and deploy them.
* `CLIENT_API_IPS` (panel `.env`): public IPs of the panel. The app uses them
  when DNS fails and lets them through the kill switch. Default: resolved from
  `APP_URL`.
