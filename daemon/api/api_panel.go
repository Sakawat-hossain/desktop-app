package api

import (
	"net"
	"strings"
)

// Panel connection settings.
//
// The client talks to our admin panel (Laravel) instead of api.ivpn.net.
// All values are plain strings so a build can override them, for example:
//
//	go build -ldflags "-X github.com/ivpn/desktop-app/daemon/api.PanelHost=panel.example.com
//	                   -X github.com/ivpn/desktop-app/daemon/api.PanelAppKey=<FAST_API_KEY>"
var (
	// PanelHost - panel host name, optionally with a port ("panel.example.com" or "1.2.3.4:8080")
	PanelHost = "panel.example.com"
	// PanelScheme - "https" (recommended) or "http" (only for local tests)
	PanelScheme = "https"
	// PanelPathPrefix - path where the client API is mounted on the panel
	PanelPathPrefix = "api/client"
	// PanelAppKey - value of the panel's FAST_API_KEY, sent as the 'x-api-key' header
	PanelAppKey = ""
	// PanelCertHashes - optional comma-separated base64 SHA256 hashes of the panel's
	// certificate public keys (certificate key pinning). Empty: normal system CA validation.
	PanelCertHashes = ""
	// UpdateHost - host with update info; empty disables update checks
	UpdateHost = ""
)

func panelCertHashes() []string {
	ret := []string{}
	for _, h := range strings.Split(PanelCertHashes, ",") {
		if h = strings.TrimSpace(h); h != "" {
			ret = append(ret, h)
		}
	}
	return ret
}

// panelHostName returns the panel host without a port (used as TLS server name)
func panelHostName() string {
	if host, _, err := net.SplitHostPort(PanelHost); err == nil {
		return host
	}
	return PanelHost
}

// panelPort returns the port of PanelHost (empty when PanelHost has no port)
func panelPort() string {
	if _, port, err := net.SplitHostPort(PanelHost); err == nil {
		return port
	}
	return ""
}

func panelScheme() string {
	if PanelScheme == "http" {
		return "http"
	}
	return "https"
}
