package service

import (
	"testing"

	apiTypes "github.com/ivpn/desktop-app/daemon/api/types"
	"github.com/ivpn/desktop-app/daemon/service/preferences"
	"github.com/ivpn/desktop-app/daemon/service/types"
	"github.com/ivpn/desktop-app/daemon/vpn"
)

var (
	testAccountUnknown = preferences.AccountStatus{}
	testAccountFree    = preferences.AccountStatus{Active: true, CurrentPlan: "Free", Capabilities: []string{}}
	testAccountPremium = preferences.AccountStatus{Active: true, CurrentPlan: "Premium", Capabilities: []string{"premium"}}
)

func testHostBase(hostname, ip string, isPremium bool) apiTypes.HostInfoBase {
	return apiTypes.HostInfoBase{Hostname: hostname, Host: ip, IsPremium: isPremium}
}

func testOvpnHost(hostname, ip string, isPremium bool) apiTypes.OpenVPNServerHostInfo {
	return apiTypes.OpenVPNServerHostInfo{HostInfoBase: testHostBase(hostname, ip, isPremium)}
}

func testWgHost(hostname, ip string, isPremium bool) apiTypes.WireGuardServerHostInfo {
	return apiTypes.WireGuardServerHostInfo{HostInfoBase: testHostBase(hostname, ip, isPremium)}
}

// Servers list as the OvpnPlus panel sends it:
//
//	server-1 (Dhaka):     Free location (two Free hosts)
//	server-2 (Singapore): Mixed location (one Free and one Premium host)
//	server-3 (Tokyo):     Premium location (all hosts are Premium)
func testServersList() *apiTypes.ServersInfoResponse {
	return &apiTypes.ServersInfoResponse{
		OpenvpnServers: []apiTypes.OpenvpnServerInfo{
			{
				ServerInfoBase: apiTypes.ServerInfoBase{Gateway: "server-1.gw", CountryCode: "BD", City: "Dhaka"},
				Hosts:          []apiTypes.OpenVPNServerHostInfo{testOvpnHost("bd1.gw", "10.0.1.1", false), testOvpnHost("bd2.gw", "10.0.1.2", false)},
			},
			{
				ServerInfoBase: apiTypes.ServerInfoBase{Gateway: "server-2.gw", CountryCode: "SG", City: "Singapore"},
				Hosts:          []apiTypes.OpenVPNServerHostInfo{testOvpnHost("sg1.gw", "10.0.2.1", false), testOvpnHost("sg2.gw", "10.0.2.2", true)},
			},
			{
				ServerInfoBase: apiTypes.ServerInfoBase{Gateway: "server-3.gw", CountryCode: "JP", City: "Tokyo", IsPremium: true},
				Hosts:          []apiTypes.OpenVPNServerHostInfo{testOvpnHost("jp1.gw", "10.0.3.1", true), testOvpnHost("jp2.gw", "10.0.3.2", true)},
			},
		},
		WireguardServers: []apiTypes.WireGuardServerInfo{
			{
				ServerInfoBase: apiTypes.ServerInfoBase{Gateway: "server-1.wg", CountryCode: "BD", City: "Dhaka"},
				Hosts:          []apiTypes.WireGuardServerHostInfo{testWgHost("bd1.wg", "10.1.1.1", false), testWgHost("bd2.wg", "10.1.1.2", false)},
			},
			{
				ServerInfoBase: apiTypes.ServerInfoBase{Gateway: "server-2.wg", CountryCode: "SG", City: "Singapore"},
				Hosts:          []apiTypes.WireGuardServerHostInfo{testWgHost("sg1.wg", "10.1.2.1", false), testWgHost("sg2.wg", "10.1.2.2", true)},
			},
			{
				ServerInfoBase: apiTypes.ServerInfoBase{Gateway: "server-3.wg", CountryCode: "JP", City: "Tokyo", IsPremium: true},
				Hosts:          []apiTypes.WireGuardServerHostInfo{testWgHost("jp1.wg", "10.1.3.1", true), testWgHost("jp2.wg", "10.1.3.2", true)},
			},
		},
	}
}

func testService(account preferences.AccountStatus, servers *apiTypes.ServersInfoResponse) *Service {
	return &Service{
		_preferences:    preferences.Preferences{Account: account},
		_serversUpdater: &serversUpdater{servers: servers},
	}
}

