<template>
  <div id="flexview">
    <!-- Window title bar: one 44 px bar across the whole window (both panels).
         The bar is the drag region of the window; its buttons are 'no-drag'. -->
    <header
      class="appTitleBar"
      v-bind:class="{ appTitleBarFramed: isWindowHasFrame }"
    >
      <div v-if="isControlView" class="appBrand">
        <svg
          class="appBrandMark"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path class="appBrandRing" d="M19.96 12.84 A8 8 0 1 1 11.16 4.04" />
          <path class="appBrandAccent" d="M13.11 4.08 A8 8 0 0 1 16.93 5.70" />
          <path class="appBrandAccent" d="M18.30 7.07 A8 8 0 0 1 19.92 10.89" />
        </svg>
        <img class="appWordmark logoLight" src="@/assets/logo.png" alt="OvpnPlus" draggable="false" />
        <img class="appWordmark logoDark" src="@/assets/logo_dark.png" alt="OvpnPlus" draggable="false" />
      </div>

      <div class="appTitleBarRight">
        <transition name="smooth-display">
          <div v-if="isToolButtonsVisible" class="appTitleBarTools">
            <button
              v-if="!isMinimizedUI"
              type="button"
              class="appBarBtn"
              v-on:click="onCenterMap()"
              title="Center map on my location"
              aria-label="Center map on my location"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="7" /><circle cx="12" cy="12" r="2" /><path d="M12 2v3M12 19v3M2 12h3M19 12h3" /></svg>
            </button>
            <button
              type="button"
              class="appBarBtn"
              v-on:click="onAccountSettings()"
              title="Account"
              aria-label="Account"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="4" /><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" /></svg>
            </button>
            <button
              type="button"
              class="appBarBtn"
              v-on:click="onSettings()"
              title="Settings"
              aria-label="Settings"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" /></svg>
            </button>
            <button
              v-if="isMinimizedUI"
              type="button"
              class="appBarBtn"
              v-on:click="onMaximize(true)"
              title="Show map"
              aria-label="Show map"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" /></svg>
            </button>
            <button
              v-else
              type="button"
              class="appBarBtn"
              v-on:click="onMaximize(false)"
              title="Hide map"
              aria-label="Hide map"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7" /></svg>
            </button>
            <!-- divider between the app tools and the window buttons (no window buttons on macOS) -->
            <span
              v-if="!isWindowHasFrame"
              class="appTitleBarDivider"
              aria-hidden="true"
            ></span>
          </div>
        </transition>

        <!-- Minimize / Close (only for windows without a native frame: Windows, Linux) -->
        <CustomTitleBar inline />
      </div>
    </header>

    <div class="appBody">
      <div class="flexColumn appLeftColumn">
        <transition name="fade" mode="out-in">
          <component
            v-bind:is="currentViewComponent"
            :onConnectionSettings="onConnectionSettings"
            :onWifiSettings="onWifiSettings"
            :onFirewallSettings="onFirewallSettings"
            :onAntiTrackerSettings="onAntitrackerSettings"
            :onDefaultView="onDefaultLeftView"
            id="left"
          ></component>
        </transition>
      </div>
      <div id="right" v-if="!isMinimizedUI">
        <transition name="fade" appear>
          <TheMap
            ref="map"
            :isBlured="isMapBlured"
            :onAccountSettings="onAccountSettings"
            :onSettings="onSettings"
            :onMinimize="() => onMaximize(false)"
          />
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
const sender = window.ipcSender;

import { DaemonConnectionType } from "@/store/types";
import { IsWindowHasFrame } from "@/platform/platform";
import Init from "@/components/Component-Init.vue";
import Login from "@/components/Component-Login.vue";
import Control from "@/components/Component-Control.vue";
import TheMap from "@/components/Component-Map.vue";
import ParanoidModePassword from "@/components/ParanoidModePassword.vue";
import CustomTitleBar from "@/views/CustomTitleBar.vue";

