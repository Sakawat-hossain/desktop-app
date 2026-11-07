<template>
  <div class="serversView">
    <!-- TOP: back | tabs (or the Fastest settings title), search | sort -->
    <div class="topArea">
      <div class="topRow">
        <button
          type="button"
          class="squareBtn backBtn"
          aria-label="Back"
          title="Back"
          v-on:click="goBack"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M19 12H5M11 6l-6 6 6 6" />
          </svg>
        </button>

        <div
          v-if="isFastestServerConfig === false"
          class="tabs"
          role="tablist"
          aria-label="Server lists"
          v-on:keydown="onTabsKeydown"
        >
          <button
            ref="tabAll"
            type="button"
            role="tab"
            class="tab"
            :class="{ active: !isFavoritesView }"
            :aria-selected="!isFavoritesView ? 'true' : 'false'"
            :tabindex="isFavoritesView ? -1 : 0"
            v-on:click="showAll"
          >
            All servers
          </button>
          <button
            ref="tabFav"
            type="button"
            role="tab"
            class="tab"
            :class="{ active: isFavoritesView }"
            :aria-selected="isFavoritesView ? 'true' : 'false'"
            :tabindex="isFavoritesView ? 0 : -1"
            v-on:click="showFavorites"
          >
            Favorites<span class="tabCount">{{ favorites.length }}</span>
          </button>
        </div>

        <div v-else class="configTitle">
          <span class="configTitleText">Fastest server settings</span>
        </div>
      </div>

      <div class="searchRow">
        <label class="searchField" :class="{ hasValue: !!filter }">
          <svg
            class="searchIcon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="6.5" />
            <path d="m20 20-4.2-4.2" />
          </svg>
          <input
            ref="filterInput"
            class="searchInput"
            type="text"
            placeholder="Search for a server"
            aria-label="Search for a server"
            spellcheck="false"
            autocomplete="off"
            v-model="filter"
            v-on:keydown.esc="onFilterEsc"
          />
          <button
            v-if="filter"
            type="button"
            class="clearBtn"
            aria-label="Clear search"
            title="Clear search"
            v-on:click.prevent="clearFilter"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke-width="2.2"
              stroke-linecap="round"
              aria-hidden="true"
            >
              <path d="M6 6l12 12M18 6 6 18" />
            </svg>
          </button>
        </label>

        <SortMenu :sortType="sortTypeStr" v-on:select="onSortType" />
      </div>
    </div>

    <!-- LIST -->
    <div class="listRegion" role="region" aria-label="Server list">
      <div ref="scrollArea" class="listScroll" v-on:scroll="onListScroll">
        <div ref="listContent" class="listContent">
          <!-- EMPTY FAVORITES -->
          <div v-if="isShowFavoriteDescriptionBlock" class="emptyState">
            <span class="emptyTile" aria-hidden="true">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                stroke-width="1.8"
                stroke-linejoin="round"
              >
                <path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z" />
              </svg>
            </span>
            <span class="emptyTitle">No favorites yet</span>
            <span class="emptyText"
              >Tap the star next to a location to keep it here.</span
            >
          </div>

          <template v-else>
            <p v-if="isFastestServerConfig" class="configNote">
              Turn off the locations Fastest server should never pick.
            </p>

            <!-- QUICK CONNECT: Fastest (+ its settings) and Random -->
            <section
              v-if="isShowQuickConnect"
              class="section"
              aria-labelledby="srvQcTitle"
            >
              <h2 id="srvQcTitle" class="sectionTitle">Quick connect</h2>
              <div class="qcGrid" :class="{ qcSingle: isMultihop }">
                <div
                  v-if="!isMultihop"
                  class="qcCard"
                  :class="{ current: isFastestInUse }"
                >
                  <button
                    type="button"
                    class="qcMain"
                    :aria-current="isFastestInUse ? 'true' : null"
                    v-on:click="onFastestServerClicked()"
                  >
                    <span class="qcTile qcTileAccent" aria-hidden="true">
                      <svg
                        width="15"
                        height="15"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M13 2 4 14h7l-1 8 9-12h-7z" />
                      </svg>
                    </span>
                    <span class="qcTexts">
                      <span class="qcTitle">Fastest</span>
                      <span class="qcSub">Best ping</span>
                    </span>
                  </button>
                  <button
                    type="button"
                    class="qcGear"
                    aria-label="Fastest server settings"
                    title="Fastest server settings"
                    v-on:click="onFastestServerConfig()"
                  >
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      aria-hidden="true"
                    >
                      <circle cx="12" cy="12" r="3" />
                      <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
                    </svg>
                  </button>
                </div>

                <div class="qcCard" :class="{ current: isRandomInUse }">
                  <button
                    type="button"
                    class="qcMain"
                    :aria-current="isRandomInUse ? 'true' : null"
                    v-on:click="onRandomServerClicked()"
                  >
                    <span class="qcTile" aria-hidden="true">
                      <svg
                        width="15"
                        height="15"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5" />
                      </svg>
                    </span>
                    <span class="qcTexts">
                      <span class="qcTitle">Random</span>
                      <span class="qcSub">Any location</span>
                    </span>
                  </button>
                </div>
              </div>
            </section>

            <!-- LOCATIONS -->
            <section class="section" aria-labelledby="srvListTitle">
              <div class="listHead">
                <h2 id="srvListTitle" class="sectionTitle">
                  {{ listTitle
                  }}<span class="countChip">{{ filteredServers.length }}</span>
                </h2>
                <span class="sortedBy">Sorted by {{ sortTypeLower }}</span>
              </div>

              <div
                v-if="filteredServers.length === 0"
                class="emptyState emptySmall"
              >
                <span class="emptyTitle">{{ noResultsText }}</span>
                <button
                  v-if="filter"
                  type="button"
                  class="linkBtn"
                  v-on:click="clearFilter"
                >
                  Clear search
                </button>
              </div>

              <div v-else class="rows">
                <template v-for="item of listItems" :key="item.key">
                  <div
                    v-if="item.isGroup"
                    class="groupHead"
                    :class="{ groupHeadFlat: isFastestServerConfig }"
                    role="heading"
                    aria-level="3"
                  >
                    <span class="groupTitle">{{ item.title }}</span>
                    <span class="groupLine" aria-hidden="true"></span>
                  </div>

                  <!-- Fastest server settings: switches that exclude locations -->
                  <FastestRow
                    v-else-if="isFastestServerConfig"
                    :server="item.server"
                    :isOn="!isSvrExcludedFomFastest(item.server)"
                    v-on:toggle="configFastestSvrClicked"
                  />

                  <LocationRow
                    v-else
                    :entry="item.server"
                    :isExitServer="isExitServer"
                    :isSelected="isEntrySelected(item.server)"
                    :selectedHostId="selectedHostIdFor(item.server)"
                    :canExpand="isServerHostsExpanded(item.server) !== undefined"
                    :isExpanded="isServerHostsExpanded(item.server) === true"
                    :upgradeKey="upgradeKey"
                    v-on:select="onServerSelected"
                    v-on:select-host="onServerHostSelected"
                    v-on:toggle-expand="onServerExpandClick"
                    v-on:favorite="favoriteClicked"
                    v-on:toggle-upgrade="onToggleUpgrade"
                    v-on:close-upgrade="onCloseUpgrade"
                  />
                </template>
              </div>
            </section>
          </template>
        </div>
      </div>

      <!-- thin scroll indicator (the native scrollbar would take width from the rows);
           positioned by updateThumb() directly, so scrolling does not re-render the list -->
      <span ref="thumb" class="scrollThumb" aria-hidden="true"></span>

      <!-- SCROLL DOWN BUTTON -->
      <transition name="fade">
        <button
          v-if="isShowScrollButton"
          type="button"
          class="scrollDownBtn"
          aria-label="Scroll down"
          title="Scroll down"
          v-on:click="onScrollDown()"
        >
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
  </div>
