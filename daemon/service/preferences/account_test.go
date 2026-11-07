package preferences

import "testing"

func TestIsCanUsePremiumHosts(t *testing.T) {
	tests := []struct {
		name     string
		account  AccountStatus
		expected bool
	}{
		// status not known (e.g. upgrade from an old version): no restrictions
		{"unknown", AccountStatus{}, true},
		// OvpnPlus panel: Free account has a plan but no "premium" capability
		{"free", AccountStatus{CurrentPlan: "Free", Capabilities: []string{}}, false},
		{"free (other capabilities)", AccountStatus{CurrentPlan: "Free", Capabilities: []string{"multihop"}}, false},
		{"premium", AccountStatus{CurrentPlan: "Premium", Capabilities: []string{"premium"}}, true},
		{"premium (letter case)", AccountStatus{CurrentPlan: "Premium", Capabilities: []string{"Premium"}}, true},
		{"premium (capabilities only)", AccountStatus{Capabilities: []string{"premium"}}, true},
	}

	for _, test := range tests {
		if got := test.account.IsCanUsePremiumHosts(); got != test.expected {
			t.Errorf("%s: IsCanUsePremiumHosts() = %v, expected %v", test.name, got, test.expected)
		}
	}
}
