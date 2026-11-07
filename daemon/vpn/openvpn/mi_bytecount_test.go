package openvpn

import (
	"testing"

	"github.com/ivpn/desktop-app/daemon/vpn"
)

func TestOnByteCountForwardsCounters(t *testing.T) {
	ch := make(chan vpn.StateInfo, 1)
	mi := &ManagementInterface{stateChan: ch}

	mi.onByteCount("12345,678")

	select {
	case s := <-ch:
		if s.State != vpn.TRAFFIC_STATS || s.RxBytes != 12345 || s.TxBytes != 678 {
			t.Fatalf("unexpected state: %+v", s)
		}
	default:
		t.Fatal("no traffic sample was sent")
	}
}

func TestOnByteCountIgnoresBadInput(t *testing.T) {
	ch := make(chan vpn.StateInfo, 1)
	mi := &ManagementInterface{stateChan: ch}

	for _, in := range []string{"", "1", "a,b", "1,2,3", "-1,5"} {
		mi.onByteCount(in)
	}
	if len(ch) != 0 {
		t.Fatalf("bad input produced %d samples", len(ch))
	}
}

func TestOnByteCountNeverBlocks(t *testing.T) {
	ch := make(chan vpn.StateInfo) // unbuffered and nobody reading
	mi := &ManagementInterface{stateChan: ch}
	mi.onByteCount("1,2") // must return instead of blocking
}

func TestTrafficStatsStateName(t *testing.T) {
	if vpn.TRAFFIC_STATS.String() != "TRAFFIC_STATS" {
		t.Fatalf("got %q", vpn.TRAFFIC_STATS.String())
	}
	if vpn.TUNNEL_HEALTH.String() != "TUNNEL_HEALTH" {
		t.Fatalf("got %q", vpn.TUNNEL_HEALTH.String())
	}
}