// premium hosts of testServersList(), by IP
var testPremiumIPs = map[string]bool{
	"10.0.2.2": true, "10.0.3.1": true, "10.0.3.2": true,
	"10.1.2.2": true, "10.1.3.1": true, "10.1.3.2": true,
}

func hostIPs[H hostBaseInterface](hosts []H) (ret []string) {
	for _, h := range hosts {
		ret = append(ret, h.GetHostInfoBase().Host)
	}
	return ret
}

func equalStrings(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func TestUsableServers(t *testing.T) {
	all := testServersList()

	// Premium account (or unknown status): the list is not changed
	if got := usableServers(all, true); got != all {
		t.Error("usableServers(isPremiumAllowed=true) must return the original list")
	}

	got := usableServers(all, false)
	if len(got.OpenvpnServers) != 2 || len(got.WireguardServers) != 2 {
		t.Fatalf("expected 2 OpenVPN and 2 WireGuard locations, got %d and %d", len(got.OpenvpnServers), len(got.WireguardServers))
	}
	// Free location: all hosts kept
	if ips := hostIPs(got.OpenvpnServers[0].Hosts); !equalStrings(ips, []string{"10.0.1.1", "10.0.1.2"}) {
		t.Errorf("free location: unexpected hosts %v", ips)
	}
	// Mixed location: only the Free host kept
	if ips := hostIPs(got.OpenvpnServers[1].Hosts); !equalStrings(ips, []string{"10.0.2.1"}) {
		t.Errorf("mixed location (OpenVPN): unexpected hosts %v", ips)
	}
	if ips := hostIPs(got.WireguardServers[1].Hosts); !equalStrings(ips, []string{"10.1.2.1"}) {
		t.Errorf("mixed location (WireGuard): unexpected hosts %v", ips)
	}
	// Premium location: skipped
	for _, s := range got.OpenvpnServers {
		if s.Gateway == "server-3.gw" {
			t.Error("premium location must be skipped")
		}
	}

	// the original (cached) list is not modified
	if len(all.OpenvpnServers) != 3 || len(all.OpenvpnServers[1].Hosts) != 2 || len(all.WireguardServers[1].Hosts) != 2 {
		t.Error("original servers list was modified")
	}
}

func TestGetFastestServerByPings(t *testing.T) {
	all := testServersList()
	usable := usableServers(all, false)

	pings := map[string]int{
		"10.0.3.1": 5,  // Tokyo (Premium) - the fastest host
		"10.0.2.2": 10, // Singapore, Premium host
		"10.0.2.1": 40, // Singapore, Free host
		"10.0.1.1": 30, // Dhaka
	}

	// Premium account: the fastest host
	if svr, err := getFastestServerByPings(all.OpenvpnServers, pings, nil); err != nil || svr.Gateway != "server-3.gw" {
		t.Errorf("premium account: expected server-3.gw, got '%s' (err: %v)", svr.Gateway, err)
	}

	// Free account: the fastest usable host (Premium hosts are not considered)
	if svr, err := getFastestServerByPings(usable.OpenvpnServers, pings, nil); err != nil || svr.Gateway != "server-1.gw" {
		t.Errorf("free account: expected server-1.gw, got '%s' (err: %v)", svr.Gateway, err)
	}

	// Free account; the mixed location is the fastest by its Free host: only the Free host is returned
	pings["10.0.2.1"] = 20
	svr, err := getFastestServerByPings(usable.OpenvpnServers, pings, nil)
	if err != nil || svr.Gateway != "server-2.gw" {
		t.Fatalf("free account (mixed location): expected server-2.gw, got '%s' (err: %v)", svr.Gateway, err)
	}
	if ips := hostIPs(svr.Hosts); !equalStrings(ips, []string{"10.0.2.1"}) {
		t.Errorf("free account (mixed location): unexpected hosts %v", ips)
	}

	// excluded gateways are skipped
	if svr, err := getFastestServerByPings(usable.OpenvpnServers, pings, []string{"server-2"}); err != nil || svr.Gateway != "server-1.gw" {
		t.Errorf("excluded gateway: expected server-1.gw, got '%s' (err: %v)", svr.Gateway, err)
	}

	// no ping results for usable hosts
	if _, err := getFastestServerByPings(usable.OpenvpnServers, map[string]int{"10.0.3.1": 5}, nil); err == nil {
		t.Error("expected error when no usable host has ping result")
	}
}

func TestGetRandomServer(t *testing.T) {
	if _, err := getRandomServer([]apiTypes.WireGuardServerInfo{}); err == nil {
		t.Error("expected error for empty servers list")
	}

	usable := usableServers(testServersList(), false)
	for i := 0; i < 100; i++ {
		svr, err := getRandomServer(usable.WireguardServers)
		if err != nil {
			t.Fatal(err)
		}
		for _, ip := range hostIPs(svr.Hosts) {
			if testPremiumIPs[ip] {
				t.Fatalf("random server for Free account has Premium host %s", ip)
			}
		}
	}
}

func TestRemovePremiumHosts(t *testing.T) {
	all := testServersList()

	// OpenVPN: mixed location -> only the Free host
	params := types.ConnectionParams{VpnType: vpn.OpenVPN}
	params.OpenVpnParameters.EntryVpnServer.Hosts = all.OpenvpnServers[1].Hosts
	ret, isEntryPremiumOnly := removePremiumHosts(params, all)
	if isEntryPremiumOnly || !equalStrings(hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), []string{"10.0.2.1"}) {
		t.Errorf("OpenVPN mixed location: unexpected result %v (premium only: %v)", hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), isEntryPremiumOnly)
	}
	// original params are not modified
	if len(params.OpenVpnParameters.EntryVpnServer.Hosts) != 2 || len(all.OpenvpnServers[1].Hosts) != 2 {
		t.Error("original hosts list was modified")
	}

	// WireGuard: Premium location -> not changed, reported
	params = types.ConnectionParams{VpnType: vpn.WireGuard}
	params.WireGuardParameters.EntryVpnServer.Hosts = all.WireguardServers[2].Hosts
	ret, isEntryPremiumOnly = removePremiumHosts(params, all)
	if !isEntryPremiumOnly || len(ret.WireGuardParameters.EntryVpnServer.Hosts) != 2 {
		t.Errorf("WireGuard premium location: expected unchanged hosts and 'premium only' (got %v, %v)", hostIPs(ret.WireGuardParameters.EntryVpnServer.Hosts), isEntryPremiumOnly)
	}

	// The servers list has priority over the host's own mark (saved params may have no 'is_premium' field)
	params = types.ConnectionParams{VpnType: vpn.WireGuard}
	params.WireGuardParameters.EntryVpnServer.Hosts = []apiTypes.WireGuardServerHostInfo{
		testWgHost("sg1.wg", "10.1.2.1", false),
		testWgHost("sg2.wg", "10.1.2.2", false), // Premium in the servers list
		testWgHost("jp1.wg", "", false),         // Premium location in the servers list (matched by hostname)
		testWgHost("xx1.wg", "10.9.9.1", true),  // not in the servers list: own mark
		testWgHost("xx2.wg", "10.9.9.2", false), // not in the servers list: own mark
	}
	ret, isEntryPremiumOnly = removePremiumHosts(params, all)
	if isEntryPremiumOnly || !equalStrings(hostIPs(ret.WireGuardParameters.EntryVpnServer.Hosts), []string{"10.1.2.1", "10.9.9.2"}) {
		t.Errorf("WireGuard hosts check by servers list: unexpected result %v", hostIPs(ret.WireGuardParameters.EntryVpnServer.Hosts))
	}

	// Multi-Hop exit server: Premium hosts removed when there is a Free one
	params = types.ConnectionParams{VpnType: vpn.WireGuard}
	params.WireGuardParameters.EntryVpnServer.Hosts = all.WireguardServers[0].Hosts
	params.WireGuardParameters.MultihopExitServer.Hosts = all.WireguardServers[1].Hosts
	ret, isEntryPremiumOnly = removePremiumHosts(params, all)
	if isEntryPremiumOnly ||
		len(ret.WireGuardParameters.EntryVpnServer.Hosts) != 2 ||
		!equalStrings(hostIPs(ret.WireGuardParameters.MultihopExitServer.Hosts), []string{"10.1.2.1"}) {
		t.Errorf("Multi-Hop: unexpected result entry=%v exit=%v", hostIPs(ret.WireGuardParameters.EntryVpnServer.Hosts), hostIPs(ret.WireGuardParameters.MultihopExitServer.Hosts))
	}

	// No hosts: nothing to do
	params = types.ConnectionParams{VpnType: vpn.OpenVPN}
	if _, isEntryPremiumOnly = removePremiumHosts(params, all); isEntryPremiumOnly {
		t.Error("empty hosts list must not be reported as 'premium only'")
	}
}

