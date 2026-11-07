<template>
  <section class="hero">
    <!-- PAUSE (top right corner) -->
    <div class="pauseCorner">
      <transition name="fade">
        <div v-if="isCanPause" class="buttonWithPopup">
          <button
            class="cornerBtn"
            title="Pause"
            aria-label="Pause"
            v-on:click="onPauseMenu"
            v-click-outside="onPauseMenuClickOutside"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <rect x="6" y="5" width="4" height="14" rx="1" />
              <rect x="14" y="5" width="4" height="14" rx="1" />
            </svg>
          </button>
          <div class="popup popupCorner">
            <div class="popuptext" v-bind:class="{ show: isCanShowPauseMenu }">
              <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(5 * 60)">
                <button>Pause for 5 min</button>
              </div>
              <div class="popup_dividing_line" />
              <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(30 * 60)">
                <button>Pause for 30 min</button>
              </div>
              <div class="popup_dividing_line" />
              <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(1 * 60 * 60)">
                <button>Pause for 1 hour</button>
              </div>
              <div class="popup_dividing_line" />
              <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(3 * 60 * 60)">
                <button>Pause for 3 hours</button>
              </div>
            </div>
          </div>
        </div>
        <button
          v-else-if="isCanResume"
          class="cornerBtn cornerBtnResume"
          title="Resume"
          aria-label="Resume"
          v-on:click="onPauseResume(null)"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M7 4.5v15l13-7.5z" />
          </svg>
        </button>
      </transition>
    </div>

    <!-- POWER BUTTON -->
    <button
      class="powerBtn"
      v-bind:class="{ on: isOn, busy: isProgress, paused: isCanResume }"
      :title="powerTitle"
      :aria-label="powerTitle"
      v-on:click="onPowerClick"
    >
      <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">
        <path d="M12 3v8" />
        <path d="M6.4 6.6a8 8 0 1 0 11.2 0" />
      </svg>
      <span class="powerLabel">{{ powerLabel }}</span>
    </button>

    <!-- STATUS -->
    <div class="statusBlock" role="status">
      <div class="statusTitle">
        {{ statusTitle }}
        <!-- Unhealthy connection notification. -->
        <button v-if="isConnectionUnhealthy" class="noBordersBtn connectionWarningBtn" aria-label="Unhealthy connection">
          <img src="@/assets/warning.svg" height="22" alt="" />
          <span class="connectionWarningPopup">
            <strong>Unhealthy connection.</strong>
            <br />
            No traffic detected on the VPN tunnel.
            This may be caused by a connectivity issue, network restriction, or a temporary disruption.
          </span>
        </button>
      </div>

      <!-- paused: time left, click for the resume menu -->
      <div v-if="isCanResume" class="buttonWithPopup">
        <button
          class="statusLine statusPaused noBordersTextBtn"
          v-on:click="onAddPauseTimeMenu"
          v-click-outside="onPauseMenuClickOutside"
        >
          <span class="dot" />Resumes in {{ pauseTimeLeftText }}
        </button>
        <div class="popup popupMin">
          <div class="popuptext popuptextMin" v-bind:class="{ show: isPauseExtendMenuShow }">
            <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(null)">
              <button>Resume now</button>
            </div>
            <div class="popup_dividing_line" />
            <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(5 * 60)">
              <button>Resume in 5 min</button>
            </div>
            <div class="popup_dividing_line" />
            <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(30 * 60)">
              <button>Resume in 30 min</button>
            </div>
            <div class="popup_dividing_line" />
            <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(1 * 60 * 60)">
              <button>Resume in 1 hour</button>
            </div>
            <div class="popup_dividing_line" />
            <div class="popup_menu_block_clickable" v-on:click="onPauseMenuItem(3 * 60 * 60)">
              <button>Resume in 3 hours</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="statusLine" v-bind:class="statusLineClass">
        <span class="dot" />{{ statusLineText }}
      </div>

      <div v-if="ipLineText" class="ipLine">{{ ipLineText }}</div>

      <transition name="fade">
        <button
          v-show="splitTunnelWarningText"
          class="noBordersTextBtn"
          v-on:click="onSplitTunnelInfoClick"
        >
          <div class="small_text_warning">
            {{ splitTunnelWarningText }}
          </div>
        </button>
      </transition>
    </div>

    <transition name="fade">
      <BlockSpeed v-if="isOn" />
    </transition>
  </section>
</template>

<script>
const sender = window.ipcSender;

import BlockSpeed from "@/components/blocks/block-speed.vue";
import { GetTimeLeftText } from "@/helpers/renderer";
import vClickOutside from "click-outside-vue3";

