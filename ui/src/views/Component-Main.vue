<template>
  <div id="flexview">
    <div class="flexColumn">
      <div class="leftPanelTopSpace">
        <header
          v-if="isControlView"
          class="appHeader"
          v-bind:class="{ appHeaderFramed: isWindowHasFrame }"
        >
          <img class="appLogo logoLight" src="@/assets/logo.png" alt="OvpnPlus" />
          <img class="appLogo logoDark" src="@/assets/logo_dark.png" alt="OvpnPlus" />
          <transition name="smooth-display">
            <div v-if="isMinimizedButtonsVisible" class="headerButtons">
              <button v-on:click="onAccountSettings()" title="Account settings" aria-label="Account settings">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="4" /><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" /></svg>
              </button>
              <button v-on:click="onSettings()" title="Settings" aria-label="Settings">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3" /><path d="M12 2v3M12 19v3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M2 12h3M19 12h3M4.9 19.1 7 17M17 7l2.1-2.1" /></svg>
              </button>
              <button v-on:click="onMaximize(true)" title="Show map" aria-label="Show map">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" /></svg>
              </button>
            </div>
          </transition>
        </header>
      </div>
      <div class="flexColumn" style="min-height: 0px">
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
    </div>
    <div id="right" v-if="!isMinimizedUI">
      <transition name="fade" appear>
        <TheMap
          :isBlured="isMapBlured"
          :onAccountSettings="onAccountSettings"
          :onSettings="onSettings"
          :onMinimize="() => onMaximize(false)"
        />
      </transition>
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

export default {
  components: {
    Init,
    Login,
    Control,
    TheMap,
    ParanoidModePassword,
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
    isMinimizedButtonsVisible: function () {
      if (this.currentViewComponent !== Control) return false;
      if (this.isCanShowMinimizedButtons !== true) return false;
      return this.isMinimizedUI;
    },
    isMinimizedUI: function () {
      return this.$store.state.settings.minimizedUI;
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
  },
};
</script>

<style scoped lang="scss">
@import "@/components/scss/constants";

#flexview {
  display: flex;
  flex-direction: row;
  height: 100%;
}

#left {
  width: 320px;
  min-width: 320px;
  max-width: 320px;
}
#right {
  width: 0%; // ???
  flex-grow: 1;
}

.appHeader {
  height: 56px;
  box-sizing: border-box;
  padding: 24px 10px 0 16px; // the top 24 px belong to the window title bar (minimize / close)
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--surface-divider);
}
.appHeaderFramed {
  height: 44px;
  padding-top: 0;
}
.appLogo {
  height: 15px;
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
.headerButtons {
  display: flex;
  gap: 2px;
}
.headerButtons button {
  -webkit-app-region: no-drag;
  z-index: 101;
  width: 30px;
  height: 30px;
  padding: 0;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.headerButtons button:hover {
  background: var(--neutral-tint);
  color: var(--text-color);
}

div.minimizedButtonsPanelRightElements {
  display: flex;
  justify-content: flex-end;
}

div.minimizedButtonsPanel {
  display: flex;

  margin-left: 10px;
  margin-right: 10px;
  margin-top: 10px;
}

div.minimizedButtonsPanel button {
  @extend .noBordersBtn;

  -webkit-app-region: no-drag;
  z-index: 101;
  cursor: pointer;

  padding: 0px;
  margin-left: 6px;
  margin-right: 6px;
}

div.minimizedButtonsPanel img {
  height: 18px;
}
</style>