func TestRemoveNotAllowedHosts(t *testing.T) {
	all := testServersList()
	params := types.ConnectionParams{VpnType: vpn.OpenVPN}
	params.OpenVpnParameters.EntryVpnServer.Hosts = all.OpenvpnServers[1].Hosts // mixed location

	// unknown account status and Premium account: not changed
	for _, acc := range []preferences.AccountStatus{testAccountUnknown, testAccountPremium} {
		ret, isEntryNotAllowed := testService(acc, all).removeNotAllowedHosts(params)
		if isEntryNotAllowed || len(ret.OpenVpnParameters.EntryVpnServer.Hosts) != 2 {
			t.Errorf("account %v: hosts must not be changed (got %v)", acc.Capabilities, hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts))
		}
	}

	// Free account: only the Free host
	s := testService(testAccountFree, all)
	ret, isEntryNotAllowed := s.removeNotAllowedHosts(params)
	if isEntryNotAllowed || !equalStrings(hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), []string{"10.0.2.1"}) {
		t.Errorf("free account: unexpected hosts %v", hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts))
	}
	// useAllowedHosts: same result (no need to choose another server)
	ret, err := s.useAllowedHosts(params)
	if err != nil || !equalStrings(hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), []string{"10.0.2.1"}) {
		t.Errorf("free account (useAllowedHosts): unexpected hosts %v (err: %v)", hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), err)
	}

	// Free account, Premium location
	params.OpenVpnParameters.EntryVpnServer.Hosts = all.OpenvpnServers[2].Hosts
	if _, isEntryNotAllowed = s.removeNotAllowedHosts(params); !isEntryNotAllowed {
		t.Error("free account: Premium location must be reported as not allowed")
	}
}

