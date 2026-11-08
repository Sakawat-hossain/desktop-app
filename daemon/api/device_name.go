package api

import (
	"os"
	"runtime"
	"strings"
)

// deviceName - the name the panel shows in the user's device list,
// for example "DESKTOP-1AB2C (Windows)".
func deviceName() string {
	osName := runtime.GOOS
	switch osName {
	case "windows":
		osName = "Windows"
	case "darwin":
		osName = "macOS"
	case "linux":
		osName = "Linux"
	}

	host, err := os.Hostname()
	host = strings.TrimSpace(host)
	if err != nil || host == "" {
		return "OvpnPlus app (" + osName + ")"
	}
	if len(host) > 40 {
		host = host[:40]
	}
	return host + " (" + osName + ")"
}