</template>

<script>
const sender = window.ipcSender;
import LocationRow from "@/components/servers/servers-location-row.vue";
import FastestRow from "@/components/servers/servers-fastest-row.vue";
import SortMenu from "@/components/servers/servers-sort-menu.vue";
import { enumValueName, getDistanceFromLatLonInKm } from "@/helpers/helpers";
import {
  CheckIsInaccessibleServer,
  CheckAndNotifyInaccessibleServer,
} from "@/helpers/helpers_servers";
import {
  IsHostLocked,
  IsServerLocked,
  HostDisplayName,
  HostId,
} from "@/helpers/helpers_premium";
import {
  GatewayId,
  EntryLocation,
  EntryPing,
  IsEntryLocked,
  UpgradeKeyForEntry,
  UpgradeKeyForHost,
  UpgradeCardDomId,
  IsPremiumAccountFor,
} from "@/components/servers/servers-helpers";
import { ServersSortTypeEnum, VpnStateEnum } from "@/store/types";

export default {
  props: [
    "onBack",
    "onServerChanged",
    "isExitServer",
    "onFastestServer",
    "onRandomServer",
  ],
  components: {
    LocationRow,
    FastestRow,
    SortMenu,
  },
  data: function () {
    return {
      filter: "",
      isFastestServerConfig: false,
      isShowScrollButton: false,
      expandedGateways: [], // list of server.gateway strings (list of gateways which is expanded to show server hosts)
      // key of the open upgrade card (Free account clicked a locked row); one at a time
      upgradeKey: null,
    };
  },
  created() {
    // the selected location opens with its hosts shown when the user chose a host of it
    // (not when the app picked the host for a Free account: "...HostIsAuto")
    const settings = this.$store.state.settings;
    const isAutoHost = this.isExit
      ? settings.serverExitHostIsAuto === true
      : settings.serverEntryHostIsAuto === true;
    const sel = this.markedServer;
    if (sel && this.markedHostId && !isAutoHost) {
      const svr = (this.servers || []).find(
        (s) => s && GatewayId(s.gateway) === GatewayId(sel.gateway),
      );
      if (svr && this.isServerHostsExpanded(svr) === false)
        this.expandedGateways.push(svr.gateway);
    }
  },
  mounted() {
    this.recalcScrollButtonVisiblity();
    this.resizeObserver = new ResizeObserver(this.recalcScrollButtonVisiblity);
    this.resizeObserver.observe(this.$refs.scrollArea);
    if (this.$refs.listContent)
      this.resizeObserver.observe(this.$refs.listContent);
  },
  // the list changed (rows expanded, an upgrade card, a search...): the
  // ResizeObserver alone does not always report it
  updated() {
    this.recalcScrollButtonVisiblity();
  },
  beforeUnmount() {
    if (this.resizeObserver) this.resizeObserver.disconnect();
    this.resizeObserver = null;
  },
  watch: {
    filter() {
      this.upgradeKey = null;
    },
    isFavoritesView() {
      this.upgradeKey = null;
    },
  },
  computed: {
    isFavoritesView: function () {
      return this.$store.state.uiState.serversFavoriteView;
    },
    isMultihop: function () {
      return this.$store.state.settings.isMultiHop;
    },
    isExit: function () {
      return (
        this.isExitServer != null &&
        this.isExitServer !== false &&
        this.isExitServer !== "false"
      );
    },
    // nothing is locked until the account status is known
    isPremiumAccount: function () {
      return IsPremiumAccountFor(this.$store.getters);
    },
    isShowFavoriteDescriptionBlock: function () {
      return this.isFavoritesView === true && this.favorites.length == 0;
    },
    isShowQuickConnect: function () {
      return this.isFavoritesView == false && this.isFastestServerConfig === false;
    },
    servers: function () {
      return this.$store.getters["vpnState/activeServers"];
    },

    sortTypeStr: function () {
      return (
        enumValueName(
          ServersSortTypeEnum,
          this.$store.state.settings.serversSortType,
        ) || "City"
      );
    },
    sortTypeLower: function () {
      return String(this.sortTypeStr).toLowerCase();
    },

    favorites: function () {
      // Favorite servers and hosts for current protocol
      return this.$store.getters["settings/favoriteServersAndHosts"] || [];
    },

    // "Fastest" / "Random" mode of this list (entry list: Fastest or Random; exit list: Random)
    isFastestInUse: function () {
      if (this.isExit) return false;
      return this.$store.getters["settings/isFastestServer"] === true;
    },
    isRandomInUse: function () {
      if (this.isExit)
        return this.$store.getters["settings/isRandomExitServer"] === true;
      if (this.isFastestInUse) return false;
      return this.$store.getters["settings/isRandomServer"] === true;
    },
    // The server marked as selected/connected in the list.
    // In the Fastest/Random modes the server is picked on connect, so the server in
    // settings is the one in use only while connected (same rule as the server card).
    markedServer: function () {
      const settings = this.$store.state.settings;
      const s = this.isExit ? settings.serverExit : settings.serverEntry;
      if (!s) return null;
      if (this.isFastestInUse || this.isRandomInUse) {
        const vpn = this.$store.state.vpnState;
        if (vpn.connectionState === VpnStateEnum.DISCONNECTED) return null;
        if (
          vpn.connectionState !== VpnStateEnum.CONNECTED &&
          vpn.isPingingServers === true
        )
          return null;
      }
      return s;
    },
    markedHostId: function () {
      if (!this.markedServer) return null;
      const settings = this.$store.state.settings;
      const id = this.isExit
        ? settings.serverExitHostId
        : settings.serverEntryHostId;
      return id ? String(id).split(".")[0] : null;
    },

    filteredServers: function () {
      let store = this.$store;
      let sType = store.state.settings.serversSortType;
      const funcGetPing = this.$store.getters["vpnState/funcGetPing"];
      const isPremiumAccount = this.isPremiumAccount;
      function compare(a, b) {
        switch (sType) {
          case ServersSortTypeEnum.City: {
            const ac = a.city || "";
            const bc = b.city || "";
            return ac.localeCompare(bc);
          }

          case ServersSortTypeEnum.Country: {
            if (!a.country && !b.country) return 0;
            if (!a.country) return 1;
            if (!b.country) return -1;

            let ret = 0;
            ret = a.country.localeCompare(b.country);
            if (ret != 0) return ret;
            // If countries are the same - compare cities
            if (a.city && b.city) return a.city.localeCompare(b.city);
            return ret;
          }

          case ServersSortTypeEnum.Latency: {
            // the latency the row shows (a Free account: usable hosts only)
            const aPing = EntryPing(a, funcGetPing, isPremiumAccount);
            const bPing = EntryPing(b, funcGetPing, isPremiumAccount);
            if (aPing && bPing) return aPing - bPing;
            if (aPing && !bPing) return -1;
            if (!aPing && bPing) return 1;
            return 0;
          }

          case ServersSortTypeEnum.Proximity: {
            const l = store.getters["getLastRealLocation"];
            if (l == null) return 0;

            var distA = getDistanceFromLatLonInKm(
              l.latitude,
              l.longitude,
              a.latitude,
              a.longitude,
            );
            var distB = getDistanceFromLatLonInKm(
              l.latitude,
              l.longitude,
              b.latitude,
              b.longitude,
            );

            if (distA === distB) return 0;
            if (distA < distB) return -1;

            return 1;
          }
        }
        return 0;
      }

      function serverToSkip() {
        // For Multi-Hop:
        // -skip entry-server for exit server selection
        // -skip exit-server for entry server selection
        if (!this.isMultihop) return null;
        if (this.isExitServer) {
          if (!this.$store.state.settings.isRandomServer)
            return this.$store.state.settings.serverEntry;
        } else {
          if (!this.$store.state.settings.isRandomExitServer)
            return this.$store.state.settings.serverExit;
        }
        return null;
      }

      let servers = this.servers || [];
      if (this.isFavoritesView) servers = this.favorites;

      let svrToSkip = serverToSkip.bind(this)();

      let filter = this.filter.trim().toLowerCase();
      const has = (v) => !!v && String(v).toLowerCase().includes(filter);
      let filtered = servers.filter((s) => {
        if (!s) return false;
        if (s.gateway === svrToSkip?.gateway) return false;
        if (!filter) return true;
        if (s.favHost) {
          // favourite host: its display name (and, as before, its hostname)
          if (has(HostDisplayName(EntryLocation(s), s.favHost))) return true;
          if (has(s.favHost.hostname)) return true;
        } else if (Array.isArray(s.hosts)) {
          // a location also matches by the display name of one of its hosts
          if (s.hosts.some((h) => h && has(HostDisplayName(s, h)))) return true;
        }
        return has(s.city) || has(s.country) || has(s.country_code);
      });

      return filtered.slice().sort(compare);
    },

    // rows of the list: country headers (sorted by Country) + entries
    listItems: function () {
      const grouped = this.sortTypeStr === "Country";
      const ret = [];
      let lastGroup = null;
      for (const s of this.filteredServers) {
        if (grouped) {
          const loc = EntryLocation(s) || s;
          const g = String(loc.country || "").trim() || "Other";
          if (g !== lastGroup) {
            ret.push({ isGroup: true, key: "group:" + g, title: g });
            lastGroup = g;
          }
        }
        ret.push({ isGroup: false, key: s.gateway, server: s });
      }
      return ret;
    },

    listTitle: function () {
      if (this.isFastestServerConfig) return "Locations";
      if (this.isFavoritesView) return "Favorites";
      return "All locations";
    },
    noResultsText: function () {
      const f = this.filter.trim();
      if (f) return `No locations match “${f}”`;
      return "No locations to show";
    },
  },

  methods: {
    goBack: function () {
      if (this.isFastestServerConfig) {
        this.filter = "";
        this.isFastestServerConfig = false;
        this.scrollToTop();
        return;
      }
      if (this.onBack != null) this.onBack();
    },

    // undefined: the location has no expand chevron
    isServerHostsExpanded: function (server) {
      if (
        this.$store.state.settings.showHosts !== true ||
        this.isFastestServerConfig === true ||
        this.$store.state.uiState.serversFavoriteView === true
      )
        return undefined; //hide expand button
      // a favourite host, or a location with a single host: nothing to expand
      if (!server || server.favHost) return undefined;
      if (!Array.isArray(server.hosts) || server.hosts.length < 2)
        return undefined;
      return this.expandedGateways.includes(server.gateway);
    },
    onServerExpandClick: function (server) {
      var index = this.expandedGateways.indexOf(server.gateway);
      if (index === -1) this.expandedGateways.push(server.gateway);
      else this.expandedGateways.splice(index, 1);

      setTimeout(() => {
        this.recalcScrollButtonVisiblity();
      }, 0);
    },

    // the row is the selected / connected location (or favourite host)
    isEntrySelected: function (entry) {
      const sel = this.markedServer;
      if (!sel || !entry) return false;
      if (entry.favHost) {
        const parent = entry.favHostParentServerObj;
        return (
          !!parent &&
          GatewayId(parent.gateway) === GatewayId(sel.gateway) &&
          !!this.markedHostId &&
          HostId(entry.favHost) === this.markedHostId
        );
      }
      return GatewayId(entry.gateway) === GatewayId(sel.gateway);
    },
    selectedHostIdFor: function (entry) {
      if (!entry || entry.favHost) return null;
      if (!this.isEntrySelected(entry)) return null;
      return this.markedHostId || null;
    },

    checkAndNotifyInaccessibleServer: async function (server, host = null) {
      return CheckAndNotifyInaccessibleServer(this.isExitServer, server, host);
    },
    // isInaccessibleServer returns:
    // - null if server is acceptble
    // - object { sameGateway: true } - servers have same gateway
    // - object { sameCountry: true } - servers are from same country (only if this.$store.state.settings.multihopWarnSelectSameCountries === true)
    // - objext { sameISP: true }     - servers are operated by same ISP (only if this.$store.state.settings.multihopWarnSelectSameISPs === true)
    isInaccessibleServer: function (server, host = null) {
      return CheckIsInaccessibleServer(this.isExitServer, server, host);
    },

    onServerSelected: async function (server) {
      if (server.favHost) {
        return this.onServerHostSelected(
          server.favHostParentServerObj,
          server.favHost,
        );
      }
      // Free account: a Premium-only location is not selected; the upgrade card opens instead
      if (IsServerLocked(server, this.isPremiumAccount)) {
        this.onToggleUpgrade(UpgradeKeyForEntry(server));
        return;
      }
      if ((await this.checkAndNotifyInaccessibleServer(server)) == false)
        return;
      this.onServerChanged(server, this.isExitServer != null);
      this.onBack();
    },
    onServerHostSelected: async function (server, host) {
      // Free account: a Premium host is not selected; the upgrade card opens instead
      if (IsHostLocked(host, this.isPremiumAccount)) {
        this.onToggleUpgrade(UpgradeKeyForHost(server, host));
        return;
      }
      if ((await this.checkAndNotifyInaccessibleServer(server, host)) == false)
        return;
      this.onServerChanged(server, this.isExitServer != null, host.hostname);
      this.onBack();
    },

    onToggleUpgrade: function (key) {
      this.upgradeKey = this.upgradeKey === key ? null : key;
      if (!this.upgradeKey) return;
      // keep the card in view when it opens near the bottom of the list
      this.$nextTick(() => {
        const el = document.getElementById(UpgradeCardDomId(this.upgradeKey));
        if (el && el.scrollIntoView)
          el.scrollIntoView({ block: "nearest", behavior: "smooth" });
      });
    },
    onCloseUpgrade: function () {
      this.upgradeKey = null;
    },

    onSortType: function (sortTypeStr) {
      this.$store.dispatch(
        "settings/serversSortType",
        ServersSortTypeEnum[sortTypeStr],
      );
    },
    onFastestServerClicked() {
      if (this.onFastestServer != null) this.onFastestServer();
      this.onBack();
    },
    onRandomServerClicked() {
      if (this.onRandomServer != null) this.onRandomServer();
      this.onBack();
    },
    isSvrExcludedFomFastest: function (server) {
      const sGwId = GatewayId(server.gateway);
      const found = this.$store.state.settings.serversFastestExcludeList.find(
        (excGw) => sGwId == GatewayId(excGw),
      );
      return found != undefined;
    },
    onFastestServerConfig() {
      this.isFastestServerConfig = true;
      this.filter = "";
      this.upgradeKey = null;
      this.scrollToTop();
    },

    favoriteClicked: function (evt, server, host) {
      if (evt) evt.stopPropagation();
      if (!server && !host) return;

      if (server.favHost) {
        return this.favoriteClicked(
          evt,
          server.favHostParentServerObj,
          server.favHost,
        );
      }
      const settings = this.$store.state.settings;
      const store = this.$store;

      if (!host) {
        // favorite SERVER
        let gatewayId = server.gateway.split(".")[0]; // only gateway ID in use for serversFavoriteList ("us-tx.wg.ivpn.net" => "us-tx")
        let favorites = settings.serversFavoriteList.slice();

        if (!favorites.includes(gatewayId)) {
          console.log(`Adding favorite location ${gatewayId}`);
          favorites.push(gatewayId);
        } else {
          console.log(`Removing favorite location ${gatewayId}`);
          favorites = favorites.filter((gw) => gw != gatewayId);

          // If the server has only one host AND this host is in favorites -> remove host also
          // Reason: If server and it's single host are in favorites - we showing only server to user.
          // (refer to "settings/favoriteServersAndHosts" for details)
          if (server.hosts.length == 1) {
            // remove HOST also
            let hostDns = server.hosts[0].dns_name;
            let favHostsDns = settings.hostsFavoriteListDnsNames.slice();
            if (favHostsDns.includes(hostDns)) {
              console.log(`Removing favorite host ${hostDns} (single host)`);
              favHostsDns = favHostsDns.filter((hn) => hn != hostDns);
              store.dispatch("settings/hostsFavoriteListDnsNames", favHostsDns);
            }
          }
        }
        store.dispatch("settings/serversFavoriteList", favorites);
      } else if (host.hostname) {
        // favorite HOST
        let favHostsDns = settings.hostsFavoriteListDnsNames.slice();
        let hostDns = host.dns_name;

        if (!favHostsDns.includes(hostDns)) {
          // add host
          console.log(`Adding favorite host ${hostDns}`);
          favHostsDns.push(hostDns);
        } else {
          // remove host
          console.log(`Removing favorite host ${hostDns}`);
          favHostsDns = favHostsDns.filter((hn) => hn != hostDns);
        }
        store.dispatch("settings/hostsFavoriteListDnsNames", favHostsDns);
      }
    },
    configFastestSvrClicked(server, event) {
      if (server == null || server.gateway == null) return;
      let excludeSvrs =
        this.$store.state.settings.serversFastestExcludeList.slice();

      // work only with Gateway ID (not with full gateway name). We need it to have common 'serversFastestExcludeList' for all protocols
      const sGwId = GatewayId(server.gateway);
      excludeSvrs = excludeSvrs.map((el) => {
        return GatewayId(el);
      });

      if (excludeSvrs.includes(sGwId))
        excludeSvrs = excludeSvrs.filter((gw) => gw != sGwId);
      else excludeSvrs.push(sGwId);

      const activeServers = (this.servers || []).slice();
      const notExcludedActiveServers = activeServers.filter(
        (s) => !excludeSvrs.includes(GatewayId(s.gateway)),
      );

      if (notExcludedActiveServers.length < 1) {
        sender.showMessageBoxSync({
          type: "info",
          buttons: ["OK"],
          message: "Please, keep at least one server",
          detail: "Not allowed to exclude all servers.",
        });
        if (event) event.preventDefault();
        return;
      }
      // a Free account: Fastest can only pick a location the account may use
      if (
        !this.isPremiumAccount &&
        !notExcludedActiveServers.some((s) => !IsEntryLocked(s, false))
      ) {
        sender.showMessageBoxSync({
          type: "info",
          buttons: ["OK"],
          message: "Please, keep at least one Free server",
          detail: "Fastest server can only pick locations your plan can use.",
        });
        if (event) event.preventDefault();
        return;
      }
      this.$store.dispatch("settings/serversFastestExcludeList", excludeSvrs);
    },

    showFavorites: function () {
      this.$store.dispatch("uiState/serversFavoriteView", true);
      this.filter = "";

      setTimeout(() => {
        this.recalcScrollButtonVisiblity();
      }, 500);
    },
    showAll: function () {
      this.$store.dispatch("uiState/serversFavoriteView", false);
      this.filter = "";

      setTimeout(() => {
        this.recalcScrollButtonVisiblity();
      }, 500);
    },
    // arrow keys move between the two tabs (and select, as the tabs switch at once)
    onTabsKeydown: function (e) {
      let toFavorites = null;
      switch (e.key) {
        case "ArrowLeft":
        case "Home":
          toFavorites = false;
          break;
        case "ArrowRight":
        case "End":
          toFavorites = true;
          break;
        default:
          return;
      }
      e.preventDefault();
      if (toFavorites) this.showFavorites();
      else this.showAll();
      this.$nextTick(() => {
        const t = toFavorites ? this.$refs.tabFav : this.$refs.tabAll;
        if (t) t.focus();
      });
    },

    clearFilter: function () {
      this.filter = "";
      if (this.$refs.filterInput) this.$refs.filterInput.focus();
    },
    onFilterEsc: function (e) {
      if (!this.filter) return;
      e.stopPropagation();
      this.filter = "";
    },

    scrollToTop: function () {
      const sa = this.$refs.scrollArea;
      if (sa) sa.scrollTop = 0;
    },
    onListScroll: function () {
      this.recalcScrollButtonVisiblity();
    },
    // not reactive data: a scroll only moves this one element
    updateThumb: function () {
      const sa = this.$refs.scrollArea;
      const el = this.$refs.thumb;
      if (!el) return;
      let t = { visible: false, top: 0, height: 0 };
      if (sa) {
        const ch = sa.clientHeight;
        const sh = sa.scrollHeight;
        if (sh > ch + 1 && ch > 8) {
          const track = ch - 4; // 2 px from the top and the bottom
          const h = Math.max(24, Math.round((track * ch) / sh));
          const maxTop = Math.max(1, sh - ch);
          const top =
            2 + Math.round(((track - h) * Math.min(sa.scrollTop, maxTop)) / maxTop);
          t = { visible: true, top, height: h };
        }
      }
      const display = t.visible ? "block" : "none";
      if (el.style.display !== display) el.style.display = display;
      if (!t.visible) return;
      const top = t.top + "px";
      const height = t.height + "px";
      if (el.style.top !== top) el.style.top = top;
      if (el.style.height !== height) el.style.height = height;
    },
    recalcScrollButtonVisiblity() {
      this.updateThumb();

      let sa = this.$refs.scrollArea;
      if (sa == null) {
        this.isShowScrollButton = false;
        return;
      }

      // more than the list's bottom padding is hidden
      const isNeedToShow = () =>
        sa.scrollHeight - (sa.clientHeight + sa.scrollTop) > 12;

      // hide - immediately; show - with 1sec delay
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
        top: sa.clientHeight * 0.9 + sa.scrollTop, //sa.scrollHeight,
        behavior: "smooth",
      });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

// R4F server list: 320 px panel, 14 px side padding (rows are 292 px wide)
.serversView {
  // colours used by components/servers/* (light theme here, dark theme below)
  --srv-moderate: #9a4a06; // latency 100-299 ms
  --srv-bar-off: #d4d4d8;
  --srv-free-border: #bfe3cb;
  --srv-tree-line: #d4d4d8;
  --srv-flag-outline: rgba(0, 0, 0, 0.12);
  --srv-thumb: #d4d4d8;
  --srv-menu-shadow: 0.14;

  @media (prefers-color-scheme: dark) {
    --srv-moderate: #fdba74;
    --srv-bar-off: #3a3a40;
    --srv-free-border: #1f3d2a;
    --srv-tree-line: #3a3a40;
    --srv-flag-outline: rgba(255, 255, 255, 0.18);
    --srv-thumb: #2e2e34;
    --srv-menu-shadow: 0.55;
  }

  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

// the global 'html * { color }' rule stops currentColor from inheriting
svg,
svg * {
  color: inherit;
}
button {
  margin: 0;
  font-family: inherit;
}
button:focus {
  outline: none;
}

// ---------- top ----------
.topArea {
  flex: none;
  position: relative;
  z-index: 2; // the sort menu opens over the list
  box-sizing: border-box;
  padding: 14px 14px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.topRow {
  height: 36px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.squareBtn {
  width: 36px;
  height: 36px;
  flex: none;
  padding: 0;
  box-sizing: border-box;
  border: 1px solid var(--control-border);
  border-radius: 10px;
  background: var(--surface-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.15s;
}
.squareBtn svg {
  display: block;
  stroke: var(--text-soft);
}
.squareBtn:hover {
  background: var(--neutral-tint);
}
.squareBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}

.tabs {
  flex: 1;
  min-width: 0;
  height: 36px;
  box-sizing: border-box;
  padding: 3px;
  border: 1px solid var(--surface-border);
  border-radius: 10px;
  background: var(--surface-color);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 3px;
}
.tab {
  height: 28px;
  min-width: 0;
  padding: 0 4px;
  box-sizing: border-box;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  line-height: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: color 0.15s, background-color 0.15s;
}
.tab:hover:not(.active) {
  color: var(--text-color);
}
.tab.active {
  border-color: var(--accent-ring);
  background: var(--accent-tint);
  color: var(--link-color);
  font-weight: 600;
}
.tab:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 0;
}
.tabCount {
  min-width: 18px;
  height: 16px;
  box-sizing: border-box;
  padding: 0 5px;
  border-radius: 8px;
  background: var(--neutral-tint);
  color: var(--text-muted);
  font-size: 10.5px;
  font-weight: 600;
  line-height: 16px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}
.tab.active .tabCount {
  background: var(--accent-ring);
  color: var(--text-color);
}

.configTitle {
  flex: 1;
  min-width: 0;
  height: 36px;
  display: flex;
  align-items: center;
}
.configTitleText {
  font-size: 14px;
  font-weight: 600;
  line-height: 18px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.searchRow {
  height: 38px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.searchField {
  flex: 1;
  min-width: 0;
  height: 38px;
  box-sizing: border-box;
  padding: 0 12px;
  border: 1px solid var(--control-border);
  border-radius: 10px;
  background: var(--surface-color);
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: text;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.searchField.hasValue {
  padding-right: 4px;
}
.searchField:focus-within {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 1px var(--accent-color);
}
.searchIcon {
  display: block;
  flex: none;
  stroke: var(--text-faint);
}
.searchInput {
  flex: 1;
  min-width: 0;
  height: 36px;
  margin: 0;
  padding: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text-color);
  font-family: inherit;
  font-size: 13px;
  line-height: 18px;
  -webkit-user-select: text;
  user-select: text;
}
.searchInput::placeholder {
  color: var(--text-faint);
  opacity: 1;
}
.clearBtn {
  width: 28px;
  height: 28px;
  flex: none;
  padding: 0;
  border: 0;
  border-radius: 7px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.clearBtn svg {
  display: block;
  stroke: var(--text-muted);
}
.clearBtn:hover {
  background: var(--neutral-tint);
}
.clearBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}

// ---------- list ----------
.listRegion {
  position: relative;
  z-index: 1; // below the top area, so the sort menu covers the whole list
  flex: 1 1 0;
  min-height: 0;
  margin-top: 10px;
}
.listScroll {
  position: absolute;
  inset: 0;
  overflow-x: hidden;
  overflow-y: auto;
  scrollbar-width: none;
}
.listScroll::-webkit-scrollbar {
  display: none;
}
.listContent {
  box-sizing: border-box;
  padding: 2px 14px 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.configNote {
  margin: 0;
  font-size: 11.5px;
  line-height: 16px;
  color: var(--text-muted);
}

.section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sectionTitle {
  margin: 0;
  height: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  line-height: 16px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-faint);
  white-space: nowrap;
}
.countChip {
  padding: 0 5px;
  border-radius: 4px;
  background: var(--neutral-tint);
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 600;
  line-height: 14px;
  letter-spacing: 0;
  font-variant-numeric: tabular-nums;
}
.listHead {
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.sortedBy {
  font-size: 11px;
  line-height: 16px;
  color: var(--text-faint);
  white-space: nowrap;
}

// QUICK CONNECT
.qcGrid {
  height: 52px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}
.qcGrid.qcSingle {
  grid-template-columns: minmax(0, 1fr);
}
.qcCard {
  min-width: 0;
  box-sizing: border-box;
  padding: 0 3px 0 10px;
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  background: var(--surface-color);
  display: flex;
  align-items: center;
  gap: 2px;
  transition: background-color 0.15s, border-color 0.15s;
}
.qcCard:not(.current):hover {
  background: var(--neutral-tint);
}
.qcCard.current {
  border-color: var(--accent-ring);
  background: var(--accent-tint);
}
.qcCard:has(> .qcMain:focus-visible) {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}
.qcMain {
  flex: 1;
  min-width: 0;
  height: 50px;
  padding: 0;
  border: 0;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 8px;
  text-align: left;
  cursor: pointer;
}
.qcTile {
  width: 28px;
  height: 28px;
  flex: none;
  box-sizing: border-box;
  border: 1px solid var(--control-border);
  border-radius: 8px;
  background: var(--neutral-tint);
  display: flex;
  align-items: center;
  justify-content: center;
}
.qcTile svg {
  display: block;
  stroke: var(--text-soft);
}
.qcTileAccent {
  border-color: var(--accent-ring);
  background: var(--accent-tint);
}
.qcTileAccent svg {
  stroke: var(--link-color);
}
.qcTexts {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.qcTitle {
  font-size: 13px;
  font-weight: 600;
  line-height: 17px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.qcSub {
  font-size: 11px;
  line-height: 14px;
  color: var(--text-faint);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.qcGear {
  width: 28px;
  height: 28px;
  flex: none;
  padding: 0;
  border: 0;
  border-radius: 7px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.qcGear svg {
  display: block;
  stroke: var(--text-muted);
}
.qcGear:hover {
  background: var(--neutral-tint);
}
.qcGear:hover svg {
  stroke: var(--text-color);
}
.qcGear:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}

// LOCATIONS
.rows {
  display: flex;
  flex-direction: column;
}
// the text starts where the flags of the rows start (27 px)
.groupHead {
  height: 22px;
  flex: none;
  box-sizing: border-box;
  padding: 0 10px 0 27px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.groupHead.groupHeadFlat {
  padding-left: 11px;
}
.groupTitle {
  min-width: 0;
  display: block;
  font-size: 10px;
  font-weight: 600;
  line-height: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-faint);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.groupLine {
  flex: 1;
  min-width: 12px;
  height: 1px;
  display: block;
  background: var(--surface-divider);
}

// EMPTY STATES
.emptyState {
  box-sizing: border-box;
  padding: 44px 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-align: center;
}
.emptyState.emptySmall {
  padding-top: 20px;
}
.emptyTile {
  width: 44px;
  height: 44px;
  margin-bottom: 6px;
  box-sizing: border-box;
  border: 1px solid var(--accent-ring);
  border-radius: 12px;
  background: var(--accent-tint);
  display: flex;
  align-items: center;
  justify-content: center;
}
.emptyTile svg {
  display: block;
  fill: var(--accent-color);
  stroke: var(--accent-color);
}
.emptyTitle {
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  overflow-wrap: anywhere;
}
.emptyText {
  max-width: 230px;
  font-size: 12px;
  line-height: 17px;
  color: var(--text-muted);
}
.linkBtn {
  height: 28px;
  padding: 0 8px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--link-color);
  font-size: 12.5px;
  font-weight: 600;
  line-height: 16px;
  cursor: pointer;
}
.linkBtn:hover {
  background: var(--neutral-tint);
}
.linkBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 0;
}

// SCROLL
.scrollThumb {
  position: absolute;
  z-index: 1;
  right: 4px;
  width: 4px;
  display: none; // shown by updateThumb()
  border-radius: 2px;
  background: var(--srv-thumb);
  pointer-events: none;
}
.scrollDownBtn {
  position: absolute;
  z-index: 3;
  bottom: 10px;
  left: calc(50% - 14px);
  width: 28px;
  height: 28px;
  padding: 0;
  box-sizing: border-box;
  border: 1px solid var(--control-border);
  border-radius: 50%;
  background: var(--surface-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, var(--srv-menu-shadow));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.scrollDownBtn svg {
  display: block;
  stroke: var(--text-soft);
}
.scrollDownBtn:hover {
  background: var(--neutral-tint);
}
.scrollDownBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}
</style>
