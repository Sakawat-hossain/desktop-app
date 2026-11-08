package api

import (
	"strings"
	"testing"
)

func TestDeviceName(t *testing.T) {
	n := deviceName()
	if n == "" || !strings.HasSuffix(n, ")") || !strings.Contains(n, " (") {
		t.Fatalf("unexpected device name %q", n)
	}
	if len(n) > 60 {
		t.Fatalf("device name too long: %q", n)
	}
}
