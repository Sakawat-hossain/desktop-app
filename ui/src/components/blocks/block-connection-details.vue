<template>
  <!-- One card of 48 px rows; the dividers come from '.detailsCard > * + *' -->
  <div class="detailsCard">
    <!-- FIREWALL (kill switch) -->
    <OnOffButtonControl
      v-bind:class="{ lowOpacity: IsPaused }"
      text="Kill switch"
      :onTextClick="onShowFirewallConfig"
      textClickTooltip="Firewall settings"
      description="Block internet if VPN drops"
      :onChecked="firewallOnChecked"
      :isChecked="this.$store.state.vpnState.firewallState.IsEnabled"
      :switcherOpacity="
        this.$store.getters['vpnState/isInverseSplitTunnel'] ? 0.4 : 1
      "
      :checkedColor="
        this.$store.state.vpnState.firewallState.IsPersistent
          ? '#77152a77'
          : null
      "
      :isProgress="firewallIsProgress"
    >
      <template #icon>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3 4 6v6c0 4.5 3.4 8.2 8 9 4.6-.8 8-4.5 8-9V6z" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      </template>
    </OnOffButtonControl>

    <!-- ANTITRACKER -->
    <OnOffButtonControl
      v-if="features.AntiTracker"
      v-bind:class="{ lowOpacity: PrioritizedDNS != null }"
      text="AntiTracker"
      :onTextClick="onShowAntiTrackerConfig"
      :textClickTooltip="`AntiTracker settings` + (PrioritizedDNS ? `\n\nNote: ${PrioritizedDNS.Description}` : '')"
      description="Block trackers whilst connected to VPN"
      :onChecked="PrioritizedDNS ? onShowAntiTrackerConfig: antitrackerOnChecked"
      :isChecked="PrioritizedDNS ? false : this.$store.state.settings.antiTracker?.Enabled"
      :switcherOpacity="
        !IsConnected ||
        this.$store.getters['vpnState/isInverseSplitTunnelAnyDns']
          ? 0.4
          : 1
      "
      :checkedColor="
        this.$store.state.settings.antiTracker?.Hardcore ? '#77152a' : null
      "
      :isProgress="antitrackerIsProgress"
    >
      <template #icon>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 3l18 18" />
          <path d="M10.6 5.1A9.6 9.6 0 0 1 12 5c5 0 9 4.5 10 7-.5 1.2-1.3 2.5-2.4 3.6M6.6 6.6C4.4 8 2.8 10 2 12c1 2.5 5 7 10 7 1.9 0 3.6-.6 5-1.5" />
          <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
        </svg>
      </template>
    </OnOffButtonControl>

    <!-- PROTOCOL -->
    <SelectButtonControl
      :click="onShowPorts"
      text="Protocol"
      v-bind:description="portProtocolText"
      title="Connection settings"
    >
      <template #icon>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 12h16M4 6h16M4 18h10" />
        </svg>
      </template>
    </SelectButtonControl>

    <!-- SPLIT TUNNEL -->
    <transition name="fade">
      <SplitTunnelControl
        v-if="isLinux && IsSplitTunnelEnabled"
        class="leftPanelBlock"
      />
    </transition>

    <!-- WIFI -->
    <transition name="fade">
      <SelectButtonControl
        v-if="
          wifiSSID &&
          (isTrustedNetworksControlActive || isConnectVPNOnInsecureNetwork)
        "
        :click="onShowWifiConfig"
        text="Wi-Fi network"
        :description="wifiSSID"
        :markerText="WiFiMarkerText"
        :markerColor="WiFiMarkerColor"
        :markerTextColor="'var(--text-color-details)'"
        title="Wi-Fi control settings"
      >
        <template #icon>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2.5 8.8a14 14 0 0 1 19 0" />
            <path d="M5.6 12.2a9.5 9.5 0 0 1 12.8 0" />
            <path d="M8.8 15.5a5 5 0 0 1 6.4 0" />
            <path d="M12 19.2h.01" stroke-width="2.6" />
          </svg>
        </template>
      </SelectButtonControl>
    </transition>
  </div>
