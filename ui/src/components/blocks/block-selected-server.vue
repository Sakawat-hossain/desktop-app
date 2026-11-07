<template>
  <div id="main">
    <button class="serverCard" v-on:click="showServersList()">
      <ServerFlag :kind="iconKind" :countryCode="countryCode" />

      <span class="texts">
        <span v-if="isExitServer" class="eyebrow">Exit server</span>
        <span class="cardTitle">{{ title }}</span>
        <span v-if="subtitle || isShowIPv6Tag" class="cardSubtitle">
          <span v-if="isShowIPv6Tag" class="ipTag">IPv6</span> {{ subtitle }}
        </span>
      </span>

      <span v-if="pingMs" class="ping" :class="pingQualityClass">
        <span class="pingDot" aria-hidden="true"></span>{{ pingMs }} ms
      </span>

      <svg
        class="chevron"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="m9 6 6 6-6 6" />
      </svg>
    </button>
  </div>
</template>

<script>
import ServerFlag from "@/components/blocks/block-server-flag.vue";
import { IsServerSupportIPv6 } from "@/helpers/helpers_servers";
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
    hostIdText: function () {
      if (!this.serverHostName) return "";
      return this.serverHostName.split(".")[0];
    },
    ispText: function () {
      if (this.$store.state.settings.showISPInfo !== true) return "";
      const h = this.selectedHost;
      if (h && h.isp) return "ISP: " + h.isp;
      return "";
    },
    locationText: function () {
      const s = this.server;
      if (!s) return "";
      return [s.city, s.country].filter((v) => !!v).join(", ");
    },

    title: function () {
      if (this.isFastestServer) return "Fastest server";
      if (this.isRandomServer) return "Random server";
      const s = this.server;
      if (!s) return "Choose a server";
      return s.city || s.country || "Choose a server";
    },
    subtitle: function () {
      if (this.isModeSelected && !this.isShowServerDetails)
        return this.isDisconnected
          ? "Picked when you connect"
          : "Picking a server…"; // connecting: the servers are being pinged
      if (!this.isShowServerDetails) return "";

      const s = this.server;
      // modes: "City, Country"; a chosen server: the city is the title already
      const where = this.isModeSelected
        ? this.locationText
        : s.city
          ? s.country
          : "";
      return [where, this.hostIdText, this.ispText]
        .filter((v) => !!v)
        .join(" · ");
    },
    isShowIPv6Tag: function () {
      return (
        this.isShowServerDetails &&
        this.$store.state.settings.enableIPv6InTunnel && // IPv6 enabled
        this.$store.state.settings.showGatewaysWithoutIPv6 && // both server types are listed
        IsServerSupportIPv6(this.server) === true
      );
    },

    // same source as controls/control-server-ping.vue
    pingMs: function () {
      if (!this.isShowServerDetails) return null;
      const funcGetPing = this.$store.getters["vpnState/funcGetPing"];
      if (!funcGetPing) return null;

      let ping = null;
      // a specific host is selected: show that host's latency
      if (this.selectedHost) ping = funcGetPing(this.selectedHost);
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

#main {
  margin: 0 16px;
}

.serverCard {
  box-sizing: border-box;
  width: 100%;
  height: 60px;
  padding: 0 12px;
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
  font-size: 15px;
  font-weight: 600;
  line-height: 20px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cardSubtitle {
  font-size: 12px;
  line-height: 16px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

// followed by a real space, so the button's name reads "IPv6 Bangladesh"
.ipTag {
  display: inline-block;
  margin-right: 2px;
  padding: 0 4px;
  border: 1px solid var(--surface-border);
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  line-height: 13px;
  color: var(--text-muted);
  vertical-align: 1px;
}

.ping {
  flex: none;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 7px;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 600;
  line-height: 16px;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.pingDot {
  width: 6px;
  height: 6px;
  flex: none;
  border-radius: 50%;
}

.pingGood {
  background: var(--good-background);
  color: var(--good-text);
}
.pingGood .pingDot {
  background: var(--good-text);
}

.pingModerate {
  background: var(--accent-tint);
  color: var(--link-color);
}
.pingModerate .pingDot {
  background: var(--accent-color);
}

.pingBad {
  background: var(--neutral-tint);
  color: var(--danger-text);
}
.pingBad .pingDot {
  background: var(--danger-dot);
}

// The global "html * { color }" rule stops currentColor from inheriting,
// so the stroke colour is set here directly.
.chevron {
  flex: none;
  fill: none;
  stroke: var(--text-faint);
}
</style>
