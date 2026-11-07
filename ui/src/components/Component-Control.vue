<template>
  <div class="flexColumn">
    <transition name="fade-super-quick" mode="out-in">
      <div
        class="flexColumn"
        v-if="uiView === 'serversEntry'"
        key="entryServers"
      >
        <Servers
          :onBack="backToMainView"
          :onServerChanged="onServerChanged"
          :onFastestServer="onFastestServer"
          :onRandomServer="onRandomServer"
        />
      </div>

      <div
        class="flexColumn"
        v-else-if="uiView === 'serversExit'"
        key="exitServers"
      >
        <Servers
          :onBack="backToMainView"
          isExitServer="true"
          :onServerChanged="onServerChanged"
          :onRandomServer="() => onRandomServer(true)"
        />
      </div>

      <!--
        Main view (B design, 556 px under the 44 px title bar):
        hero (power button, status, speed) | cards (server, kill switch + protocol;
        they scroll when they do not fit) | plan card pinned to the bottom.
      -->
      <div v-else class="flexColumn controlView">
        <ConnectBlock
          class="heroArea"
          :onChecked="switchChecked"
          :isChecked="isConnected"
          :isProgress="isInProgress"
          :onPauseResume="onPauseResume"
        />

        <div class="cardsArea">
          <div class="scrollWrap">
            <div
              ref="scrollArea"
              class="scrollableColumnContainer cardsScroll"
              @scroll="recalcScrollButtonVisiblity()"
            >
              <div v-if="isMultihopAllowed" class="hopButtonsArea">
                <HopButtonsBlock />
                <div class="horizontalLine hopButtonsSeparator" />
              </div>

              <SelectedServerBlock
                :onShowServersPressed="onShowServersPressed"
              />

              <SelectedServerBlock
                v-if="isMultiHop"
                :onShowServersPressed="onShowServersPressed"
                isExitServer="true"
              />

              <ConnectionDetailsBlock
                :onShowPorts="onShowPorts"
                :onShowWifiConfig="onShowWifiConfig"
                :onShowFirewallConfig="onFirewallSettings"
                :onShowAntiTrackerConfig="onAntiTrackerSettings"
              />
            </div>

            <!-- outside the scrolling box, so it stays at the bottom of the visible part -->
            <transition name="fade">
              <button
                type="button"
                title="Scroll down"
                aria-label="Scroll down"
                class="btnScrollDown"
                v-if="isShowScrollButton"
                v-on:click="onScrollDown()"
              >
                <!-- the same 28 px button and chevron as the server list's -->
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke-width="2.2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </button>
            </transition>
          </div>

          <PlanBar />
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import Servers from "./Component-Servers.vue";
import ConnectBlock from "./blocks/block-connect.vue";
import ConnectionDetailsBlock from "./blocks/block-connection-details.vue";
import SelectedServerBlock from "@/components/blocks/block-selected-server.vue";
import HopButtonsBlock from "./blocks/block-hop-buttons.vue";
import PlanBar from "./blocks/block-plan-bar.vue";

const sender = window.ipcSender;
import { VpnStateEnum, VpnTypeEnum } from "@/store/types";
import { capitalizeFirstLetter } from "@/helpers/helpers";
import {
  IsServerLocked,
  IsHostLocked,
  HostId,
} from "@/helpers/helpers_premium";

const viewTypeEnum = Object.freeze({
  default: "default",
  serversEntry: "serversEntry",
  serversExit: "serversExit",
});

async function connect(me, isConnect) {
  try {
    me.isConnectProgress = true;
    if (isConnect === true) {
      // Free account: a selection it cannot use (e.g. kept from a Premium plan)
      // falls back to the fastest usable server instead of failing
      me.ensureUsableServers(true);
      await sender.Connect();
    } else await sender.Disconnect();
  } catch (e) {
    console.error(e);
    sender.showMessageBoxSync({
      type: "error",
      buttons: ["OK"],
      message: `Failed to ${isConnect ? "connect" : "disconnect"}: ` + e,
    });
  } finally {
    me.isConnectProgress = false;
  }
}

