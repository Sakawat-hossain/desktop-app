<template>
  <div class="mapPopup" v-on:click="onMouseClick">
    <div v-if="isTheCurrentLocation" class="popupCaption">
      Your current location
    </div>
    <div v-if="isExitServerCountrySameAsEntry" class="popupNote">
      When using multihop you must select entry and exit servers in different
      countries. Please select a different entry or exit server.
    </div>

    <div class="popupPlace">
      <span v-if="countryCode" class="flagBox">
        <MapFlag :countryCode="countryCode" />
      </span>
      <span class="popupName">{{ placeName }}</span>
      <span v-if="pingMs" class="popupPing" :class="pingClass">
        <span class="pingDot" aria-hidden="true"></span>{{ pingMs }} ms
      </span>
    </div>

    <button
      class="popupBtn popupBtnPrimary"
      v-if="isCanConnect"
      v-on:click="onConnect(location)"
    >
      Connect to server
    </button>
    <button class="popupBtn" v-if="isCanDisconnect" v-on:click="onDisconnect">
      Disconnect
    </button>

    <div v-if="isPaused && pauseTimeLeftText" class="popupPause">
      <div class="popupNote">Connection will resume automatically in</div>
      <div class="popupPauseTime">
        {{ pauseTimeLeftText }}
      </div>

      <!--
      <button class="popupBtn popupBtnPrimary" v-on:click="onResume()">
        Resume
      </button>
      -->
    </div>
  </div>
</template>

<script>
import MapFlag from "@/components/map/map-flag.vue";
import { VpnStateEnum } from "@/store/types";
import { GetTimeLeftText } from "@/helpers/renderer";