export default {
  components: {
    Init,
    Login,
    Control,
    TheMap,
    ParanoidModePassword,
    CustomTitleBar,
  },
  data: function () {
    return {
      isCanShowMinimizedButtons: true,
    };
  },
  computed: {
    isWindowHasFrame: function () {
      return IsWindowHasFrame();
    },
    isLoggedIn: function () {
      return this.$store.getters["account/isLoggedIn"];
    },
    currentViewComponent: function () {
      const daemonConnection = this.$store.state.daemonConnectionState;
      if (daemonConnection !== DaemonConnectionType.Connected)
        return Init;
      if (this.$store.state.uiState.isParanoidModePasswordView === true)
        return ParanoidModePassword;
      if (!this.isLoggedIn) return Login;

      return Control;
    },
    isMapBlured: function () {
      if (this.currentViewComponent !== Control) return "true";
      return "false";
    },
    isControlView: function () {
      return this.currentViewComponent === Control;
    },
    // Title bar tools (Account, Settings, Show/Hide map, Center map).
    // Shown only for the logged-in Control view.
    // Compact window: hidden while the left panel shows a non-default view (e.g. servers list).
    // Expanded window: always shown (as the map buttons were).
    isToolButtonsVisible: function () {
      if (this.currentViewComponent !== Control) return false;
      if (!this.isMinimizedUI) return true;
      return this.isCanShowMinimizedButtons === true;
    },
    isMinimizedUI: function () {
      return this.$store.state.settings.minimizedUI;
    },
  },

  watch: {
    // A Control view that is shown again (after log out / log in, a daemon reconnect or the
    // password view) always starts in its default view, even if the servers list was open
    // when it was removed. Show the title bar tools again.
    isControlView: function (isControl) {
      if (isControl) this.isCanShowMinimizedButtons = true;
    },
  },

  methods: {
    onAccountSettings: function () {
      //if (this.$store.state.settings.minimizedUI)
      sender.ShowAccountSettings();
      //else this.$router.push({ name: "settings", params: { view: "account" } });
    },
    onSettings: function () {
      sender.ShowSettings();
    },
    onConnectionSettings: function () {
      sender.ShowConnectionSettings();
    },
    onWifiSettings: function () {
      sender.ShowWifiSettings();
    },
    onFirewallSettings: function () {
      sender.ShowFirewallSettings();
    },
    onAntitrackerSettings: function () {
      sender.ShowAntitrackerSettings();
    },
    onDefaultLeftView: function (isDefaultView) {
      this.isCanShowMinimizedButtons = isDefaultView;
    },
    onMaximize: function (isMaximize) {
      this.$store.dispatch("settings/minimizedUI", !isMaximize);
    },
    onCenterMap: function () {
      const map = this.$refs.map;
      if (map && typeof map.centerCurrentLocation === "function")
        map.centerCurrentLocation();
    },
  },
};
</script>

<style scoped lang="scss">
@import "@/components/scss/constants";

#flexview {
  display: flex;
  flex-direction: column;
  height: 100%;
}

// ===== Title bar =====
.appTitleBar {
  // above the panels: a map popup near the top edge must not cover the bar
  position: relative;
  z-index: 10;
  flex: none;
  height: 44px;
  box-sizing: border-box;
  padding: 0 4px 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--surface-divider);
  background: var(--background-color);

  // the bar moves the window; its buttons do not
  -webkit-app-region: drag;
}
// macOS: native window buttons (traffic lights) are drawn at the top-left corner
.appTitleBarFramed {
  padding-left: 76px;
  padding-right: 8px;
}

.appBrand {
  flex: none;
  display: flex;
  align-items: center;
  gap: 8px;
  user-select: none;
}
.appBrandMark {
  display: block;
  flex: none;
}
.appBrandMark path {
  fill: none;
  stroke-width: 4;
}
.appBrandRing {
  stroke: var(--text-color);
}
.appBrandAccent {
  stroke: var(--accent-color);
}
.appWordmark {
  display: block;
  height: 11px;
  width: auto;
  user-select: none;
  pointer-events: none;
}
.logoDark {
  display: none;
}
@media (prefers-color-scheme: dark) {
  .logoLight {
    display: none;
  }
  .logoDark {
    display: block;
  }
}

.appTitleBarRight {
  flex: none;
  margin-left: auto;
  display: flex;
  align-items: center;
}
.appTitleBarTools {
  display: flex;
  align-items: center;
}
.appTitleBarDivider {
  flex: none;
  width: 1px;
  height: 16px;
  margin: 0 6px;
  background: var(--surface-border);
}

.appBarBtn {
  -webkit-app-region: no-drag;
  flex: none;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
// the global 'html *' color rule would otherwise give the icon the text colour
.appBarBtn svg,
.appBarBtn svg * {
  color: inherit;
}
.appBarBtn:hover {
  background: var(--neutral-tint);
  color: var(--text-color);
}
.appBarBtn:focus {
  outline: none;
}
.appBarBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}

// ===== Panels under the title bar =====
.appBody {
  flex: 1 1 0;
  min-height: 0;
  display: flex;
  flex-direction: row;
}
.appLeftColumn {
  flex: none;
  min-height: 0;
}

#left {
  width: 320px;
  min-width: 320px;
  max-width: 320px;
}
#right {
  width: 0%; // ???
  min-width: 0;
  flex-grow: 1;
  // the 1 px line between the left panel and the map
  box-sizing: border-box;
  border-left: 1px solid var(--surface-divider);
}
</style>