export default {
  directives: {
    clickOutside: vClickOutside.directive,
  },
  components: {
    BlockSpeed,
  },
  props: ["onChecked", "onPauseResume", "isChecked", "isProgress"],
  data: () => ({
    isPauseMenuAllowed: false,
    isPauseExtendMenuShow: false,
    pauseTimeUpdateTimer: null,
    pauseTimeLeftText: "",
    now: Date.now(),
    clockTimer: null,
  }),
  mounted() {
    this.startPauseTimer();
    this.clockTimer = setInterval(() => {
      this.now = Date.now();
    }, 1000);
  },
  unmounted() {
    if (this.clockTimer) clearInterval(this.clockTimer);
    if (this.pauseTimeUpdateTimer) clearInterval(this.pauseTimeUpdateTimer);
  },
  computed: {
    isMinimizedUI: function () {
      return this.$store.state.settings.minimizedUI;
    },
    isConnected: function () {
      return this.$store.getters["vpnState/isConnected"];
    },
    isOn: function () {
      return this.isChecked === true && this.isProgress !== true && !this.isCanResume;
    },
    isDisconnecting: function () {
      return this.$store.getters["vpnState/isDisconnecting"];
    },
    powerLabel: function () {
      if (this.isProgress) return "CANCEL";
      if (this.isCanResume) return "PAUSED";
      if (this.isOn) return "ON";
      return "CONNECT";
    },
    powerTitle: function () {
      if (this.isProgress) return "Cancel";
      return this.isChecked === true ? "Disconnect" : "Connect";
    },
    statusTitle: function () {
      if (this.isProgress) return this.isDisconnecting ? "Disconnecting…" : "Connecting…";
      if (this.isCanResume) return "Paused";
      if (this.isOn) return "Protected";
      return "Not protected";
    },
    statusLineClass: function () {
      if (this.isProgress) return "statusBusy";
      if (this.isOn) return "statusOn";
      return "statusOff";
    },
    statusLineText: function () {
      if (this.isProgress)
        return this.isDisconnecting ? "Closing the tunnel" : "Setting up a secure tunnel";
      if (this.isOn) {
        const elapsed = this.connectedForText;
        return elapsed ? `Connected · ${elapsed}` : "Connected";
      }
      return "Your real IP is visible";
    },
    connectedForText: function () {
      const t = this.$store.state.vpnState.connectionInfo?.TimeSecFrom1970;
      if (!t) return "";
      const startMs = t instanceof Date ? t.getTime() : Number(t) * 1000;
      if (!Number.isFinite(startMs) || startMs <= 0) return "";
      let sec = Math.max(0, Math.floor((this.now - startMs) / 1000));
      const h = Math.floor(sec / 3600);
      sec -= h * 3600;
      const m = Math.floor(sec / 60);
      const s = sec - m * 60;
      const pad = (n) => String(n).padStart(2, "0");
      return `${pad(h)}:${pad(m)}:${pad(s)}`;
    },
    ipLineText: function () {
      const l = this.$store.state.location;
      if (!l || !l.ip_address) return "";
      let place = "";
      if (l.city) place = l.country_code ? `${l.city}, ${l.country_code}` : l.city;
      else if (l.country) place = l.country;
      return place ? `${l.ip_address} · ${place}` : l.ip_address;
    },
    pauseConnectionTill: function () {
      return this.$store.state.vpnState?.connectionInfo?.PausedTill;
    },
    isPaused: function () {
      return this.$store.getters["vpnState/isPaused"];
    },
    isCanPause: function () {
      if (!this.isConnected) return false;
      if (this.isProgress === true) return false;
      if (this.$store.state.uiState.isPauseResumeInProgress === true)
        return false;

      var connInfo = this.$store.state.vpnState.connectionInfo;
      if (connInfo === null) return false;
      if (!this.isPaused) return true;
      return false;
    },
    isCanResume: function () {
      if (this.isCanPause) return false;
      if (!this.isConnected) return false;
      if (this.isProgress === true) return false;
      if (this.$store.state.uiState.isPauseResumeInProgress === true)
        return false;

      if (this.isPaused) return true;
      return false;
    },
    isCanShowPauseMenu: function () {
      return this.isCanPause && this.isPauseMenuAllowed;
    },
    isConnectionUnhealthy: function () {
      return this.$store.getters["vpnState/isConnectionUnhealthy"];
    },
    // Single slot for Split Tunnel warnings: the view has room for one line.
    // Details and the fix are in the Split Tunnel settings (see the click handler).
    splitTunnelWarningText: function () {
      if (this.$store.getters["uiState/splitTunnelMacOSIssue"])
        return "Split Tunnel is not active";
      if (this.$store.getters["vpnState/isInverseSplitTunnel"])
        return "Inverse Split Tunnel mode is active";
      return "";
    },
  },
  watch: {
    isPaused() {
      this.startPauseTimer();
    },
  },
  methods: {
    onPowerClick(e) {
      if (!this.onChecked) return;
      // same behaviour as the old switch: during progress a click cancels
      if (this.isProgress) this.onChecked(false, e);
      else this.onChecked(this.isChecked !== true, e);
    },
    onSplitTunnelInfoClick() {
      sender.ShowSplitTunnelSettings();
    },
    onPauseMenuClickOutside() {
      this.isPauseExtendMenuShow = false;
      this.isPauseMenuAllowed = false;
    },
    onPauseMenu() {
      if (this.isPauseMenuAllowed != true) this.onPauseResume(null);
      this.isPauseMenuAllowed = !this.isPauseMenuAllowed;
    },
    onAddPauseTimeMenu() {
      if (this.isCanResume != true) this.isPauseExtendMenuShow = false;
      else this.isPauseExtendMenuShow = !this.isPauseExtendMenuShow;
    },
    onPauseMenuItem(seconds) {
      this.isPauseMenuAllowed = false;
      this.isPauseExtendMenuShow = false;
      if (this.onPauseResume != null) this.onPauseResume(seconds);
    },
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

<style scoped lang="scss">
@import "@/components/scss/constants";
@import "@/components/scss/popup";

.hero {
  position: relative;
  padding: 12px 20px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

// ---------- power button ----------
.powerBtn {
  position: relative;
  margin: 10px;
  width: 112px;
  height: 112px;
  border-radius: 50%;
  border: 2px solid var(--surface-border);
  background: var(--surface-color);
  box-shadow: 0 0 0 9px var(--surface-color);
  color: var(--text-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  cursor: pointer;
  transition: background-color 0.25s, box-shadow 0.25s, color 0.25s;
  -webkit-app-region: no-drag;
}
.powerBtn:hover {
  border-color: var(--accent-color);
}
.powerBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 12px;
}
.powerBtn.on {
  border-color: var(--accent-color);
  background: var(--accent-color);
  color: var(--accent-text-color);
  box-shadow: 0 0 0 9px var(--accent-tint), 0 0 0 10px var(--accent-ring);
}
.powerBtn.on:hover {
  background: var(--accent-color-hover);
}
.powerBtn.paused {
  border-color: var(--accent-color);
  color: var(--link-color);
}
.powerBtn.busy::after {
  content: "";
  position: absolute;
  inset: -12px;
  border-radius: 50%;
  border: 2px solid transparent;
  border-top-color: var(--accent-color);
  border-right-color: var(--accent-color);
  animation: powerSpin 1s linear infinite;
}
@keyframes powerSpin {
  to {
    transform: rotate(360deg);
  }
}
.powerLabel {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

// ---------- status ----------
.statusBlock {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  text-align: center;
}
.statusTitle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 23px;
  line-height: 27px;
  font-weight: 700;
  letter-spacing: -0.3px;
}
.statusLine {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  line-height: 16px;
  font-variant-numeric: tabular-nums;
}
.statusLine .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex: none;
}
.statusOn {
  color: var(--link-color);
}
.statusOn .dot {
  background: var(--accent-color);
}
.statusOff {
  color: var(--danger-text);
}
.statusOff .dot {
  background: var(--danger-dot);
}
.statusBusy,
.statusPaused {
  color: var(--text-muted);
}
.statusBusy .dot,
.statusPaused .dot {
  background: var(--text-faint);
}
.statusPaused {
  cursor: pointer;
  text-decoration: underline dotted;
  text-underline-offset: 3px;
}
.ipLine {
  font-size: 12.5px;
  line-height: 15px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

// ---------- pause corner ----------
.pauseCorner {
  position: absolute;
  top: 12px;
  right: 16px;
  z-index: 5;
}
.cornerBtn {
  width: 34px;
  height: 34px;
  border: 1px solid var(--surface-border);
  border-radius: 50%;
  background: var(--surface-color);
  color: var(--text-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}
.cornerBtn:hover {
  border-color: var(--accent-color);
}
.cornerBtnResume {
  background: var(--accent-color);
  border-color: var(--accent-color);
  color: var(--accent-text-color);
}
// the corner popup opens to the left so it stays inside the 320 px panel
.popupCorner .popuptext {
  margin-left: -190px;
}
.popupCorner .popuptext::after {
  left: auto;
  right: 6px;
}

.popup_menu_block_clickable {
  @extend .popup_menu_block;
  cursor: pointer;
}

.small_text_warning {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: -0.3px;
  color: var(--warning-color);
}

//----------------- Unhealthy connection -------------------------------------

.connectionWarningBtn {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin: 0px;
  padding: 0px;
}

.connectionWarningBtn:hover .connectionWarningPopup {
  visibility: visible;
  opacity: 1;
  transition-delay: 0s;
}

.connectionWarningPopup {
  pointer-events: none;
  visibility: hidden;
  opacity: 0;
  transition: visibility 0s linear 1.5s, opacity 0.3s ease 0.2s;
  position: absolute;
  top: calc(100% + 14px);
  left: 50%;
  transform: translateX(-50%);
  min-width: 240px;
  max-width: 240px;
  background-color: var(--background-color);
  border-radius: 14px;
  box-shadow: 0px 0px 34px rgba(0, 0, 0, var(--shadow-opacity-koef));
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.5;
  font-weight: normal;
  text-align: left;
  z-index: 4;
}

.connectionWarningPopup::before {
  content: "";
  position: absolute;
  top: -12px;
  left: 50%;
  margin-left: -12px;
  border-width: 0 12px 12px 12px;
  border-style: solid;
  border-color: transparent transparent var(--background-color) transparent;
}

// in use for minimalistic UI (reduced width)
.popupMin .popuptextMin {
  min-width: 160px;
  max-width: 160px;
  margin-left: -80px;
}
</style>