</template>

<script>
import { Platform, PlatformEnum } from "@/platform/platform";

import OnOffButtonControl from "@/components/controls/control-config-on-off-button.vue";
import SelectButtonControl from "@/components/controls/control-config-to-select-button.vue";
import SplitTunnelControl from "@/components/controls/control-split-tunnel.vue";

const sender = window.ipcSender;
import { enumValueName } from "@/helpers/helpers";
import { VpnTypeEnum, PortTypeEnum, VpnStateEnum } from "@/store/types";
import config from "@/config";

function processError(e) {
  console.error(e);
  sender.showMessageBox({
    type: "error",
    buttons: ["OK"],
    message: e.toString(),
  });
}

export default {
  components: {
    OnOffButtonControl,
    SelectButtonControl,
    SplitTunnelControl,
  },
  props: [
    "onShowPorts",
    "onShowWifiConfig",
    "onShowFirewallConfig",
    "onShowAntiTrackerConfig",
  ],
  data: function () {
    return {
      antitrackerIsProgress: false,
      firewallIsProgress: false,
    };
  },

  computed: {
    features() {
      return config.Features;
    },
    portProtocolText: function () {
      let port = this.$store.getters["settings/getPort"];
      let protocol = this.$store.getters["settings/vpnType"];
      const isMH = this.$store.state.settings.isMultiHop;
      const isV2Ray = !!this.$store.getters["settings/getV2RayConfig"];
      const isObfsProxy =
        this.$store.getters["settings/isConnectionUseObfsproxy"];
      const vpnName = enumValueName(VpnTypeEnum, protocol);
      const portType = enumValueName(PortTypeEnum, port.type);
      if (!isV2Ray && (isMH === true || isObfsProxy)) {
        // do not show port number for multi-hop connections
        return `${vpnName} · ${portType}`;
      }
      return `${vpnName} · ${portType} ${port.port}`;
    },
    isTrustedNetworksControlActive() {
      let wifiSettings = this.$store.state.settings.daemonSettings.WiFi;
      if (wifiSettings == null) return false;
      return wifiSettings.trustedNetworksControl;
    },
    isConnectVPNOnInsecureNetwork: function () {
      let wifiSettings = this.$store.state.settings.daemonSettings.WiFi;
      if (wifiSettings == null) return false;
      return wifiSettings.connectVPNOnInsecureNetwork;
    },
    defaultTrustForUndefinedNetworks() {
      let wifiSettings = this.$store.state.settings.daemonSettings.WiFi;
      if (wifiSettings == null) return null;
      return wifiSettings.defaultTrustStatusTrusted;
    },
    wifiSSID() {
      const currWifi = this.$store.state.vpnState.currentWiFiInfo;
      if (currWifi == null || currWifi.SSID == null) return "";
      return currWifi.SSID;
    },
    WiFiMarkerText: function () {
      if (this.wifiSSID == "") return null;
      const TRUSTED = "TRUSTED";
      const UNTRUSTED = "UNTRUSTED";
      const INSECURE = "INSECURE";
      const NOTRUSTSTATUS = "NO TRUST STATUS";
      const trustState = this.getTrustInfoForCurrentWifi();
      if (trustState.isTrusted == true) return TRUSTED;
      else if (trustState.isTrusted == false) return UNTRUSTED;
      else if (trustState.isInsecure == true) return INSECURE;
      if (this.isTrustedNetworksControlActive == true) return NOTRUSTSTATUS;
      return null;
    },
    WiFiMarkerColor: function () {
      if (this.wifiSSID == "") return null;
      const TRUSTED = "#64ad07";
      const UNTRUSTED = "var(--warning-color)";
      const INSECURE = "darkorange";
      const NOTRUSTSTATUS = "var(--background-color-alternate)"; //"#BBBBBB";
      const trustState = this.getTrustInfoForCurrentWifi();

      if (trustState.isTrusted == true) return TRUSTED;
      else if (trustState.isTrusted == false) return UNTRUSTED;
      else if (trustState.isInsecure == true) return INSECURE;
      if (this.isTrustedNetworksControlActive == true) return NOTRUSTSTATUS;
      return NOTRUSTSTATUS;
    },
    IsPaused: function () {
      return this.$store.getters["vpnState/isPaused"];
    },
    IsConnected: function () {
      return (
        this.$store.state.vpnState.connectionState === VpnStateEnum.CONNECTED
      );
    },
    isLinux: function () {
      return Platform() === PlatformEnum.Linux;
    },
    IsSplitTunnelEnabled: function () {
      return this.$store.state.vpnState.splitTunnelling?.IsEnabled;
    },
    PrioritizedDNS: function () {
      return this.$store.getters["settings/getPrioritizedDNS"];
    },
  },

  methods: {
    async antitrackerOnChecked(antitrackerIsEnabled) {
      try {
        this.antitrackerIsProgress = true;

        let at = this.$store.state.settings.antiTracker;
        if (!at)
          at = {
            Enabled: antitrackerIsEnabled,
            Hardcore: false,
            AntiTrackerBlockListName: "",
          };
        else at = JSON.parse(JSON.stringify(at));
        at.Enabled = antitrackerIsEnabled;

        this.$store.dispatch("settings/antiTracker", at);
        await sender.SetDNS();
      } catch (e) {
        processError(e);
      } finally {
        this.antitrackerIsProgress = false;
      }
    },
    async firewallOnChecked(isEnabled) {
      try {
        this.firewallIsProgress = true;
        await sender.EnableFirewall(isEnabled);
      } catch (e) {
        processError(e);
      } finally {
        this.firewallIsProgress = false;
      }
    },
    getCurrentWiFiConfig() {
      let curWifiInfo = this.$store.state.vpnState.currentWiFiInfo;
      if (curWifiInfo == null || curWifiInfo.SSID == "") return null;

      let wifiSettings = this.$store.state.settings.daemonSettings.WiFi;
      if (wifiSettings == null || wifiSettings.networks == null) return null;

      for (let w of wifiSettings.networks) {
        if (w.ssid == curWifiInfo.SSID) return w;
      }
    },
    getTrustInfoForCurrentWifi() {
      let ret = { isTrusted: null, isInsecure: null };
      if (this.isTrustedNetworksControlActive) {
        let currentNetworkConfig = this.getCurrentWiFiConfig();
        if (currentNetworkConfig != null)
          ret.isTrusted = currentNetworkConfig.isTrusted;
        else if (this.defaultTrustForUndefinedNetworks != null)
          ret.isTrusted = this.defaultTrustForUndefinedNetworks;
      }

      if (ret.isTrusted == null) {
        let curWifiInfo = this.$store.state.vpnState.currentWiFiInfo;
        if (curWifiInfo != null && curWifiInfo.IsInsecureNetwork)
          ret.isInsecure = true;
      }
      return ret;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

// the row icons come from this template (slots): the global 'html *' rule
// gives them the text colour, so let them take the colour the row sets
svg,
svg * {
  color: inherit;
}

// side margins 16 px; the 8 px gaps above/below come from Component-Control
.detailsCard {
  flex: none;
  margin: 0 16px;
  border: 1px solid var(--surface-border);
  border-radius: 14px;
  background: var(--surface-color);
  overflow: hidden;
}
.detailsCard > * + * {
  border-top: 1px solid var(--surface-divider);
}

// Split Tunnel row (Linux), same height as the other rows
.leftPanelBlock {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 48px;
  box-sizing: border-box;
  padding: 6px 14px;
}

.lowOpacity {
  opacity: 0.5;
}
</style>