export default {
  props: {
    onConnectionSettings: Function,
    onWifiSettings: Function,
    onFirewallSettings: Function,
    onAntiTrackerSettings: Function,
    onDefaultView: Function,
  },

  components: {
    PlanBar,
    HopButtonsBlock,
    Servers,
    ConnectBlock,
    SelectedServerBlock,
    ConnectionDetailsBlock,
  },
  mounted() {
    this.recalcScrollButtonVisiblity();

    // ResizeObserver sometimes is stopping to work for unknown reason. So, We do not use it for now
    // Instead, watchers are in use: isMinimizedUI, isMultiHop
    //const resizeObserver = new ResizeObserver(this.recalcScrollButtonVisiblity);
    //resizeObserver.observe(this.$refs.scrollArea);
  },
  data: function () {
    return {
      isShowScrollButton: false,
      isConnectProgress: false,
      uiView: viewTypeEnum.default,
      lastServersPingRequestTime: null,
    };
  },

  computed: {
    isConnected: function () {
      return this.$store.getters["vpnState/isConnected"];
    },
    isConnecting: function () {
      return this.$store.getters["vpnState/isConnecting"];
    },
    isOpenVPN: function () {
      return this.$store.state.settings.vpnType === VpnTypeEnum.OpenVPN;
    },
    isMultihopAllowed: function () {
      return this.$store.getters["account/isMultihopAllowed"];
    },
    isInProgress: function () {
      if (this.isConnectProgress) return this.isConnectProgress;
      return (
        this.$store.state.vpnState.connectionState !== VpnStateEnum.CONNECTED &&
        this.$store.state.vpnState.connectionState !== VpnStateEnum.DISCONNECTED
      );
    },
    // needed for watcher
    conectionState: function () {
      return this.$store.state.vpnState.connectionState;
    },
    isMinimizedUI: function () {
      return this.$store.state.settings.minimizedUI;
    },
    isMultiHop: function () {
      return this.$store.state.settings.isMultiHop;
    },
    // true when the account status is known and it is not Premium
    isFreeAccount: function () {
      return this.$store.getters["vpnState/isFreeAccount"] === true;
    },
    // needed for watcher: which servers the account may use ("" until the status is known)
    accountTierKey: function () {
      if (this.$store.getters["vpnState/isAccountStatusKnown"] !== true)
        return "";
      return this.$store.getters["account/isPremiumAccount"] === true
        ? "premium"
        : "free";
    },
    // needed for watcher: things that change the height of the hero or of the cards
    // (split tunnel warning line, plan card, Wi-Fi row, the speed card hidden while paused,
    // the IP line that wraps for a long address or city) and so the room left to the cards
    cardsLayoutKey: function () {
      const l = this.$store.state.location;
      return [
        this.$store.getters["vpnState/isInverseSplitTunnel"] === true,
        this.$store.getters["uiState/splitTunnelMacOSIssue"] === true,
        !!this.$store.state.account.accountStatus,
        this.$store.state.vpnState.currentWiFiInfo?.SSID || "",
        this.$store.getters["vpnState/isPaused"] === true,
        l ? [l.ip_address, l.city, l.country_code, l.country].join(",") : "",
      ].join("|");
    },
  },

  watch: {
    conectionState(newValue, oldValue) {
      // the speed card appears/disappears with the connection: the cards area changes height
      setTimeout(() => this.recalcScrollButtonVisiblity(), 1000);

      // Free account: a server kept while it was in use (e.g. the plan ended during
      // the connection) is replaced now that it is not
      if (newValue === VpnStateEnum.DISCONNECTED && newValue != oldValue)
        this.ensureUsableServers();

      // show connection failure description:

      // only in case of changing to DISCONNECTED
      if (newValue !== VpnStateEnum.DISCONNECTED || newValue == oldValue)
        return;

      // if disconnection reason defined
      let failureInfo = this.$store.state.vpnState.disconnectedInfo;
      if (!failureInfo || !failureInfo.ReasonDescription) return;

      sender.showMessageBoxSync({
        type: "error",
        buttons: ["OK"],
        message: `Failed to connect`,
        detail: capitalizeFirstLetter(failureInfo.ReasonDescription),
      });
    },
    isMinimizedUI() {
      setTimeout(() => this.recalcScrollButtonVisiblity(), 1000);
    },
    isMultiHop() {
      setTimeout(() => this.recalcScrollButtonVisiblity(), 1000);
    },
    cardsLayoutKey() {
      setTimeout(() => this.recalcScrollButtonVisiblity(), 1000);
    },
    // the account became Free (or Premium): keep the selection to servers it may use
    accountTierKey: {
      immediate: true,
      handler(key) {
        if (key) this.ensureUsableServers();
      },
    },
  },

  methods: {
    async switchChecked(isConnect) {
      connect(this, isConnect);
    },
    async onPauseResume(seconds) {
      if (seconds == null || seconds == 0) {
        // RESUME
        if (this.$store.getters["vpnState/isPaused"])
          await sender.ResumeConnection();
      } else {
        // PAUSE
        await sender.PauseConnection(seconds);
      }
    },
    async onShowServersPressed(isExitServers) {
      // send request to update servers from backend
      sender.UpdateServersRequest();

      this.uiView = isExitServers
        ? viewTypeEnum.serversExit
        : viewTypeEnum.serversEntry;

      if (this.onDefaultView) this.onDefaultView(false);

      // request servers ping not more often than once per 15 seconds
      let isHasPingResuls =
        Object.keys(this.$store.state.vpnState.hostsPings).length > 0;
      if (
        isHasPingResuls == false ||
        this.lastServersPingRequestTime == null ||
        (new Date().getTime() - this.lastServersPingRequestTime.getTime()) /
          1000 >
          15
      ) {
        try {
          await sender.PingServers();
        } catch (e) {
          console.error(e);
        }
        this.lastServersPingRequestTime = new Date();
      } else {
        console.log(
          "Server pings request blocked (due to requests per minute limitation)",
        );
      }
    },
    onShowPorts() {
      if (this.onConnectionSettings != null) this.onConnectionSettings();
    },
    onShowWifiConfig() {
      if (this.onWifiSettings != null) this.onWifiSettings();
    },
    backToMainView() {
      this.uiView = viewTypeEnum.default;
      if (this.onDefaultView) this.onDefaultView(true);

      setTimeout(this.recalcScrollButtonVisiblity, 1000);
    },
    // Free account: keep the selected servers and hosts to ones it may use
    // (runs in the main process; for a Premium account it only drops a host
    // the app chose automatically). isBeforeConnect: a connect is about to start,
    // so it applies even while the current connection is still up.
    ensureUsableServers(isBeforeConnect) {
      this.$store.dispatch("settings/ensureUsableServers", {
        beforeConnect: isBeforeConnect === true,
      });
    },
    onServerChanged(server, isExitServer, serverHostName) {
      if (server == null || isExitServer == null) return;
      let hostId = null;
      if (serverHostName) {
        // serverHostName - not null when user selected specific host of the server
        hostId = serverHostName.split(".")[0];
      }

      // Free account: a Premium-only location or a Premium host cannot be used;
      // the server list shows the upgrade prompt for it, the selection stays
      if (this.isFreeAccount) {
        if (IsServerLocked(server, false)) return;
        if (hostId) {
          const host = (server.hosts || []).find((h) => HostId(h) === hostId);
          if (IsHostLocked(host, false)) return;
        }
      }

      // a host the app chose itself for a Free account counts as "no host chosen"
      // (settings/ensureUsableServers), so choosing the same location again changes nothing
      const settings = this.$store.state.settings;
      const entryHostId =
        settings.serverEntryHostIsAuto === true
          ? null
          : settings.serverEntryHostId;
      const exitHostId =
        settings.serverExitHostIsAuto === true
          ? null
          : settings.serverExitHostId;

      let needReconnect = false;
      if (!isExitServer) {
        if (
          !this.$store.state.settings.serverEntry ||
          this.$store.state.settings.serverEntry.gateway !== server.gateway ||
          entryHostId !== hostId ||
          this.$store.state.settings.isRandomServer !== false
        ) {
          this.$store.dispatch("settings/isRandomServer", false);
          this.$store.dispatch("settings/serverEntry", server);
          this.$store.dispatch("settings/serverEntryHostId", hostId);
          needReconnect = true;
        }
      } else {
        if (
          !this.$store.state.settings.serverExit ||
          this.$store.state.settings.serverExit.gateway !== server.gateway ||
          exitHostId !== hostId ||
          this.$store.state.settings.isRandomExitServer !== false
        ) {
          this.$store.dispatch("settings/isRandomExitServer", false);
          this.$store.dispatch("settings/serverExit", server);
          this.$store.dispatch("settings/serverExitHostId", hostId);
          needReconnect = true;
        }
      }
      if (this.$store.state.settings.isFastestServer !== false) {
        this.$store.dispatch("settings/isFastestServer", false);
        needReconnect = true;
      }

      if (needReconnect == true && (this.isConnecting || this.isConnected))
        connect(this, true);
    },
    onFastestServer() {
      this.$store.dispatch("settings/isFastestServer", true);
      if (this.isConnected) connect(this, true);
    },
    onRandomServer(isExitServer) {
      if (isExitServer === true)
        this.$store.dispatch("settings/isRandomExitServer", true);
      else this.$store.dispatch("settings/isRandomServer", true);
      if (this.isConnected) connect(this, true);
    },
    recalcScrollButtonVisiblity() {
      let sa = this.$refs.scrollArea;
      if (sa == null) {
        this.isShowScrollButton = false;
        return;
      }

      const isNeedToShow = function () {
        let pixelsToTheEndScroll =
          sa.scrollHeight - (sa.clientHeight + sa.scrollTop);
        // The plan card sits right under the cards, so even a few hidden pixels cut
        // the last card visibly: show the button unless (almost) nothing is hidden.
        if (pixelsToTheEndScroll < 4) return false;
        return true;
      };

      // hide - imediately; show - with 1sec delay
      if (!isNeedToShow()) this.isShowScrollButton = false;
      else {
        setTimeout(() => {
          this.isShowScrollButton = isNeedToShow();
        }, 1000);
      }
    },
    onScrollDown() {
      let sa = this.$refs.scrollArea;
      if (sa == null) return;
      sa.scrollTo({
        top: sa.scrollHeight,
        behavior: "smooth",
      });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

// Left panel (320 x 556 in the B design):
//   hero 292 (connected) | 60 server + 8 + 98 kill switch/protocol | 8 | 72 plan | 14
// Every card brings its own 16 px side margins (block-selected-server,
// block-connection-details, block-plan-bar); this file owns the vertical rhythm.
.controlView {
  min-height: 0;
}

.heroArea {
  flex: none;
}

.cardsArea {
  flex: 1 1 auto;
  min-height: 0;
  box-sizing: border-box;
  padding-bottom: 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between; // plan card at the bottom
  gap: 8px;
}

.scrollWrap {
  position: relative;
  flex: 0 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

div.cardsScroll {
  flex: 0 1 auto;
  min-height: 0;
  gap: 8px;
  // 3 px of room so focus rings are not clipped by the scrolling box,
  // taken back by the negative margin (no layout cost)
  padding: 3px 0;
  margin: -3px 0;
}
// cards keep their height; the box scrolls instead
div.cardsScroll > * {
  flex: none;
}

// the global button is 'position: fixed' to the window bottom; here it sits at the
// bottom of the visible cards, above the plan card. 28 px with a visible focus ring,
// like the server list's scroll button (the global one is 24 px without an outline).
button.btnScrollDown {
  position: absolute;
  bottom: 4px;
  left: calc(50% - 14px);
  width: 28px;
  height: 28px;
  margin: 0;
  box-sizing: border-box;
  border: 1px solid var(--control-border);
  background: var(--surface-color);
}
button.btnScrollDown svg {
  display: block;
  stroke: var(--text-soft);
}
button.btnScrollDown:hover {
  background: var(--neutral-tint);
}
button.btnScrollDown:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}
</style>
