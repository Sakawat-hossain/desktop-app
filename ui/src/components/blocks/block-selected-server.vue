<template>
  <div id="main">
    <button class="serverCard" v-on:click="showServersList()">
      <ServerFlag
        :kind="iconKind"
        :countryCode="countryCode"
        :badgeCountryCode="badgeCountryCode"
        :width="42"
        :height="30"
      />

      <span class="texts">
        <span v-if="isExitServer" class="eyebrow">Exit server</span>
        <span class="cardTitle">{{ title }}</span>
        <span v-if="isShowSubline" class="cardSubline">
          <span v-if="isShowIPv6Tag" class="ipTag">IPv6</span>
          <span v-if="subtitle" class="cardSubtitle">{{ subtitle }}</span>
          <span v-if="pingMs" class="ping" :class="pingQualityClass">
            <span class="pingDot" aria-hidden="true"></span>{{ pingMs }} ms
          </span>
        </span>
      </span>

      <span class="side">
        <span v-if="tier" class="tierChips" :title="tierTitle">
          <span v-if="tier !== 'Premium'" class="tierChip tierFree">Free</span>
          <span
            v-if="tier !== 'Free'"
            class="tierChip tierPremium"
            :class="{ crownOnly: tier === 'Mixed' }"
          >
            <svg
              class="crown"
              width="10"
              height="10"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M2.8 7.6 7.7 11.6 12 4.6 16.3 11.6 21.2 7.6 19.3 17.2H4.7z"
                fill="currentColor"
              />
              <rect
                x="4.7"
                y="18.8"
                width="14.6"
                height="2.6"
                rx="1.3"
                fill="currentColor"
              />
            </svg>
            <span :class="{ srOnly: tier === 'Mixed' }">Premium</span>
          </span>
        </span>

        <span class="changePill">
          Change
          <svg
            class="changeChevron"
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.4"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="m9 6 6 6-6 6" />
          </svg>
        </span>
      </span>
    </button>
  </div>
</template>

<script>
import ServerFlag from "@/components/blocks/block-server-flag.vue";
import { IsServerSupportIPv6 } from "@/helpers/helpers_servers";
import {
  ServerTier,
  HostDisplayName,
  IsHostPremium,
  IsServerPremium,
} from "@/helpers/helpers_premium";
import { VpnStateEnum } from "@/store/types";

