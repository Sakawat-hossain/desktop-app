<template>
  <div class="geoInfo">
    <!-- IP row: the address, or the loading / failed status -->
    <div class="ipRow">
      <div class="ipCell">
        <div class="labelRow">
          <span class="infoLabel">IP ADDRESS</span>

          <template v-if="isInfoShown">
            <!-- IPv4 / IPv6 switch (only when both addresses are known) -->
            <div
              v-if="isInfoAvailableIPv4 && isInfoAvailableIPv6"
              class="ipToggle"
              role="group"
              aria-label="IP version"
            >
              <button
                class="ipToggleBtn"
                v-bind:class="{ ipToggleBtnSelected: !isIPv6View }"
                v-bind:aria-pressed="!isIPv6View ? 'true' : 'false'"
                v-on:click="onIPv4View"
              >
                IPv4
              </button>
              <button
                class="ipToggleBtn"
                v-bind:class="{ ipToggleBtnSelected: isIPv6View }"
                v-bind:aria-pressed="isIPv6View ? 'true' : 'false'"
                v-on:click="onIPv6View"
              >
                IPv6
              </button>
            </div>
            <span v-else-if="ipVersion" class="ipTag">{{ ipVersion }}</span>

            <span
              v-if="
                isInfoAvailableIPv4 &&
                isInfoAvailableIPv6 &&
                !isIPv4andIPv6LocationsEqual
              "
              class="mismatchText"
            >
              Location does not match
            </span>
          </template>
        </div>

        <!-- Loading connection info ... -->
        <div v-if="isLoading" class="statusText">Loading connection info ...</div>
        <!-- Failed to load connection info -->
        <div v-else-if="!isInfoShown" class="statusText">
          Failed to load connection info
        </div>
        <div v-else class="ipValueRow">
          <span
            class="ipValue"
            v-bind:class="{ ipHidden: isIpHidden }"
            :aria-hidden="isIpHidden ? 'true' : null"
            >{{ ip || "Unknown" }}</span
          >
          <span v-if="isIpHidden" class="visuallyHidden">IP address hidden</span>
          <button
            v-if="ip"
            class="eyeBtn"
            v-on:click="onToggleIp"
            :aria-label="isIpHidden ? 'Show IP address' : 'Hide IP address'"
            :title="isIpHidden ? 'Show IP address' : 'Hide IP address'"
            :aria-pressed="isIpHidden ? 'false' : 'true'"
          >
            <!-- eye: the IP is hidden, click to show it -->
            <svg
              v-if="isIpHidden"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            <!-- eye crossed out: the IP is shown, click to hide it -->
            <svg
              v-else
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M10.6 5.1A10.6 10.6 0 0 1 12 5c6.4 0 10 7 10 7a17.7 17.7 0 0 1-2.6 3.6" />
              <path d="M6.6 6.6C3.9 8.4 2 12 2 12s3.6 7 10 7a9.7 9.7 0 0 0 5.4-1.6" />
              <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
              <path d="M3 3l18 18" />
            </svg>
          </button>
        </div>
      </div>

      <button
        v-if="!isLoading"
        class="refreshBtn"
        v-on:click="onRefreshCurrLocation"
        aria-label="Refresh IP address"
        title="Refresh IP address"
      >
        <svg
          class="refreshIcon"
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill="none"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M20 12a8 8 0 1 1-2.34-5.66L20 8.5" />
          <path d="M20 3.5v5h-5" />
        </svg>
      </button>
    </div>

    <div class="cardDivider" aria-hidden="true"></div>

    <!-- LOCATION / PROVIDER: always shown, so the card keeps its height while the info loads -->
    <div class="detailsGrid">
      <div class="infoCell">
        <span class="infoLabel">LOCATION</span>
        <span v-if="!isInfoShown" class="infoValue noValue">—</span>
        <span v-else class="infoValue locationValue">
          <!-- 21 x 15 rectangular flag, centred on the first 20 px text line -->
          <span v-if="countryCode" class="flagBox">
            <MapFlag :countryCode="countryCode" />
          </span>
          <span class="valueText">{{ locationName || "Unknown" }}</span>
        </span>
      </div>
      <div class="infoCell providerCell">
        <span class="infoLabel">PROVIDER</span>
        <span v-if="!isInfoShown" class="infoValue noValue">—</span>
        <span
          v-else
          class="infoValue valueText"
          v-bind:class="{ infoAccent: isOvpnPlusProvider }"
        >
          {{ isp || "Unknown" }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import MapFlag from "@/components/map/map-flag.vue";

const sender = window.ipcSender;

export default {
  components: { MapFlag },
  methods: {
    onToggleIp() {
      this.$store.dispatch("uiState/isMapIpShown", !this.$store.state.uiState.isMapIpShown);
    },
    onRefreshCurrLocation() {
      try {
        sender.GeoLookup();
      } catch (e) {
        console.error(e);
      }
    },
    onIPv4View() {
      this.$store.dispatch("uiState/isIPv6View", false);
    },
    onIPv6View() {
      this.$store.dispatch("uiState/isIPv6View", true);
    },
  },
  computed: {
    isIpHidden() {
      return this.$store.state.uiState.isMapIpShown !== true;
    },
    isIPv6View: function () {
      return this.$store.getters["getIsIPv6View"];
    },
    isIPv4andIPv6LocationsEqual: function () {
      return this.$store.getters["isIPv4andIPv6LocationsEqual"];
    },
    isInfoAvailableIPv4: function () {
      return this.$store.getters["getIsInfoAvailableIPv4"];
    },
    isInfoAvailableIPv6: function () {
      return this.$store.getters["getIsInfoAvailableIPv6"];
    },

    // isRequestingLocation
    isRequestingLocationIPv4: function () {
      return this.$store.state.isRequestingLocation;
    },
    isRequestingLocationIPv6: function () {
      return this.$store.state.isRequestingLocationIPv6;
    },
    isLoading: function () {
      return (
        (!this.isIPv6View && this.isRequestingLocationIPv4) ||
        (this.isIPv6View && this.isRequestingLocationIPv6)
      );
    },
    // the connection info is loaded (not loading and not failed)
    isInfoShown: function () {
      return (
        !this.isLoading && (this.isInfoAvailableIPv4 || this.isInfoAvailableIPv6)
      );
    },

    // location info for the current view (IPv4 or IPv6)
    currentLocation: function () {
      if (this.isIPv6View) return this.$store.state.locationIPv6;
      return this.$store.state.location;
    },

    ip: function () {
      const l = this.currentLocation;
      if (!l || !l.ip_address) return null;
      return l.ip_address;
    },
    ipVersion: function () {
      if (!this.ip) return null;
      return this.ip.includes(":") ? "IPv6" : "IPv4";
    },

    locationName: function () {
      const l = this.currentLocation;
      if (!l) return null;

      if (l.city) {
        if (l.country_code) return `${l.city}, ${l.country_code}`;
        else if (l.country) return `${l.city}, ${l.country}`;
      } else if (l.country) return `${l.country}`;
      return null;
    },
    countryCode: function () {
      const l = this.currentLocation;
      if (!l || !l.country_code) return null;
      return String(l.country_code).toUpperCase();
    },
    isOvpnPlusProvider: function () {
      const l = this.currentLocation;
      return !!l && l.isIvpnServer == true;
    },
    isp: function () {
      const l = this.currentLocation;
      if (!l) return null;
      if (l.isIvpnServer == true) return "OvpnPlus";
      if (!l.isp) return null;
      return l.isp;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

// IP / location / provider part of the map's "Connection details" card (the card is drawn by Component-Map).
// NOTE: every element gets an explicit colour because App.vue sets "html * { color }" for all elements.

.geoInfo {
  width: 100%;
  display: flex;
  flex-direction: column;
}

// ---------- IP row ----------
.ipRow {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 32px;
  gap: 12px;
  align-items: center;
}
.ipCell {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.labelRow {
  min-height: 14px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  column-gap: 6px;
  row-gap: 2px;
}
.infoLabel {
  font-size: 11px;
  font-weight: 600;
  line-height: 14px;
  letter-spacing: 0.06em;
  white-space: nowrap;
  color: var(--text-faint);
}
.ipTag {
  padding: 0 5px;
  border-radius: 4px;
  background: var(--neutral-tint);
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 600;
  line-height: 14px;
  white-space: nowrap;
}
.ipValueRow {
  min-height: 28px;
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}
.ipValue {
  min-width: 0;
  font-size: 15px;
  font-weight: 600;
  line-height: 22px;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
  color: var(--text-color);
  transition: filter 0.15s;
}
// hidden IP: blurred in place, so the row keeps its size and the address cannot be read or copied
.ipHidden {
  filter: blur(6px);
  user-select: none;
  -webkit-user-select: none;
}
.visuallyHidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
button.eyeBtn {
  flex: none;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 0;
  border-radius: 7px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  pointer-events: auto;
}
button.eyeBtn svg,
button.eyeBtn svg * {
  color: inherit;
  stroke: var(--text-muted);
}
// IP hidden: the "show" eye is a little brighter (it is the action to look for)
button.eyeBtn[aria-pressed="false"] svg,
button.eyeBtn[aria-pressed="false"] svg * {
  stroke: var(--text-soft, var(--text-color));
}
button.eyeBtn:hover {
  background: var(--neutral-tint);
}
button.eyeBtn:hover svg,
button.eyeBtn:hover svg * {
  stroke: var(--text-color);
}
button.eyeBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 1px;
}
.statusText {
  font-size: 13px;
  line-height: 22px;
  color: var(--text-muted);
}
.mismatchText {
  font-size: 11px;
  line-height: 14px;
  color: var(--text-faint);
}

// IPv4 / IPv6 switch: the tag drawn as a two-part segmented control
.ipToggle {
  display: flex;
  align-items: center;
  gap: 1px;
  padding: 1px;
  border-radius: 5px;
  background: var(--neutral-tint);
}
button.ipToggleBtn {
  position: relative;
  height: 16px;
  padding: 0 6px;
  border: 0;
  border-radius: 4px;
  background: transparent;
  color: var(--text-faint);
  font-size: 10px;
  font-weight: 600;
  line-height: 16px;
  cursor: pointer;
  pointer-events: auto;
}
// a 24 px tall hit area around the 16 px segment (pointer target size)
button.ipToggleBtn::before {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: -4px;
  bottom: -4px;
}
button.ipToggleBtn:hover {
  color: var(--text-color);
}
button.ipToggleBtnSelected {
  background: var(--surface-color);
  color: var(--text-color);
}
button.ipToggleBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 1px;
}

// Refresh button (32 x 32)
button.refreshBtn {
  width: 32px;
  height: 32px;
  flex: none;
  padding: 0;
  box-sizing: border-box;
  // same border and icon colours as the pause button (block-connect.vue)
  border: 1px solid var(--control-border, var(--surface-border));
  border-radius: 8px;
  // half way between the card and the neutral tint (#1D1D21 on the dark card, as in the design)
  background: color-mix(in srgb, var(--surface-color), var(--neutral-tint));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  pointer-events: auto;
}
button.refreshBtn:hover {
  border-color: var(--accent-color);
}
button.refreshBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}
.refreshIcon {
  stroke: var(--text-soft, var(--text-color));
}
button.refreshBtn:hover .refreshIcon {
  stroke: var(--text-color);
}

.cardDivider {
  height: 1px;
  margin: 12px 0;
  background: var(--surface-divider);
}

// ---------- LOCATION / PROVIDER ----------
.detailsGrid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.infoCell {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.providerCell {
  box-sizing: border-box;
  padding-left: 16px;
  border-left: 1px solid var(--surface-divider);
}
.infoValue {
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  color: var(--text-color);
}
// long city or ISP names wrap (no ellipsis)
.valueText {
  min-width: 0;
  overflow-wrap: anywhere;
  color: var(--text-color);
}
.locationValue {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  min-width: 0;
}
// as tall as one text line: the flag sits in the middle of the first line
.flagBox {
  flex: none;
  height: 20px;
  display: flex;
  align-items: center;
}
.infoValue.infoAccent {
  color: var(--link-color);
}
// loading / failed: a placeholder keeps the card height
.infoValue.noValue {
  color: var(--text-faint);
}
</style>