export default {
  props: ["location", "onConnect", "onDisconnect", "onMouseClick", "onResume"],
  components: {
    MapFlag,
  },
  data: () => ({
    pauseTimeUpdateTimer: null,
    pauseTimeLeftText: "",
  }),
  mounted() {
    this.startPauseTimer();
  },
  unmounted() {
    if (this.pauseTimeUpdateTimer) {
      clearInterval(this.pauseTimeUpdateTimer);
      this.pauseTimeUpdateTimer = null;
    }
  },
  computed: {
    // needed for watcher
    pauseConnectionTill: function () {
      return this.$store.state.vpnState?.connectionInfo?.PausedTill;
    },
    isPaused: function () {
      return this.$store.getters["vpnState/isPaused"];
    },
    isTheCurrentLocation: function () {
      return (
        this.location === this.$store.state.location ||
        this.location === this.$store.state.locationIPv6
      );
    },

    isExitServerCountrySameAsEntry: function () {
      if (this.location == null || this.location.gateway == null) return false;
      return (
        this.$store.state.settings.isMultiHop &&
        this.location.country_code ===
          this.$store.state.settings.serverEntry.country_code
      );
    },

    isCanDisconnect() {
      if (this.$store.state.vpnState.connectionState !== VpnStateEnum.CONNECTED)
        return false;
      if (this.location == null || this.location.gateway == null) return false;

      if (
        (this.$store.state.settings.isMultiHop &&
          this.location.country_code ===
            this.$store.state.settings.serverExit.country_code) ||
        (this.$store.state.settings.isMultiHop == false &&
          this.location.country_code ===
            this.$store.state.settings.serverEntry.country_code)
      )
        return true;

      return false;
    },

    isCanConnect: function () {
      // selected curent users location (not a server)
      if (this.isTheCurrentLocation) return false;
      // not allowed multi-hop connect for servers in same country
      if (this.isExitServerCountrySameAsEntry) return false;
      if (this.isCanDisconnect) return false;
      if (this.location != null && this.location.gateway == null) return false;
      return true;
    },

    isAllowedExitServer: function () {
      if (this.$store.state.settings.isMultiHop === false) return true;
      if (this.location == null) return true;

      if (
        this.location.country_code ===
        this.$store.state.settings.serverExit.country_code
      )
        return false;
      return true;
    },

    countryCode: function () {
      const l = this.location;
      if (!l || !l.country_code) return null;
      return String(l.country_code).toUpperCase();
    },
    // "City, Country" (as the old full-name server label)
    placeName: function () {
      const l = this.location;
      if (!l) return "";
      if (!l.city && !l.country) return "";
      if (!l.city) return l.country;
      if (!l.country) return l.city;
      return `${l.city}, ${l.country}`;
    },
    // latency of a server (the user's own location has none)
    pingMs: function () {
      const l = this.location;
      if (!l || !l.gateway) return null;
      const funcGetPing = this.$store.getters["vpnState/funcGetPing"];
      if (typeof funcGetPing !== "function") return null;
      const p = funcGetPing(l);
      if (!(p > 0)) return null;
      return Math.round(p);
    },
    // same thresholds as the server list (control-server-ping.vue)
    pingClass: function () {
      const p = this.pingMs;
      if (p == null) return "";
      if (p < 100) return "pingGood";
      if (p < 300) return "pingModerate";
      return "pingBad";
    },
  },
  watch: {
    isPaused() {
      this.startPauseTimer();
    },
  },
  methods: {
    startPauseTimer() {
      if (this.pauseTimeUpdateTimer) return;
      if (!this.pauseConnectionTill) return;

      this.pauseTimeUpdateTimer = setInterval(() => {
        this.pauseTimeLeftText = GetTimeLeftText(this.pauseConnectionTill);

        if (!this.isPaused) {
          clearInterval(this.pauseTimeUpdateTimer);
          this.pauseTimeUpdateTimer = null;
        }
      }, 1000);

      this.pauseTimeLeftText = GetTimeLeftText(this.pauseConnectionTill);
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

// Content of the map popup (the card around it is drawn by Component-Map).
// NOTE: every element gets an explicit colour because App.vue sets "html * { color }" for all elements.
.mapPopup {
  // light theme; the dark value is below
  --popup-ping-moderate: #b45309;

  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
}
@media (prefers-color-scheme: dark) {
  .mapPopup {
    --popup-ping-moderate: #fdba74;
  }
}

.popupCaption {
  font-size: 11px;
  font-weight: 600;
  line-height: 14px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-faint);
}
.popupNote {
  font-size: 12px;
  line-height: 16px;
  color: var(--text-muted);
}

.popupPlace {
  min-width: 0;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
// as tall as one text line: the flag sits in the middle of the first line
.flagBox {
  flex: none;
  height: 20px;
  display: flex;
  align-items: center;
}
.popupName {
  flex: 1;
  min-width: 0;
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  overflow-wrap: anywhere;
  color: var(--text-color);
}
.popupPing {
  flex: none;
  height: 20px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  line-height: 16px;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  color: var(--text-muted);
}
.pingDot {
  width: 6px;
  height: 6px;
  flex: none;
  border-radius: 50%;
  background: var(--text-muted);
}
.pingGood {
  color: var(--good-text);
}
.pingGood .pingDot {
  background: var(--good-text);
}
.pingModerate {
  color: var(--popup-ping-moderate);
}
.pingModerate .pingDot {
  background: var(--popup-ping-moderate);
}
.pingBad {
  color: var(--danger-text);
}
.pingBad .pingDot {
  background: var(--danger-text);
}

// Connect (gold) / Disconnect (neutral): 32 px tall, full width
button.popupBtn {
  width: 100%;
  height: 32px;
  margin-top: 4px;
  padding: 0 12px;
  box-sizing: border-box;
  border: 1px solid var(--control-border, var(--surface-border));
  border-radius: 8px;
  background: var(--neutral-tint);
  color: var(--text-color);
  font-size: 13px;
  font-weight: 600;
  line-height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
button.popupBtn:hover {
  border-color: var(--accent-color);
}
button.popupBtnPrimary {
  border-color: var(--accent-color);
  background: var(--accent-color);
  color: var(--accent-text-color);
}
button.popupBtnPrimary:hover {
  border-color: var(--accent-color-hover);
  background: var(--accent-color-hover);
}
button.popupBtn:focus {
  outline: none;
}
button.popupBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}

.popupPause {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.popupPauseTime {
  font-size: 16px;
  font-weight: 600;
  line-height: 20px;
  font-variant-numeric: tabular-nums;
  color: var(--text-color);
}
</style>