func TestUpdateParamsAccordingToMetadata_RandomServer(t *testing.T) {
	all := testServersList()

	for _, vpnType := range []vpn.Type{vpn.OpenVPN, vpn.WireGuard} {
		s := testService(testAccountFree, all)
		params := types.ConnectionParams{VpnType: vpnType}
		params.Metadata.ServerSelectionEntry = types.Random

		for i := 0; i < 100; i++ {
			ret, err := s.updateParamsAccordingToMetadata(params)
			if err != nil {
				t.Fatal(err)
			}
			var ips []string
			if vpnType == vpn.OpenVPN {
				ips = hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts)
			} else {
				ips = hostIPs(ret.WireGuardParameters.EntryVpnServer.Hosts)
			}
			if len(ips) == 0 {
				t.Fatal("no hosts chosen")
			}
			for _, ip := range ips {
				if testPremiumIPs[ip] {
					t.Fatalf("Free account (%v): Random server has Premium host %s", vpnType, ip)
				}
			}
		}
	}

	// Free account, only Premium locations: error (no panic)
	premiumOnly := &apiTypes.ServersInfoResponse{WireguardServers: []apiTypes.WireGuardServerInfo{all.WireguardServers[2]}}
	params := types.ConnectionParams{VpnType: vpn.WireGuard}
	params.Metadata.ServerSelectionEntry = types.Random
	if _, err := testService(testAccountFree, premiumOnly).updateParamsAccordingToMetadata(params); err == nil {
		t.Error("expected error when no server is available for the Free account")
	}
	// Unknown account status: Premium locations are used as before
	ret, err := testService(testAccountUnknown, premiumOnly).updateParamsAccordingToMetadata(params)
	if err != nil || len(ret.WireGuardParameters.EntryVpnServer.Hosts) != 2 {
		t.Errorf("unknown account status: expected the Premium location (err: %v)", err)
	}
}

