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
        <div v-else class="ipValue">{{ ip || "Unknown" }}</div>
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
          <img
            v-if="flagUrl"
            class="flag"
            :src="flagUrl"
            alt=""
            width="14"
            height="14"
            v-on:error="onFlagError"
          />
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
const sender = window.ipcSender;

export default {
  data: () => ({
    // flag image that failed to load (do not try to show it again)
    failedFlagUrl: null,
  }),
  methods: {
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
    onFlagError(e) {
      this.failedFlagUrl = e?.target?.getAttribute("src") || null;
    },
  },
  computed: {
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
    flagUrl: function () {
      const l = this.currentLocation;
      if (!l || !l.country_code) return null;
      const url = `flags/svg/${String(l.country_code).toUpperCase()}.svg`;
      if (url === this.failedFlagUrl) return null;
      return url;
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
.ipValue {
  font-size: 15px;
  font-weight: 600;
  line-height: 22px;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
  color: var(--text-color);
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
  gap: 7px;
  min-width: 0;
}
.flag {
  width: 14px;
  height: 14px;
  flex: none;
  margin-top: 3px; // centre on the first 20 px text line
  border-radius: 50%;
  object-fit: cover;
  display: block;
}
.infoValue.infoAccent {
  color: var(--link-color);
}
// loading / failed: a placeholder keeps the card height
.infoValue.noValue {
  color: var(--text-faint);
}
</style>