export default {
  props: ["onShowServersPressed", "isExitServer"],
  components: {
    ServerFlag,
  },
  computed: {
    server: function () {
      return this.isExitServer
        ? this.$store.state.settings.serverExit
        : this.$store.state.settings.serverEntry;
    },
    serverHostName: function () {
      return this.isExitServer
        ? this.$store.state.settings.serverExitHostId
        : this.$store.state.settings.serverEntryHostId;
    },
    isConnected: function () {
      return (
        this.$store.state.vpnState.connectionState === VpnStateEnum.CONNECTED
      );
    },
    isDisconnected: function () {
      return (
        this.$store.state.vpnState.connectionState === VpnStateEnum.DISCONNECTED
      );
    },

    // "Fastest server" mode is selected (entry server only; never in multi-hop)
    isFastestServer: function () {
      if (this.isExitServer) return false;
      return this.$store.getters["settings/isFastestServer"] === true;
    },
    // "Random server" mode is selected for this hop
    isRandomServer: function () {
      if (this.isFastestServer) return false;
      return (
        (this.isExitServer
          ? this.$store.getters["settings/isRandomExitServer"]
          : this.$store.getters["settings/isRandomServer"]) === true
      );
    },
    isModeSelected: function () {
      return this.isFastestServer || this.isRandomServer;
    },
    // In the Fastest/Random modes the real server is picked on connect.
    // The selected server in settings is the one in use only while a
    // connection exists and the pick is not still being made (pinging).
    isServerInUseKnown: function () {
      if (this.isDisconnected) return false;
      if (
        !this.isConnected &&
        this.$store.state.vpnState.isPingingServers === true
      )
        return false;
      return this.server != null;
    },
    // the card shows a concrete server (its location, host and ping)
    isShowServerDetails: function () {
      if (!this.server) return false;
      return !this.isModeSelected || this.isServerInUseKnown;
    },

    iconKind: function () {
      if (this.isFastestServer) return "fastest";
      if (this.isRandomServer) return "random";
      return "flag";
    },
    countryCode: function () {
      return this.server ? this.server.country_code : null;
    },
    // Fastest/Random: the flag of the server in use, on the mode tile
    badgeCountryCode: function () {
      if (!this.isModeSelected || !this.isShowServerDetails) return null;
      return this.countryCode;
    },

    // the host chosen in the server list (null: the whole location)
    selectedHost: function () {
      if (!this.serverHostName || !this.server || !this.server.hosts)
        return null;
      const hostId = this.serverHostName.split(".")[0];
      if (!hostId) return null;
      return (
        this.server.hosts.find(
          (h) => h && h.hostname && h.hostname.startsWith(hostId + "."),
        ) || null
      );
    },
    // the host the tunnel is connected to, as the daemon reports it
    connectedHost: function () {
      if (!this.isConnected) return null;
      const s = this.server;
      const ci = this.$store.state.vpnState.connectionInfo;
      if (!s || !Array.isArray(s.hosts) || !ci) return null;
      if (this.isExitServer) {
        if (!ci.ExitHostname) return null;
        return s.hosts.find((h) => h && h.hostname === ci.ExitHostname) || null;
      }
      if (!ci.ServerIP) return null;
      return s.hosts.find((h) => h && h.host === ci.ServerIP) || null;
    },
    // the host whose tier and ping the card shows, when one is known
    shownHost: function () {
      return this.selectedHost || this.connectedHost;
    },
    ispText: function () {
      if (this.$store.state.settings.showISPInfo !== true) return "";
      const h = this.shownHost;
      if (h && h.isp) return "ISP: " + h.isp;
      return "";
    },

    title: function () {
      if (this.isFastestServer) return "Fastest server";
      if (this.isRandomServer) return "Random server";
      const s = this.server;
      if (!s) return "Choose a server";
      // a host the user chose in the list: its name ("Dhaka District #1"), never its address;
      // a host the app picked itself (Free account on a mixed location) keeps the location name
      const isAutoHost = this.isExitServer
        ? this.$store.state.settings.serverExitHostIsAuto === true
        : this.$store.state.settings.serverEntryHostIsAuto === true;
      if (this.selectedHost && !isAutoHost) return HostDisplayName(s, this.selectedHost);
      return s.city || s.country || "Choose a server";
    },
    subtitle: function () {
      if (this.isModeSelected && !this.isShowServerDetails)
        return this.isDisconnected
          ? "Picked when you connect"
          : "Picking a server…"; // connecting: the servers are being pinged
      if (!this.isShowServerDetails) return "";

      const s = this.server;
      // modes: the city in use (its flag is on the tile);
      // a chosen server: the city is the title already, so the country
      // (not repeated for a city-state: "Singapore", "Hong Kong")
      const isCityState =
        !!s.city &&
        !!s.country &&
        s.city.trim().toLowerCase() === s.country.trim().toLowerCase();
      const where = this.isModeSelected
        ? s.city || s.country
        : s.city && !isCityState
          ? s.country
          : "";
      return [where, this.ispText].filter((v) => !!v).join(" · ");
    },
    isShowIPv6Tag: function () {
      return (
        this.isShowServerDetails &&
        this.$store.state.settings.enableIPv6InTunnel && // IPv6 enabled
        this.$store.state.settings.showGatewaysWithoutIPv6 && // both server types are listed
        IsServerSupportIPv6(this.server) === true
      );
    },
    isShowSubline: function () {
      return !!this.subtitle || this.isShowIPv6Tag || !!this.pingMs;
    },

    // same source as controls/control-server-ping.vue
    pingMs: function () {
      if (!this.isShowServerDetails) return null;
      const funcGetPing = this.$store.getters["vpnState/funcGetPing"];
      if (!funcGetPing) return null;

      let ping = null;
      // a specific host is selected or in use: show that host's latency
      if (this.shownHost) ping = funcGetPing(this.shownHost);
      if (!(ping > 0)) ping = funcGetPing(this.server);
      if (!(ping > 0)) return null;
      return Math.max(1, Math.round(ping));
    },
    pingQualityClass: function () {
      const p = this.pingMs;
      if (p == null) return "";
      if (p < 100) return "pingGood";
      if (p < 300) return "pingModerate";
      return "pingBad";
    },

    // "Free" | "Premium" | "Mixed" (a location with both kinds of hosts);
    // a chosen or connected host shows its own tier.
    // The daemon leaves "is_premium" out when it is false (omitempty), so a
    // Free host has no such field at all: never fall back to the location's
    // "Mixed" for a known host.
    tier: function () {
      if (!this.isShowServerDetails) return null;
      const h = this.shownHost;
      if (h)
        return IsHostPremium(h) || IsServerPremium(this.server)
          ? "Premium"
          : "Free";
      return ServerTier(this.server);
    },
    tierTitle: function () {
      if (this.tier === "Premium") return "Premium server";
      if (this.tier === "Mixed") return "Free and Premium servers";
      return "Free server";
    },
  },
  methods: {
    showServersList() {
      if (this.onShowServersPressed != null)
        this.onShowServersPressed(this.isExitServer);
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

// the global 'html *' rule gives every element the text colour:
// let the icons take the colour of the text they sit in
svg,
svg * {
  color: inherit;
}

#main {
  margin: 0 16px;
}

.serverCard {
  // colours only this card uses (light theme; dark values below)
  --card-free-border: #bfe3cb;
  --card-ping-moderate: #b45309;

  box-sizing: border-box;
  width: 100%;
  height: 60px;
  margin: 0;
  padding: 0 9px 0 10px;
  border: 1px solid var(--surface-border);
  border-radius: 14px;
  background-color: var(--surface-color);
  outline-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s;
}
@media (prefers-color-scheme: dark) {
  .serverCard {
    --card-free-border: #1f3d2a;
    --card-ping-moderate: #fdba74;
  }
}
.serverCard:hover {
  border-color: var(--accent-color);
}
// offset 1px: the ring then reaches 3px outside the card, which is exactly
// the room the scrolling cards box in Component-Control leaves at its top
.serverCard:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 1px;
}

.texts {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.eyebrow {
  font-size: 10.5px;
  font-weight: 600;
  line-height: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-faint);
  white-space: nowrap;
}

// not ".title": App.vue has a global ".title" rule (the window drag strip)
.cardTitle {
  display: block;
  min-width: 0;
  font-size: 15px;
  font-weight: 600;
  line-height: 20px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

// "Bangladesh ● 42 ms": the country gives way, the ping never does
.cardSubline {
  min-width: 0;
  height: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  line-height: 16px;
  white-space: nowrap;
}
.cardSubtitle {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-muted);
}

.ipTag {
  flex: none;
  box-sizing: border-box;
  height: 15px;
  padding: 0 4px;
  border: 1px solid var(--surface-border);
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  line-height: 13px;
  color: var(--text-muted);
}

.ping {
  flex: none;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.pingDot {
  width: 6px;
  height: 6px;
  flex: none;
  border-radius: 50%;
}
.pingGood {
  color: var(--good-text);
}
.pingGood .pingDot {
  background: var(--good-text);
}
.pingModerate {
  color: var(--card-ping-moderate);
}
.pingModerate .pingDot {
  background: var(--card-ping-moderate);
}
.pingBad {
  color: var(--danger-text);
}
.pingBad .pingDot {
  background: var(--danger-text);
}

// right column: the server's tier above the "Change" pill
.side {
  flex: none;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.tierChips {
  display: flex;
  align-items: center;
  gap: 3px;
}
.tierChip {
  position: relative;
  flex: none;
  box-sizing: border-box;
  height: 16px;
  padding: 0 5px;
  border: 1px solid;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
  line-height: 14px;
  letter-spacing: 0.02em;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 2px;
}
.tierChip > span {
  color: inherit;
}
.tierFree {
  border-color: var(--card-free-border);
  background: var(--good-background);
  color: var(--good-text);
}
.tierPremium {
  padding-left: 3px;
  border-color: var(--accent-ring);
  background: var(--accent-tint);
  color: var(--link-color);
}
// a location with Free and Premium hosts: "Free" + a crown-only chip
.tierPremium.crownOnly {
  width: 16px;
  padding: 0;
  justify-content: center;
}
.crown {
  display: block;
  flex: none;
}
.srOnly {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}

// part of the card button (one hit target), drawn as the card's action
.changePill {
  flex: none;
  box-sizing: border-box;
  height: 28px;
  padding: 0 5px 0 8px;
  border: 1px solid var(--accent-ring);
  border-radius: 8px;
  background: var(--accent-tint);
  color: var(--link-color);
  font-size: 12px;
  font-weight: 600;
  line-height: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 1px;
}
.changeChevron {
  display: block;
  flex: none;
}
</style>