// testVpnProcess - a non-nil VPN process: PingServers() then returns the saved ping results
// (as in the connected state) instead of pinging, so the tests do not need network access
type testVpnProcess struct{ vpn.Process }

func testServiceWithPings(account preferences.AccountStatus, servers *apiTypes.ServersInfoResponse, pings map[string]int) *Service {
	s := testService(account, servers)
	s._vpn = testVpnProcess{}
	s._ping._result = pings
	return s
}

// Saved location is Premium only (e.g. after a downgrade): auto-connect uses another server the account can use
func TestUseAllowedHosts_PremiumLocation(t *testing.T) {
	all := testServersList()
	pings := map[string]int{
		"10.0.3.1": 5,  // Tokyo (Premium) - the fastest host
		"10.0.2.2": 10, // Singapore, Premium host
		"10.0.2.1": 20, // Singapore, Free host
		"10.0.1.1": 30, // Dhaka
		"10.1.3.1": 5, "10.1.2.2": 10, "10.1.1.2": 15, "10.1.2.1": 20,
	}

	ovpnParams := types.ConnectionParams{VpnType: vpn.OpenVPN}
	ovpnParams.OpenVpnParameters.EntryVpnServer.Hosts = all.OpenvpnServers[2].Hosts // Premium location
	wgParams := types.ConnectionParams{VpnType: vpn.WireGuard}
	wgParams.WireGuardParameters.EntryVpnServer.Hosts = all.WireguardServers[2].Hosts // Premium location

	// Unknown account status and Premium account: not changed, no pinging
	for _, acc := range []preferences.AccountStatus{testAccountUnknown, testAccountPremium} {
		ret, err := testService(acc, all).useAllowedHosts(ovpnParams)
		if err != nil || !equalStrings(hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), []string{"10.0.3.1", "10.0.3.2"}) {
			t.Errorf("account %v: hosts must not be changed (got %v, err: %v)", acc.Capabilities, hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), err)
		}
	}

	// Free account: the fastest server the account can use (only its Free hosts)
	s := testServiceWithPings(testAccountFree, all, pings)
	ret, err := s.useAllowedHosts(ovpnParams)
	if err != nil || !equalStrings(hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), []string{"10.0.2.1"}) {
		t.Errorf("free account (OpenVPN): expected the Free host of the fastest usable location, got %v (err: %v)", hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts), err)
	}
	ret, err = s.useAllowedHosts(wgParams)
	if err != nil || !equalStrings(hostIPs(ret.WireGuardParameters.EntryVpnServer.Hosts), []string{"10.1.1.1", "10.1.1.2"}) {
		t.Errorf("free account (WireGuard): expected the fastest usable location, got %v (err: %v)", hostIPs(ret.WireGuardParameters.EntryVpnServer.Hosts), err)
	}
	// the saved parameters are not modified
	if len(ovpnParams.OpenVpnParameters.EntryVpnServer.Hosts) != 2 || ovpnParams.OpenVpnParameters.EntryVpnServer.Hosts[0].Host != "10.0.3.1" {
		t.Error("original connection parameters were modified")
	}

	// Free account, latency not known (pinging failed): a random server the account can use
	s = testServiceWithPings(testAccountFree, all, nil)
	for i := 0; i < 50; i++ {
		ret, err := s.useAllowedHosts(ovpnParams)
		if err != nil {
			t.Fatalf("free account (no pings): unexpected error: %v", err)
		}
		ips := hostIPs(ret.OpenVpnParameters.EntryVpnServer.Hosts)
		if len(ips) == 0 {
			t.Fatal("free account (no pings): no hosts chosen")
		}
		for _, ip := range ips {
			if testPremiumIPs[ip] {
				t.Fatalf("free account (no pings): Premium host %s chosen", ip)
			}
		}
	}

	// Free account, no server the account can use: error, the Premium hosts are not used
	premiumOnly := &apiTypes.ServersInfoResponse{OpenvpnServers: []apiTypes.OpenvpnServerInfo{all.OpenvpnServers[2]}}
	if _, err := testServiceWithPings(testAccountFree, premiumOnly, pings).useAllowedHosts(ovpnParams); err == nil {
		t.Error("free account (no usable servers): expected error")
	}
}
