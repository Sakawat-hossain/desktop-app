<template>
  <div id="main">
    <!-- Popup -->
    <div class="popup">
      <div
        ref="popup"
        class="popuptext"
        v-bind:class="{
          show:
            isPopupVisible &&
            isMapLoaded &&
            isInProgress == false &&
            isBlured !== 'true',
        }"
      >
        <popupControl
          :location="selectedPopupLocation"
          :onConnect="connect"
          :onDisconnect="disconnect"
          :onMouseClick="onPopupMouseClick"
          :onResume="resume"
        />
      </div>
    </div>

    <!--
      The map tool buttons (Hide map, Settings, Account, Center map) live in the window title bar
      (views/Component-Main.vue). It calls this component's centerCurrentLocation() through a template ref.
    -->

    <!-- Bottom panel: account notices + the "Connection details" card -->
    <div class="bottomPanel" ref="bottomPanel">
      <div
        class="accountWillExpire"
        v-if="$store.getters['account/messageAccountExpiration']"
      >
        <img src="@/assets/alert-triangle.svg" style="margin-right: 12px" />
        {{ $store.getters["account/messageAccountExpiration"] }}
        <div class="flexRowRestSpace" />
        <button class="noBordersBtn" v-on:click="onAccountRenew()">
          RENEW
        </button>
      </div>
      <div
        class="trialWillExpire"
        v-on:click="onAccountRenew()"
        v-if="$store.getters['account/messageFreeTrial']"
      >
        <img src="@/assets/alert-circle.svg" style="margin-right: 12px" />
        {{ $store.getters["account/messageFreeTrial"] }}
        <div class="flexRowRestSpace" />
        <button class="noBordersBtn">UPGRADE</button>
      </div>

      <section class="detailsCard" aria-label="Connection details">
        <transition name="fade">
          <!-- (it comes with the move into the connected country, after the connection effect) -->
          <div
            v-if="
              isConnected &&
              !$store.getters['vpnState/isPaused'] &&
              !isFxHolding
            "
            class="speedSection"
          >
            <BlockSpeedGraph />
            <div class="cardDivider" aria-hidden="true"></div>
          </div>
        </transition>
        <GeolocationInfoControl />
      </section>
    </div>
    <!-- Map -->
    <!-- (any scroll of the map, a drag, a move or a zoom, places the user's card again) -->
    <div class="mapcontainer" ref="combined" @scroll.passive="onMapScroll">
      <canvas
        class="canvas"
        ref="canvas"
        v-bind:class="{ blured: isBlured === 'true' }"
        @mousedown="mouseDown"
        @mouseup="mouseUp"
        @mousemove="mouseMove"
        @wheel="wheel"
      >
      </canvas>

      <!-- Top-located canvas to be able to blure map -->
      <canvas
        class="canvasTop"
        v-bind:class="{ blured: isBlured === 'true' }"
      ></canvas>

      <!-- a soft vignette along the edges of the visible map (over the land, under the
           server dots and markers); it stays in place while the map moves -->
      <div class="mapVignette" aria-hidden="true"></div>

      <!-- the ocean (background) with the inline world map on it -->
      <div class="bigMapArea" ref="bigMapArea">
        <MapWorld
          ref="mapWorld"
          class="map"
          :highlightIndex="connectedCountryIndex"
          :userCountryIndex="userCountryIndex"
          :serverCountries="serverCountryIndexes"
        />

        <!-- Hidden element to calculate styled text size-->
        <div
          ref="hiddenTestTextMeter"
          class="mapLocationName"
          style="opacity: 0; pointer-events: none; z-index: -1"
        ></div>

        <div class="mapLocationsContainer" ref="mapLocationsContainer">
          <!-- dashed line from the user's location to the selected server (not connected) -->
          <svg
            v-if="isMapLoaded && routeLine"
            class="routeLine"
            v-bind:class="{ routeLineMoving: routeLine.moving }"
            :width="routeLine.width"
            :height="routeLine.height"
            :viewBox="`0 0 ${routeLine.width} ${routeLine.height}`"
            :style="{ left: routeLine.left + 'px', top: routeLine.top + 'px' }"
            aria-hidden="true"
          >
            <path :d="routeLine.d" />
          </svg>

          <!-- connecting: the gold line and the comet from the user's location to the server -->
          <MapConnectFx
            v-if="isMapLoaded && connectFxView"
            :key="connectFxView.id"
            :fxId="connectFxView.id"
            :from="connectFxView.from"
            :to="connectFxView.to"
            :mode="connectFxView.mode"
            @landed="onConnectFxLanded"
            @done="onConnectFxDone"
          />

          <!-- Location point (servers without a marker) -->
          <div
            v-show="isMapLoaded && !isZooming"
            class="mapLocationPoint"
            v-for="l of plainLocations"
            @wheel="wheel"
            v-on:click="locationClicked(l.location)"
            @mouseenter="onLocationEnter(l)"
            @mouseleave="onLocationLeave(l)"
            v-bind:key="'point_' + locationKey(l.location)"
            v-bind:class="{
              mapLocationPointHovered: isHovered(l),
              mapLocationLocked: l.locked,
            }"
            :style="{ left: l.x + 'px', top: l.y + 'px' }"
          ></div>
          <!-- Location name -->
          <div
            v-show="isMapLoaded && !isZooming"
            class="mapLocationName"
            v-for="l of plainLocations"
            @wheel="wheel"
            v-on:click="locationClicked(l.location)"
            @mouseenter="onLocationEnter(l)"
            @mouseleave="onLocationLeave(l)"
            v-bind:key="'name_' + locationKey(l.location)"
            v-bind:class="{
              mapLocationNameHovered: isHovered(l),
              mapLocationLocked: l.locked,
            }"
            :style="{ left: l.left + 'px', top: l.top + 'px' }"
          >
            {{ l.width > 0 ? l.location.city : "" }}
          </div>

          <!-- the user's own location: the only label there (no popup, no server name) -->
          <MapMarker
            v-if="isMapLoaded && userMarker"
            kind="user"
            :x="userMarker.x"
            :y="userMarker.y"
            :caption="userMarker.caption"
            :tone="userMarker.tone"
            :pulse="userMarker.pulse"
            :title="userMarker.title"
            :countryCode="userMarker.code"
            :code="userMarker.code"
            :note="userMarker.note"
            :cardSide="userCardSide"
            :cardDy="userCardDy"
            :label="userMarker.label"
            @cardSize="onUserCardSize"
            @click="locationClicked(userMarker.location)"
            @wheel="wheel"
          />

          <!-- the selected / connecting / connected server -->
          <MapMarker
            v-if="isMapLoaded && serverMarker"
            :kind="serverMarker.kind"
            :x="serverMarker.x"
            :y="serverMarker.y"
            :caption="serverMarker.caption"
            :title="serverMarker.title"
            :countryCode="serverMarker.code"
            :code="serverMarker.code"
            :tier="serverMarker.tier"
            :wave="serverMarker.wave"
            :pulse="serverMarker.pulse"
            :label="serverMarker.label"
            @click="locationClicked(serverMarker.location)"
            @wheel="wheel"
          />

          <!-- label of the server under the mouse -->
          <MapHoverTip
            v-if="isMapLoaded && hoverTipInfo"
            ref="hoverTip"
            :title="hoverTipInfo.title"
            :countryCode="hoverTipInfo.code"
            :tier="hoverTipInfo.tier"
            :locked="hoverTipInfo.locked"
            :style="{ left: hoverTip.left + 'px', top: hoverTip.top + 'px' }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { VpnStateEnum } from "@/store/types";
import {
  CheckAndNotifyInaccessibleServer,
  CheckAndNotifyLockedServer,
} from "@/helpers/helpers_servers";
import {
  IsHostPremium,
  IsServerLocked,
  ServerTier,
} from "@/helpers/helpers_premium";

const sender = window.ipcSender;
import popupControl from "@/components/controls/control-map-popup.vue";
import GeolocationInfoControl from "@/components/controls/control-geolocation-info.vue";
import BlockSpeedGraph from "@/components/blocks/block-speed-graph.vue";
import MapWorld from "@/components/map/map-world.vue";
import MapMarker from "@/components/map/map-marker.vue";
import MapHoverTip from "@/components/map/map-hover-tip.vue";
import MapConnectFx from "@/components/map/map-connect-fx.vue";
import {
  MAP_WIDTH,
  MAP_HEIGHT,
  countryIndexOfLocation,
  countryBoxOfLocation,
  routeControlPoint,
  USER_PIN,
} from "@/components/map/map-geometry";

import config from "@/config";

import {
  notLinear,
  getPosFromCoordinates,
  getCoordinatesBy,
} from "@/helpers/helpers";

const defaultZoomScale = 0.41;
// Not connected: the user's location and the selected server are framed together.
// The map zooms out (never in beyond the default) until both fit, but not below this.
const minFrameScale = 0.15;
// room kept free between the framed markers (with their label cards) and the map edges
const frameMarginPx = 16;
// Connected: the map zooms in on the connected country until its box takes about
// this part of the visible map (width and height), between the default zoom and this.
const countryViewPart = 0.5;
const maxCountryScale = 0.8;
// how long the map takes to move (and zoom) to a new view
const moveDurationMs = 600;
// connected, after the connection effect: the move into the connected country
// (the country fill fades in meanwhile: components/map/map-world.vue)
const connectZoomMs = 900;
// a new number for every connection effect (see updateConnectFx())
let connectFxSeq = 0;
// gap between the bottom panel ("Connection details" card) and the map bottom edge (see .bottomPanel)
const bottomPanelGapPx = 20;
// minimal free map height above the card to keep centred locations above it
const minVisibleMapHeightPx = 80;
// plain server dot: a 6 px gold dot in a 2 px gap and a 1 px ring (see .mapLocationPoint);
// 5.5 px is the radius other names keep clear of (a name starts 10 px from the point)
const PointRadius = 5.5;
// the user's label card stays this far inside the visible map (its edges, and the top
// of the "Connection details" card); it flips to the left of the pin to stay in view
const userCardMarginPx = 8;
// and this far from the selected server's pin and card (it flips or slides to keep clear)
const userCardAvoidGapPx = 4;

// Free / Premium mark: the host's own when a host is known, else the location's
function tierOf(server, host) {
  if (host) return IsHostPremium(host) ? "Premium" : "Free";
  if (!server) return null;
  return ServerTier(server);
}
function tierText(tier) {
  if (tier === "Mixed") return "Free and Premium";
  return tier || "";
}

// a location's point on the map, in map units (MAP_WIDTH x MAP_HEIGHT), or null
function mapUnitsPoint(location) {
  if (location == null) return null;
  const lon = Number(location.longitude);
  const lat = Number(location.latitude);
  if (!Number.isFinite(lon) || !Number.isFinite(lat)) return null;
  return getCoordinatesBy(lon, lat, MAP_WIDTH, MAP_HEIGHT);
}

// Box { l, t, r, b } (map units) of the dashed line from the user's location 'u' to the
// server 's': the same curve as the 'routeLine' computed property draws.
function routeBox(u, s) {
  const box = {
    l: Math.min(u.x, s.x),
    t: Math.min(u.y, s.y),
    r: Math.max(u.x, s.x),
    b: Math.max(u.y, s.y),
  };
  const c = routeControlPoint(u, s);
  // the extreme of the quadratic curve on each axis (when it is between the ends)
  for (const axis of ["x", "y"]) {
    const den = u[axis] - 2 * c[axis] + s[axis];
    if (Math.abs(den) < 1e-9) continue;
    const t = (u[axis] - c[axis]) / den;
    if (t <= 0 || t >= 1) continue;
    const v =
      (1 - t) * (1 - t) * u[axis] + 2 * (1 - t) * t * c[axis] + t * t * s[axis];
    if (axis === "x") {
      box.l = Math.min(box.l, v);
      box.r = Math.max(box.r, v);
    } else {
      box.t = Math.min(box.t, v);
      box.b = Math.max(box.b, v);
    }
  }
  return box;
}

// Centre 'c' of a view 2 x 'half' wide, moved as little as possible so that the content
// from 'lo' to 'hi' is inside it with 'margin' to spare (centred when it cannot be).
function clampCentre(c, lo, hi, half, margin) {
  const min = hi + margin - half;
  const max = lo - margin + half;
  if (min > max) return (lo + hi) / 2;
  return Math.min(Math.max(c, min), max);
}

// Where the user's label card goes beside its pin: { side: "right" | "left", dy }, dy
// being how far (px) it slides down (+) or up (-) from its place centred on the pin head
// (the stem stays on it: at most USER_PIN.stemInset from its top and bottom edges).
// 'u': the user's point; 'card': its size ({ w, h }); 'avoid': rects ({ l, t, r, b }, the
// space of 'u') it keeps clear of: the server marker's pin and card; 'view': the rect it
// stays inside, 'margin' px within its edges, or null (framing: anywhere).
// On the right of the pin when it can be, else on the left, slid as little as possible;
// when nothing is clear, the place in the view that covers the least of 'avoid'; when
// nothing fits the view, on the side with the more room, slid into it as far as it goes.
function userCardPlacement(u, card, avoid, view, margin) {
  const gap = USER_PIN.cardGap;
  const pad = userCardAvoidGapPx;
  const reach = Math.max(0, Math.floor(card.h / 2 - USER_PIN.stemInset));
  const top0 = u.y + USER_PIN.headY - card.h / 2;
  // the slide that keeps it in the view (the top edge first)
  let dyView = 0;
  if (view) {
    if (top0 + card.h > view.b - margin)
      dyView = view.b - margin - (top0 + card.h);
    if (top0 + dyView < view.t + margin) dyView = view.t + margin - top0;
  }
  dyView = Math.round(Math.min(reach, Math.max(-reach, dyView)));
  const inView = (t) =>
    !view ||
    (t >= view.t + margin - 0.5 && t + card.h <= view.b - margin + 0.5);
  // the part of 'avoid' (each rect 'pad' px larger) the card covers
  const covered = (l, t) => {
    let area = 0;
    for (const a of avoid) {
      const w = Math.min(l + card.w, a.r + pad) - Math.max(l, a.l - pad);
      const h = Math.min(t + card.h, a.b + pad) - Math.max(t, a.t - pad);
      if (w > 0 && h > 0) area += w * h;
    }
    return area;
  };
  // the slides to try: into the view, just clear of each rect, the farthest ones
  const dys = new Set([dyView, reach, -reach]);
  for (const a of avoid) {
    dys.add(Math.ceil(a.b + pad - top0)); // under it
    dys.add(Math.floor(a.t - pad - card.h - top0)); // over it
  }
  let best = null;
  ["right", "left"].forEach((side, sideIndex) => {
    const l = side === "left" ? u.x - gap - card.w : u.x + gap;
    if (
      view &&
      (l < view.l + margin - 0.5 || l + card.w > view.r - margin + 0.5)
    )
      return;
    for (const dy of dys) {
      if (Math.abs(dy) > reach || !inView(top0 + dy)) continue;
      const c = {
        side,
        dy,
        cost: covered(l, top0 + dy),
        sideIndex,
        off: Math.abs(dy - dyView),
      };
      if (
        !best ||
        c.cost < best.cost ||
        (c.cost === best.cost &&
          (c.sideIndex < best.sideIndex ||
            (c.sideIndex === best.sideIndex && c.off < best.off)))
      )
        best = c;
    }
  });
  if (best) return { side: best.side, dy: best.dy };
  // no place in the view: the side with the more room
  const roomRight = view.r - margin - (u.x + gap + card.w);
  const roomLeft = u.x - gap - card.w - (view.l + margin);
  const side = roomRight >= 0 || roomRight >= roomLeft ? "right" : "left";
  return { side, dy: dyView };
}

// Room ({ l, t, r, b }, px around its point) the user's marker takes: the pin and its
// ripples, and the card where 'placement' (userCardPlacement()) puts it.
function userMarkerExtent(card, placement) {
  const gap = USER_PIN.cardGap;
  const l = placement.side === "left" ? -gap - card.w : gap;
  const t = USER_PIN.headY - card.h / 2 + placement.dy;
  return {
    l: Math.min(-USER_PIN.ringRx, l),
    t: Math.min(USER_PIN.top, t),
    r: Math.max(USER_PIN.ringRx, l + card.w),
    b: Math.max(USER_PIN.ringRy, t + card.h),
  };
}

export default {
  components: {
    popupControl,
    GeolocationInfoControl,
    BlockSpeedGraph,
    MapWorld,
    MapMarker,
    MapHoverTip,
    MapConnectFx,
  },
  props: {
    isBlured: String,
    onAccountSettings: Function,
    onSettings: Function,
    onMinimize: Function,
  },

  data: () => ({
    selectedPopupLocation: null,
    isMapLoaded: false,
    isPopupVisible: false,

    canvas: null,

    bigMapArea: null,
    map: null,
    combinedDiv: null,
    popup: null,
    mapLocationsContainer: null,
    hiddenTestTextMeter: null,

    scale: defaultZoomScale,

    // the running move of the map to a new view (see startView()), or null
    scrollTo: null,
    // true while a move changes the zoom: the plain server dots and names are hidden
    // (they are placed for one zoom) and placed again when the move ends
    isZooming: false,

    moving: false,
    startMoveX: 0,
    startMoveY: 0,
    lastMoveX: 0,
    lastMoveY: 0,

    mapPos: {
      mapLeftOffset: 0.0,
      mapTopOffset: 0.0,
    },

    // the server under the mouse: { location, x, y, left, top } (px in the locations layer)
    hoverTip: null,

    // where the user's label card is: on the "right" or "left" of the pin, and how far
    // (px) it slides down (+) or up (-) to stay in the visible map (see placeUserCard())
    userCardSide: "right",
    userCardDy: 0,

    // keeps the map centred when its container changes size
    resizeObserver: null,

    // The connection effect (components/map/map-connect-fx.vue), or null:
    // { id, mode: "travel" | "land" | "leave", landed, gateway, from, to (map units) }.
    // "land": connected, the comet is landing; the connected view waits for it.
    connectFx: null,
    // the system asks for less motion: no connection effect, no zoom animation on connect
    reducedMotion: false,
    reducedMotionQuery: null,

    locationsToDisplay: [
      /*{
        location,
        x,
        y,
        left: textPos.textX,
        top: textPos.textY,
        pointRadius,
        circleRadius,
        width: textWidth,
        height: textHeight,
        locked,          // a Free account cannot use this server
        marker,          // true: the area of a marker (pin, label card), not a plain dot
      } */
    ],
  }),

  computed: {
    servers: function () {
      return this.$store.getters["vpnState/activeServers"];
    },
    entryServer: function () {
      return this.$store.state.settings.serverEntry;
    },
    selectedServer: function () {
      if (this.$store.state.settings.isMultiHop)
        return this.$store.state.settings.serverExit;
      return this.$store.state.settings.serverEntry;
    },

    location: function () {
      let l = this.$store.state.location;

      // IPv6
      if (this.$store.getters["getIsIPv6View"]) {
        let lv6 = this.$store.state.locationIPv6;
        if (lv6 && lv6.isRealLocation) l = lv6;
        if (!lv6) l = null;
      }

      if (l == null || l.isRealLocation !== true) return null;
      return l;
    },

    isRequestingLocation: function () {
      let isInProcess = this.$store.state.isRequestingLocation;
      // IPv6
      if (this.$store.getters["getIsIPv6View"]) {
        isInProcess = this.$store.state.isRequestingLocationIPv6;
      }
      return isInProcess;
    },

    isFastestServer: function () {
      return this.$store.state.settings.isFastestServer;
    },
    isRandomExitServer: function () {
      return this.$store.state.settings.isRandomExitServer;
    },
    // Fastest / Random server mode: the server is picked on connect,
    // so the one in the settings is not shown as "selected" while disconnected
    isServerModeSelected: function () {
      const s = this.$store.state.settings;
      if (s.isMultiHop) return s.isRandomExitServer === true;
      return s.isFastestServer === true || s.isRandomServer === true;
    },

    isPaused: function () {
      return this.$store.getters["vpnState/isPaused"];
    },

    connectedLocation: function () {
      if (!this.isConnected) return null;
      return this.selectedServer;
    },

    // needed for watcher
    isLoggedIn: function () {
      return this.$store.getters["account/isLoggedIn"];
    },
    // Same rule as the server list and the store ("vpnState/isFreeAccount"): until the
    // account status is known nothing is locked, so a Premium account never sees its
    // servers locked while the app is starting (or when the status cannot be loaded).
    isPremiumAccount: function () {
      const free = this.$store.getters["vpnState/isFreeAccount"];
      if (free === true) return false;
      if (free === false) return true;
      return this.$store.getters["account/isPremiumAccount"] === true;
    },
    isConnecting: function () {
      return this.$store.getters["vpnState/isConnecting"];
    },
    isConnected: function () {
      if (this.isPaused) return false;
      return (
        this.$store.state.vpnState.connectionState === VpnStateEnum.CONNECTED
      );
    },
    isDisconnected: function () {
      if (this.isPaused) return true;
      return (
        this.$store.state.vpnState.connectionState === VpnStateEnum.DISCONNECTED
      );
    },
    isInProgress: function () {
      return !this.isConnected && !this.isDisconnected;
    },
    isMinimizedUI: function () {
      return this.$store.state.settings.minimizedUI;
    },

    // ---------------- countries ----------------
    // countries (indexes of the map paths) that have servers: drawn a little lighter
    serverCountryIndexes: function () {
      const set = new Set();
      for (const s of this.servers || []) {
        const i = countryIndexOfLocation(s);
        if (i >= 0) set.add(i);
      }
      return Array.from(set).sort((a, b) => a - b);
    },
    // the country of the connected server: filled
    // (after the connection effect: it fades in with the move into the country)
    connectedCountryIndex: function () {
      if (!this.isConnected || !this.connectedLocation || this.isFxHolding)
        return -1;
      return countryIndexOfLocation(this.connectedLocation);
    },
    // the user's own country while not protected: softly tinted (the same lookup)
    userCountryIndex: function () {
      if (this.isConnected || !this.userMarker) return -1;
      return countryIndexOfLocation(this.location);
    },

    // ---------------- connection effect ----------------
    // Fastest / Random server: the server is picked on connect; it is known once the
    // daemon starts the connection to it (it reports the endpoint) or is connected.
    isConnectTargetKnown: function () {
      if (!this.isServerModeSelected) return true;
      const vs = this.$store.state.vpnState;
      if (vs.isPingingServers === true) return false;
      return vs.remoteEndpoint != null || vs.connectionInfo != null;
    },
    // Connecting, the user's location and the server known: the ends of the effect
    // (map units), else null.
    connectFxTarget: function () {
      if (!this.isConnecting || this.isPaused || !this.isConnectTargetKnown)
        return null;
      const server = this.selectedServer;
      const from = mapUnitsPoint(this.location);
      const to = mapUnitsPoint(server);
      if (!from || !to) return null;
      return { gateway: server.gateway, from, to };
    },
    // what the effect depends on (see updateConnectFx())
    connectFxSignal: function () {
      const t = this.reducedMotion ? null : this.connectFxTarget;
      return [
        t ? [t.gateway, t.from.x, t.from.y].join("/") : "",
        this.isConnected ? "connected" : "",
        this.reducedMotion ? "reduced" : "",
      ].join("|");
    },
    // connected, the comet still on its way: the server is shown as "CONNECTING"
    isFxArriving: function () {
      const fx = this.connectFx;
      return fx != null && fx.mode === "land" && fx.landed !== true;
    },
    // connected, the effect still landing: the connected view (zoom into the country,
    // country fill, speed graph) waits for it
    isFxHolding: function () {
      const fx = this.connectFx;
      return fx != null && fx.mode === "land";
    },
    // the effect in px of the locations layer (it follows the zoom)
    connectFxView: function () {
      const fx = this.connectFx;
      if (!fx) return null;
      const k = this.scale;
      return {
        id: fx.id,
        mode: fx.mode,
        from: { x: fx.from.x * k, y: fx.from.y * k },
        to: { x: fx.to.x * k, y: fx.to.y * k },
      };
    },

    // ---------------- markers ----------------
    // the host chosen in the server list (null: the app picks one)
    selectedHost: function () {
      return (
        this.$store.getters[
          this.$store.state.settings.isMultiHop
            ? "settings/selectedExitHost"
            : "settings/selectedEntryHost"
        ] || null
      );
    },
    // the host the tunnel is connected to, as the daemon reports it
    connectedHost: function () {
      const srv = this.connectedLocation;
      const ci = this.$store.state.vpnState.connectionInfo;
      if (!srv || !Array.isArray(srv.hosts) || !ci) return null;
      if (this.$store.state.settings.isMultiHop) {
        if (!ci.ExitHostname) return null;
        return srv.hosts.find((h) => h && h.hostname === ci.ExitHostname) || null;
      }
      if (!ci.ServerIP) return null;
      return srv.hosts.find((h) => h && h.host === ci.ServerIP) || null;
    },

    // The selected server's marker: outlined pin ("SELECTED", "CONNECTING", "PAUSED")
    // or, when connected, the gold pin with the "PROTECTED" card.
    serverMarker: function () {
      const server = this.selectedServer;
      if (!server) return null;

      let kind = "selected";
      let caption = "SELECTED";
      let state = "Selected server";
      let host = this.selectedHost;
      let wave = false;
      let pulse = false;
      // connected, the comet of the connection effect still on its way: "CONNECTING"
      const arriving = this.isFxArriving;
      if (this.isConnected && !arriving) {
        kind = "connected";
        caption = "PROTECTED"; // the left panel says "Connected"
        state = "Connected server";
        host = this.connectedHost || host;
        wave = true;
      } else if (this.isPaused) {
        caption = "PAUSED";
        state = "Paused connection";
      } else if (this.isInProgress || arriving) {
        // Fastest / Random: the server is not known while the servers are being pinged,
        // nor (connecting) until the daemon starts the connection to it
        if (
          this.isServerModeSelected &&
          this.$store.state.vpnState.isPingingServers === true
        )
          return null;
        if (this.isConnecting && !this.isConnectTargetKnown) return null;
        if (this.isConnecting || arriving) {
          caption = "CONNECTING";
          state = "Connecting to";
          pulse = true;
        } else if (this.$store.getters["vpnState/isDisconnecting"]) {
          caption = "DISCONNECTING";
          state = "Disconnecting from";
        }
      } else if (this.isServerModeSelected) return null;

      const p = this.getLocationXYCoordinates(server);
      if (!p) return null;

      const tier = tierOf(server, host);
      const title = server.city || server.country || "";
      const code = String(server.country_code || "").toUpperCase();
      return {
        location: server,
        kind,
        x: p.x,
        y: p.y,
        caption,
        title,
        code,
        tier,
        wave,
        pulse,
        label: [state + ": " + title, code, tierText(tier)]
          .filter((v) => !!v)
          .join(", "),
      };
    },

    // The user's own location (known only while not connected): red pin, "NOT PROTECTED"
    // card with the place and "Your real IP is visible" (connecting: "Connecting...")
    userMarker: function () {
      const l = this.location;
      if (!l) return null;
      const p = this.getLocationXYCoordinates(l);
      if (!p) return null;
      const unprotected = !this.isConnected;
      // connecting: a ripple breathes, the card says so
      const connecting = unprotected && this.isConnecting === true;
      const code = String(l.country_code || "").toUpperCase();
      const title = l.city || l.country || "Your location";
      let note = null;
      if (connecting) note = "Connecting\u2026";
      else if (unprotected) note = "Your real IP is visible";
      const place =
        "Your location: " + [title, code].filter((v) => !!v).join(", ");
      let state = "";
      if (connecting) state = ". Not protected yet, connecting";
      else if (unprotected) state = ". Not protected, your real IP is visible";
      return {
        location: l,
        kind: "user",
        x: p.x,
        y: p.y,
        caption: unprotected ? "NOT PROTECTED" : "YOUR LOCATION",
        tone: unprotected ? "danger" : "neutral",
        pulse: connecting,
        title,
        code,
        note,
        label: place + state,
      };
    },

    // things that change the room the markers take (names of other servers keep clear of it)
    markersLayoutKey: function () {
      const u = this.userMarker;
      const s = this.serverMarker;
      return [
        u ? [u.caption, u.title, u.code, u.note].join("/") : "",
        s
          ? [s.kind, s.caption, s.title, s.code, s.tier, s.location.gateway].join("/")
          : "",
      ].join("|");
    },

    // dashed connection line: the user's location -> the selected server (quadratic curve)
    // (connecting: the connection effect draws its gold line instead; when it fades out
    // after a cancel, the dashed line is back under it)
    routeLine: function () {
      const u = this.userMarker;
      const s = this.serverMarker;
      if (!u || !s || this.isConnected || s.kind !== "selected") return null;
      if (this.connectFx && this.connectFx.mode !== "leave") return null;

      const dx = s.x - u.x;
      const dy = s.y - u.y;
      const len = Math.sqrt(dx * dx + dy * dy);
      if (len < 24) return null; // the markers overlap: no room for a line

      // bend the line to one side (downwards) by 40 % of its length
      const c = routeControlPoint(u, s);
      const cx = c.x;
      const cy = c.y;

      const pad = 3;
      const left = Math.floor(Math.min(u.x, s.x, cx) - pad);
      const top = Math.floor(Math.min(u.y, s.y, cy) - pad);
      const right = Math.ceil(Math.max(u.x, s.x, cx) + pad);
      const bottom = Math.ceil(Math.max(u.y, s.y, cy) + pad);
      const f = (v) => Math.round(v * 10) / 10;
      return {
        left,
        top,
        width: right - left,
        height: bottom - top,
        d: `M${f(u.x - left)} ${f(u.y - top)}Q${f(cx - left)} ${f(cy - top)} ${f(s.x - left)} ${f(s.y - top)}`,
        moving: s.pulse === true,
      };
    },

    plainLocations: function () {
      return this.locationsToDisplay.filter((l) => l.marker !== true);
    },

    hoverTipInfo: function () {
      const t = this.hoverTip;
      if (!t || !t.location) return null;
      const l = t.location;
      return {
        title: l.city || l.country || "",
        code: String(l.country_code || "").toUpperCase(),
        tier: l.gateway ? tierOf(l, null) : null,
        locked: !!l.gateway && IsServerLocked(l, this.isPremiumAccount),
      };
    },
  },

  mounted() {
    this.canvas = this.$refs.canvas;

    this.popup = this.$refs.popup;
    this.bigMapArea = this.$refs.bigMapArea;
    this.map = this.$refs.mapWorld ? this.$refs.mapWorld.$el : null;
    this.combinedDiv = this.$refs.combined;
    this.mapLocationsContainer = this.$refs.mapLocationsContainer;
    this.hiddenTestTextMeter = this.$refs.hiddenTestTextMeter;

    // resize canvas on window resize
    // (this method should be called each time when main window resizing)
    this.windowResizing();

    // the map is inline: it is ready now
    this.mapLoaded();
    // mounted while connecting ("Show map", or the app opened while it connects):
    // the connection effect starts now (its watcher only sees later changes)
    this.updateConnectFx();

    // The map can mount before the window has grown to its full width ("Show map"):
    // keep the point in the middle of the map in the middle when the size changes.
    if (typeof ResizeObserver !== "undefined") {
      this.resizeObserver = new ResizeObserver(() => this.onMapResize());
      this.resizeObserver.observe(this.combinedDiv);
      // the bottom panel grows (a notice, the location rows once loaded): the user's
      // card keeps above it
      this.panelObserver = new ResizeObserver(() => this.placeUserCard(true));
      this.panelObserver.observe(this.$refs.bottomPanel);
    }

    // names are measured with the UI font: measure again once it is loaded
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => {
        if (this.combinedDiv && this.combinedDiv.isConnected) this.updateCities();
      });
    }
  },

  created: function () {
    // not reactive: the size ({ w, h }, px) of the user's label card, as laid out
    // (map-marker.vue reports it), or null before it is shown; the card ({ key, w, h })
    // the last framed view was made for, and that view ({ scale, left, top }) once the
    // map is there, or null (see onUserCardSize()); the selected server's card width
    // ({ key, w }: see userCardObstacles()); the observer of the bottom panel
    this.userCardSize = null;
    this.framedCard = null;
    this.framedView = null;
    this.serverCardW = null;
    this.panelObserver = null;
    window.addEventListener("mousemove", this.windowsmousemove);
    if (typeof window.matchMedia === "function") {
      const q = window.matchMedia("(prefers-reduced-motion: reduce)");
      this.reducedMotion = q.matches === true;
      if (typeof q.addEventListener === "function") {
        q.addEventListener("change", this.onReducedMotionChange);
        this.reducedMotionQuery = q;
      }
    }
  },
  unmounted: function () {
    window.removeEventListener("mousemove", this.windowsmousemove);
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
    if (this.panelObserver) {
      this.panelObserver.disconnect();
      this.panelObserver = null;
    }
    if (this.reducedMotionQuery) {
      this.reducedMotionQuery.removeEventListener(
        "change",
        this.onReducedMotionChange,
      );
      this.reducedMotionQuery = null;
    }
  },

  watch: {
    servers() {
      // NOTE! When watching an array, the callback will only trigger when the array is replaced. If you need to trigger on mutation, the 'deep' option must be specified.
      // https://v3-migration.vuejs.org/breaking-changes/watch.html
      this.updateCities();
    },

    connectedLocation(newVal, oldVal) {
      this.updateCities();
      // connected (or connected to another server): the server, zoomed in on its country.
      // Not when the server list is refreshed (the daemon does it every hour): the same
      // server then comes as a new object, and the user's zoom and drag must stay.
      // (Less motion: straight to that view, once the details card has its new size.
      // After a connection effect, the view waits for it: see showStateNow().)
      if (newVal && (!oldVal || oldVal.gateway !== newVal.gateway)) {
        if (this.reducedMotion)
          this.whenLaidOut(false, () => this.showStateNow(true));
        else this.showState(newVal);
      }
    },
    // connecting: start, land or end the connection effect
    connectFxSignal() {
      this.updateConnectFx();
    },
    // Fastest / Random: the server became known while connecting: frame it with the
    // user's location
    isConnectTargetKnown(known) {
      if (known && this.isConnecting) this.showState(this.selectedServer);
    },

    selectedServer(newVal, oldVal) {
      this.updateCities();
      if (!oldVal || (newVal && oldVal.gateway !== newVal.gateway))
        this.showState(this.selectedServer);
    },
    isFastestServer() {
      if (this.isFastestServer !== true && this.isRandomExitServer != true)
        this.showState(this.selectedServer);
    },
    isRandomExitServer() {
      if (this.isFastestServer !== true && this.isRandomExitServer != true)
        this.showState(this.selectedServer);
    },
    isMinimizedUI() {
      if (!this.isMinimizedUI) this.centerCurrentLocation();
    },
    location() {
      this.updateCities();
      setTimeout(() => {
        this.centerCurrentLocation();
      }, 300);
    },
    isLoggedIn() {
      this.centerCurrentLocation();
    },
    // a marker appeared, disappeared or changed its card: place the other names again
    markersLayoutKey() {
      this.updateCities();
    },
    isPremiumAccount() {
      // locked servers are dimmed
      this.updateCities();
    },
    isConnecting() {
      // AR-APP-40 - When app starts connecting, ... map should move to position of selected gateway
      // (with the user's location known: both stay framed, the dashed line runs to the server)
      if (this.isConnecting)
        setTimeout(() => {
          this.showState(this.selectedServer);
        }, 300);
    },
    isConnected() {
      // AR-APP-11 - When VPN status is changed to connected, map should be positioned to the coordinates of selected gateway
      // (less motion: without animation; after a connection effect it waits for it)
      if (this.isConnected) {
        setTimeout(() => {
          this.centerCurrentLocation(this.reducedMotion);
        }, 300);
      }
    },
    // Disconnected (or paused): leave the zoom of the connected country. The user's
    // location is usually being looked up again now: its arrival frames both markers.
    isDisconnected() {
      if (this.isDisconnected)
        setTimeout(() => {
          this.centerCurrentLocation();
        }, 300);
    },
    // the location lookup ended without a location: the selected server alone
    isRequestingLocation() {
      if (!this.isRequestingLocation && !this.location && !this.isConnected)
        this.centerCurrentLocation();
    },
  },

  methods: {
    mapLoaded() {
      if (!this.map) return;
      const mapFullW = MAP_WIDTH;
      const mapFullH = MAP_HEIGHT;
      // scale map (and fit locations container to map scalled size)
      this.applyScale(this.scale);

      // To be able to scroll any direction with no border limits,
      // we are creating big scrolling area and map will be placed on center of it
      // So, there will be free space around the map.
      this.mapPos.mapLeftOffset = mapFullW;
      this.mapPos.mapTopOffset = mapFullH;
      this.bigMapArea.style.width = `${mapFullW * 3}px`;
      this.bigMapArea.style.height = `${mapFullH * 3}px`;
      this.mapLocationsContainer.style.left = `${this.mapPos.mapLeftOffset}px`;
      this.mapLocationsContainer.style.top = `${this.mapPos.mapTopOffset}px`;
      this.map.style.left = `${this.mapPos.mapLeftOffset}px`;
      this.map.style.top = `${this.mapPos.mapTopOffset}px`;

      this.updateCities();
      this.centerCurrentLocation(true);

      this.isMapLoaded = true;
    },
    onMapResize() {
      const c = this.canvas;
      if (c == null || !this.combinedDiv) return;
      const oldW = c.width;
      const oldH = c.height;
      this.windowResizing();
      if (c.width === oldW && c.height === oldH) return;
      this.stopScroll();
      this.isPopupVisible = false;
      this.hoverTip = null;
      // the map had no room before (mounted while the window was still compact):
      // centre it now, as on load
      if (oldW < minVisibleMapHeightPx || oldH < minVisibleMapHeightPx) {
        this.centerCurrentLocation(true);
        return;
      }
      this.combinedDiv.scrollLeft -= (c.width - oldW) / 2;
      this.combinedDiv.scrollTop -= (c.height - oldH) / 2;
    },
    windowResizing() {
      // This method should be called each time when main window resizing
      let c = this.canvas;

      if (c == null) return;

      if (c.width === c.clientWidth && c.height === c.clientHeight) return;

      // update canvas size
      c.width = c.clientWidth;
      c.height = c.clientHeight;
    },
    onAccountRenew() {
      sender.shellOpenExternal(config.URLAccount);
    },
    // ================= CONNECTION ====================
    async disconnect() {
      this.isPopupVisible = false;
      try {
        sender.Disconnect();
      } catch (e) {
        console.error(e);
        sender.showMessageBoxSync({
          type: "error",
          buttons: ["OK"],
          message: `Failed to disconnect: ` + e,
        });
      }
    },

    async connect(location) {
      this.isPopupVisible = false;
      // a Free account cannot use a location whose hosts are all Premium:
      // say so ("<City> is Premium", Upgrade / Not now) instead of connecting
      if (
        location?.gateway &&
        IsServerLocked(location, this.isPremiumAccount)
      ) {
        await CheckAndNotifyLockedServer(location);
        return;
      }
      try {
        // check if we can change server (for multihop)
        var settings = this.$store.state.settings;
        if (settings.isMultiHop === true) {
          this.$store.dispatch("settings/isRandomExitServer", false);
          this.$store.dispatch("settings/serverExit", location);
          this.$store.dispatch("settings/serverExitHostId", null);
          await sender.Connect();
        } else {
          this.$store.dispatch("settings/isFastestServer", false);
          this.$store.dispatch("settings/isRandomServer", false);
          this.$store.dispatch("settings/serverEntry", location);
          this.$store.dispatch("settings/serverEntryHostId", null);
          await sender.Connect();
        }
      } catch (e) {
        console.error(e);
        sender.showMessageBoxSync({
          type: "error",
          buttons: ["OK"],
          message: `Failed to connect: ` + e,
        });
      }
    },
    async resume() {
      this.isPopupVisible = false;
      try {
        await sender.ResumeConnection();
      } catch (e) {
        console.error(e);
        sender.showMessageBoxSync({
          type: "error",
          buttons: ["OK"],
          message: `Failed to resume: ` + e,
        });
      }
    },
    // ================= CONNECTION EFFECT ====================
    // Starts, lands or ends the connection effect (components/map/map-connect-fx.vue):
    // - connecting, the user's location and the server known: the gold line draws itself
    //   from the user to the server and a comet runs along it;
    // - connected to that server: the comet lands at the pin, a ripple bursts, the line
    //   fades; then the map moves into the connected country (endConnectFx());
    // - anything else (cancelled, failed, disconnected): it fades out, and the map takes
    //   the disconnected view as before.
    updateConnectFx() {
      const fx = this.connectFx;
      const t = this.reducedMotion ? null : this.connectFxTarget;
      if (t) {
        if (
          !fx ||
          fx.mode !== "travel" ||
          fx.gateway !== t.gateway ||
          fx.from.x !== t.from.x ||
          fx.from.y !== t.from.y
        ) {
          this.connectFx = {
            id: ++connectFxSeq,
            mode: "travel",
            landed: false,
            gateway: t.gateway,
            from: t.from,
            to: t.to,
          };
        }
        return;
      }
      if (!fx) return;
      // less motion asked for meanwhile: no effect (the view it held is shown at once)
      if (this.reducedMotion) {
        this.endConnectFx(false);
        return;
      }
      if (fx.mode === "travel") {
        const server = this.connectedLocation;
        fx.mode = server && server.gateway === fx.gateway ? "land" : "leave";
      } else if (fx.mode === "land" && !this.isConnected) {
        fx.mode = "leave";
      }
    },
    // The effect ended (or was dropped). When it held the connected view back: the map
    // moves into the connected country now (at once with less motion or a hidden window).
    endConnectFx(animate) {
      const fx = this.connectFx;
      if (!fx) return;
      this.connectFx = null;
      if (fx.mode !== "land" || !this.isConnected) return;
      const jump = animate !== true || this.reducedMotion || document.hidden;
      // after the DOM update: the details card gets its speed graph now
      this.whenLaidOut(false, () => this.showStateNow(jump, connectZoomMs));
      // and once more a little later, as after a connect without the effect (isConnected
      // watcher): the card can still change its height (the VPN location arrives)
      setTimeout(() => this.centerCurrentLocation(this.reducedMotion), 300);
    },
    // the comet is at the server: it is shown connected (gold pin, "CONNECTED" card)
    onConnectFxLanded(id) {
      if (this.connectFx && this.connectFx.id === id)
        this.connectFx.landed = true;
    },
    onConnectFxDone(id) {
      if (this.connectFx && this.connectFx.id === id) this.endConnectFx(true);
    },
    onReducedMotionChange(e) {
      this.reducedMotion = e.matches === true;
    },
    // ================= MOUSE ====================
    mouseDown(e) {
      if (this.$store.getters["account/isLoggedIn"] !== true) return;
      this.stopScroll();
      this.isPopupVisible = false;
      this.hoverTip = null;
      this.startMoveX = this.lastMoveX = e.offsetX;
      this.startMoveY = this.lastMoveY = e.offsetY;
      this.moving = true;
    },
    mouseUp() {
      this.moving = false;
    },
    windowsmousemove(e) {
      if (this.moving) {
        // the mouse event out of canvas bounds
        if (e.toElement !== this.canvas) {
          this.mouseMove(e);
        }
      }
    },
    mouseMove(e) {
      if (e.buttons !== 1) {
        // MouseEvent.buttons
        // 0 : No button or un-initialized
        // 1 : Primary button (usually the left button)
        // 2 : Secondary button (usually the right button)
        this.mouseUp();
        return;
      }

      if (this.moving) {
        if (this.map != null) {
          const mapFullW = MAP_WIDTH;
          const mapFullH = MAP_HEIGHT;
          let offsetX = e.offsetX;
          let offsetY = e.offsetY;
          if (e.toElement !== this.canvas) {
            var rect = this.combinedDiv.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
          }

          // MOVING
          // SCROLL HORISONTALLY
          const scrollLeftOffset = this.lastMoveX - offsetX;
          const newScrollLeft = this.combinedDiv.scrollLeft + scrollLeftOffset;

          if (
            // map moving right
            // (minimum visible right map part = 30% of natural width)
            (scrollLeftOffset > 0 &&
              ((newScrollLeft - this.mapPos.mapLeftOffset) / this.scale <
                mapFullW * 0.7 ||
                mapFullW * this.scale -
                  (newScrollLeft - this.mapPos.mapLeftOffset) >
                  this.canvas.width)) ||
            // map moving left
            // (minimum visible left map part = 30% of natural width)
            (scrollLeftOffset < 0 &&
              (newScrollLeft -
                this.mapPos.mapLeftOffset +
                this.canvas.width -
                mapFullW * 0.3 * this.scale >
                0 ||
                newScrollLeft > this.mapPos.mapLeftOffset))
          ) {
            this.combinedDiv.scrollLeft = newScrollLeft;
          }

          // SCROLL VERTICALLY
          const scrollTopOffset = this.lastMoveY - offsetY;
          const newScrollTop = this.combinedDiv.scrollTop + scrollTopOffset;
          if (
            // map moving bottom
            // (minimum visible bottom map part = 2249px+30% of natural height)
            // (2249 pixels at the button of the map is just ocean. No necessary to show it)
            (scrollTopOffset > 0 &&
              ((newScrollTop - this.mapPos.mapTopOffset) / this.scale <
                (mapFullH - 2249) * 0.7 ||
                (mapFullH - 2249) * this.scale -
                  (newScrollTop - this.mapPos.mapTopOffset) >
                  this.canvas.height)) ||
            // map moving top
            // (minimum visible top map part = 30% of natural height)
            (scrollTopOffset < 0 &&
              (newScrollTop -
                this.mapPos.mapTopOffset +
                this.canvas.height -
                mapFullH * 0.3 * this.scale >
                0 ||
                newScrollTop > this.mapPos.mapTopOffset))
          ) {
            this.combinedDiv.scrollTop = newScrollTop;
          }

          this.lastMoveX = offsetX;
          this.lastMoveY = offsetY;
        }
      }
    },

    async locationClicked(location) {
      if (this.$store.getters["account/isLoggedIn"] !== true) return;

      // A Free account cannot use this location (all its hosts are Premium): do not
      // select or connect it; say so instead ("<City> is Premium" with Upgrade, which
      // opens the account page, and Not now). The map does not move, so the hover
      // label under the mouse keeps showing the lock.
      if (
        location?.gateway &&
        IsServerLocked(location, this.isPremiumAccount)
      ) {
        await CheckAndNotifyLockedServer(location);
        return;
      }

      this.hoverTip = null;

      // does selected VPN server location?
      if (location?.gateway) {
        let settings = this.$store.state.settings;
        let conectionState = this.$store.state.vpnState.connectionState;

        const isMultihop = settings.isMultiHop;
        let isSvrOk = null;
        if (conectionState === VpnStateEnum.DISCONNECTED) {
          // activate selected server
          if (isMultihop) {
            isSvrOk = await CheckAndNotifyInaccessibleServer(true, location);
            if (isSvrOk === true) {
              this.$store.dispatch("settings/serverExit", location);
              this.$store.dispatch("settings/isRandomExitServer", false);
            }
          } else {
            this.$store.dispatch("settings/serverEntry", location);
            this.$store.dispatch("settings/isRandomServer", false);
            this.$store.dispatch("settings/isFastestServer", false);
          }
        }

        if (settings.connectSelectedMapLocation === true) {
          // connect
          if (isSvrOk == null && isMultihop)
            isSvrOk = await CheckAndNotifyInaccessibleServer(true, location);

          if (isSvrOk !== false) {
            this.connect(location);
          }
        }
      }

      if (this.location == location) {
        // center current location and show popup
        this.centerServer(location, false, true);
      } else if (
        location?.gateway &&
        this.selectedServer &&
        location.gateway === this.selectedServer.gateway
      ) {
        // the selected (or connected) server: frame it as the state wants
        // (not connected: together with the user's location)
        this.showState(location);
      } else {
        // center clicked server location
        this.centerServer(location);
      }
    },

    // ================= HOVER LABEL ====================
    locationKey(location) {
      if (!location) return "";
      return location.gateway || location.city || "";
    },
    isHovered(l) {
      return this.hoverTip != null && this.hoverTip.location === l.location;
    },
    onLocationEnter(l) {
      if (this.moving || !l || !l.location) return;
      this.hoverTip = {
        location: l.location,
        x: l.x,
        y: l.y,
        // under the dot, clear of the mouse pointer
        left: l.x - 7.5,
        top: l.y + 25,
      };
      this.$nextTick(() => this.fitHoverTip());
    },
    onLocationLeave(l) {
      if (this.hoverTip && l && this.hoverTip.location === l.location)
        this.hoverTip = null;
    },
    // ================= THE USER'S CARD ====================
    // The map scrolled (dragged, moved to a view, zoomed): the user's card keeps in view.
    onMapScroll() {
      this.placeUserCard(true);
    },
    // the user's card was laid out with a new size: the room it takes changed
    onUserCardSize(size) {
      if (!size || !(size.w > 0) || !(size.h > 0)) return;
      const old = this.userCardSize;
      if (old && old.w === size.w && old.h === size.h) return;
      this.userCardSize = { w: size.w, h: size.h };
      // (places the card too)
      this.updateCities();
      // The view was framed for this card with another size of it (an estimate before
      // it was laid out, or before the UI font was loaded) and has not moved since:
      // frame it again with the real size, at once (the first time, this comes before
      // the card is painted). Not when the card changed (a new place, "Connecting..."):
      // the watchers of those frame the view again themselves.
      const f = this.framedCard;
      if (
        f &&
        (f.w !== size.w || f.h !== size.h) &&
        this.userMarker &&
        f.key === this.userCardKey(this.userMarker) &&
        !this.isConnected &&
        !this.isInProgress &&
        !this.connectFx &&
        !this.scrollTo &&
        !this.moving &&
        this.isAtFramedView()
      )
        this.showStateNow(true);
    },
    // what the user's card shows (its size follows it)
    userCardKey(m) {
      return [m.caption, m.title, m.code, m.note].join("/");
    },
    // size ({ w, h }, px) of the user's card: as laid out, or estimated before it is shown
    userCardBox(m) {
      if (this.userCardSize) return this.userCardSize;
      return { w: this.estimateCardWidth(m), h: m.note ? 74 : 54 };
    },
    // the map is still at the last framed view (not moved, dragged or zoomed since)
    isAtFramedView() {
      const f = this.framedView;
      if (!f || !this.combinedDiv) return false;
      return (
        f.scale === this.scale &&
        Math.abs(f.left - this.combinedDiv.scrollLeft) <= 1 &&
        Math.abs(f.top - this.combinedDiv.scrollTop) <= 1
      );
    },
    // The rects ({ l, t, r, b }, px in the locations layer) the user's card keeps clear
    // of: the server marker's pin and card (the areas other names keep clear of:
    // markerAreas()), its point at (sx, sy) (default: where it is now).
    userCardObstacles(sx, sy) {
      const s = this.serverMarker;
      if (!s || !this.hiddenTestTextMeter) return [];
      // its card width is measured once for what it shows (not on every scroll)
      const key = [s.kind, s.caption, s.title, s.code, s.tier].join("/");
      if (!this.serverCardW || this.serverCardW.key !== key)
        this.serverCardW = { key, w: this.estimateCardWidth(s) };
      const at = { ...s, x: sx == null ? s.x : sx, y: sy == null ? s.y : sy };
      const rects = [];
      for (const a of this.markerAreas(at, this.serverCardW.w)) {
        const r = a.pointRadius;
        rects.push({ l: a.x - r, t: a.y - r, r: a.x + r, b: a.y + r });
        rects.push({
          l: a.left,
          t: a.top,
          r: a.left + a.width,
          b: a.top + a.height,
        });
      }
      return rects;
    },
    // Where the user's card goes (userCardPlacement()): on the right of the pin, or on
    // its left when it would go past the right edge of the visible map or cover the
    // selected server's pin or card; centred on the pin head, slid up or down (with the
    // stem still on it) to stay above the "Connection details" card, below the top edge
    // and clear of the server marker. 'relayout': the server names are placed again when
    // the card changes its side or slides onto one of them (they keep clear of it).
    placeUserCard(relayout) {
      const u = this.userMarker;
      if (!u || !this.combinedDiv || !this.canvas) return;
      const card = this.userCardBox(u);
      const left = this.combinedDiv.scrollLeft - this.mapPos.mapLeftOffset;
      const top = this.combinedDiv.scrollTop - this.mapPos.mapTopOffset;
      let height = this.getVisibleMapHeight();
      // very small map: the card can cover the bottom panel (see getVisibleMapCenterY)
      if (height < minVisibleMapHeightPx) height = this.canvas.height;
      const view = {
        l: left,
        t: top,
        r: left + this.combinedDiv.clientWidth,
        b: top + height,
      };
      const p = userCardPlacement(
        u,
        card,
        this.userCardObstacles(),
        view,
        userCardMarginPx,
      );

      if (p.side === this.userCardSide && p.dy === this.userCardDy) return;
      const flipped = p.side !== this.userCardSide;
      this.userCardSide = p.side;
      this.userCardDy = p.dy;
      if (relayout && (flipped || this.isUserCardOverNames(u, card)))
        this.updateCities();
    },
    // the user's card (where it is now) covers a server name or dot placed before
    isUserCardOverNames(u, card) {
      const gap = USER_PIN.cardGap;
      const l = this.userCardSide === "left" ? u.x - gap - card.w : u.x + gap;
      const t = u.y + USER_PIN.headY - card.h / 2 + this.userCardDy;
      const hit = (x, y, w, h) =>
        x < l + card.w && l < x + w && y < t + card.h && t < y + h;
      return this.locationsToDisplay.some(
        (c) =>
          c.marker !== true &&
          ((c.width > 0 && hit(c.left, c.top, c.width, c.height)) ||
            hit(
              c.x - c.pointRadius,
              c.y - c.pointRadius,
              2 * c.pointRadius,
              2 * c.pointRadius,
            )),
      );
    },

    // keep the hover label inside the visible map (above the "Connection details" card)
    fitHoverTip() {
      const tip = this.hoverTip;
      const ref = this.$refs.hoverTip;
      const el = ref ? ref.$el : null;
      if (!tip || !el || !this.combinedDiv) return;

      const margin = 8;
      const w = el.offsetWidth;
      const h = el.offsetHeight;
      const viewLeft = this.combinedDiv.scrollLeft - this.mapPos.mapLeftOffset;
      const viewTop = this.combinedDiv.scrollTop - this.mapPos.mapTopOffset;
      const viewRight = viewLeft + this.combinedDiv.clientWidth;
      const viewBottom = viewTop + this.getVisibleMapHeight();

      let left = tip.x - 7.5;
      if (left + w > viewRight - margin) left = viewRight - margin - w;
      if (left < viewLeft + margin) left = viewLeft + margin;
      let top = tip.y + 25;
      // no room under the dot: above it
      if (top + h > viewBottom - margin) top = tip.y - 17 - h;

      if (left !== tip.left || top !== tip.top)
        this.hoverTip = { ...tip, left, top };
    },

    // ================= SCROLLING ====================
    // Moves the map to the view of the current state (load, "Center map", location arrival,
    // connect / disconnect, ...):
    // - connected: the server in the middle, zoomed in on its country;
    // - not connected, a server selected and the user's location known: both, with their cards;
    // - else (IVPN's behaviour): the user's location (with its popup) or the selected server.
    centerCurrentLocation(noAnimation) {
      this.whenLaidOut(noAnimation, () => {
        if (this.showStateNow(noAnimation)) return;
        if (!this.isConnected && this.location != null) {
          this.centerServerNow(
            this.location,
            noAnimation,
            true,
            this.disconnectedScale(),
          );
        } else if (
          !this.isRequestingLocation ||
          (this.combinedDiv.scrollLeft == 0 && this.combinedDiv.scrollTop == 0)
        ) {
          this.centerServerNow(
            this.selectedServer,
            noAnimation,
            false,
            this.isConnected ? null : this.disconnectedScale(),
          );
        }
      });
    },
    // As centerCurrentLocation(), for the events that centred 'server' before
    // (selection change, connecting, ...): with nothing to frame, 'server' is centred.
    showState(server, noAnimation) {
      this.whenLaidOut(noAnimation, () => {
        if (this.showStateNow(noAnimation)) return;
        // connecting to a Fastest / Random server that is not known yet (no marker):
        // the user's location stays in the middle
        if (this.isConnecting && !this.serverMarker && this.location)
          server = this.location;
        this.centerServerNow(
          server,
          noAnimation,
          false,
          this.isConnected ? null : this.disconnectedScale(),
        );
      });
    },
    // Connected: the connected server, zoomed in on its country. Not connected: the user's
    // location and the selected server together. Returns false when neither applies.
    // 'durationMs': how long the move takes (default: moveDurationMs).
    showStateNow(noAnimation, durationMs) {
      if (this.isConnected) {
        // the connection effect is landing: the map moves in when it ends (endConnectFx())
        if (this.isFxHolding) return true;
        const server = this.selectedServer;
        const p = mapUnitsPoint(server);
        if (!p) return false;
        this.startView(
          { scale: this.getCountryScale(server), x: p.x, y: p.y, durationMs },
          noAnimation,
        );
        return true;
      }
      const target = this.getFrameTarget();
      if (!target) return false;
      this.startView(target, noAnimation);
      return true;
    },
    // Watchers run before the DOM update, and the "Connection details" card can change
    // its height in that same update (e.g. the speed section appears on connect):
    // measure the card once the DOM is updated.
    whenLaidOut(noAnimation, func) {
      if (noAnimation) {
        if (this.isViewReady()) func();
        return;
      }
      this.$nextTick(() => {
        if (this.isViewReady()) func();
      });
    },
    // the map can be hidden (unmounted) before a deferred call runs
    isViewReady() {
      if (!this.combinedDiv || !this.combinedDiv.isConnected) return false;
      this.windowResizing(); // update canvas size
      return true;
    },
    // not connected, one location to show: the current zoom, but not closer than the default
    // (e.g. after the zoom of the connected country)
    disconnectedScale() {
      return Math.min(this.scale, defaultZoomScale);
    },

    centerServer(server, noAnimation, isPopupRequired, scale) {
      if (server == null) return;
      this.whenLaidOut(noAnimation, () =>
        this.centerServerNow(server, noAnimation, isPopupRequired, scale),
      );
    },
    // 'scale': the zoom to show it at (default: the current one)
    centerServerNow(server, noAnimation, isPopupRequired, scale) {
      const p = mapUnitsPoint(server);
      if (!p) return;
      this.startView(
        {
          scale: scale || this.scale,
          x: p.x,
          y: p.y,
          isPopupRequired,
          location: server,
        },
        noAnimation,
      );
    },

    // Height (in canvas pixels) of the map part that the bottom panel
    // (the "Connection details" card and its 20 px bottom gap) does not cover.
    getVisibleMapHeight() {
      const height = this.canvas ? this.canvas.height : 0;
      const panel = this.$refs.bottomPanel;
      if (!panel || !height) return height;

      let covered = panel.offsetHeight + bottomPanelGapPx;
      // the speed section stays in the DOM while it fades out: it will be gone, do not count it
      const leaving = panel.querySelector(".speedSection.fade-leave-active");
      if (leaving) covered -= leaving.offsetHeight;
      return height - covered;
    },
    // Vertical position (in canvas pixels) where a centred location is placed:
    // the middle of the map area that is not covered by the bottom panel.
    getVisibleMapCenterY() {
      const height = this.canvas ? this.canvas.height : 0;
      if (!this.$refs.bottomPanel || !height) return height / 2;
      const visible = this.getVisibleMapHeight();
      // very small map: not enough room above the card, use the real centre
      if (visible < minVisibleMapHeightPx) return height / 2;
      return visible / 2;
    },
    // The size of the map part not covered by the bottom panel, and where a centred
    // point goes in it (canvas px).
    getVisibleMapArea() {
      const width = this.canvas ? this.canvas.width : 0;
      const centerY = this.getVisibleMapCenterY();
      let height = this.getVisibleMapHeight();
      // very small map: the centred point is in the real centre (see getVisibleMapCenterY)
      if (height < minVisibleMapHeightPx) height = centerY * 2;
      return { width, height, centerY };
    },

    // Not connected: the view that shows the user's location and the selected server
    // together, with their label cards and the dashed line between them, or null.
    // The middle of the two points is centred, and the view zooms out (from the default
    // zoom, not below 'minFrameScale') just enough for both. When they do not fit even
    // then, the selected server keeps its place in the view and the line leads off it.
    getFrameTarget() {
      const u = this.userMarker;
      const s = this.serverMarker;
      if (this.isConnected || !u || !s || s.kind === "connected") return null;
      const pu = mapUnitsPoint(u.location);
      const ps = mapUnitsPoint(s.location);
      if (!pu || !ps) return null;

      const area = this.getVisibleMapArea();
      if (area.width <= 0 || area.height <= 0) return null;
      const margin = frameMarginPx;
      const room = {
        w: area.width - 2 * margin,
        h: area.height - 2 * margin,
      };

      // What each marker takes around its point (px). The server's is the same at every
      // zoom; the user's card goes beside its pin clear of the server marker, which is
      // nearer at a smaller zoom (placeUserCard() puts it there too once framed).
      const uCard = this.userCardBox(u);
      this.framedCard = { key: this.userCardKey(u), w: uCard.w, h: uCard.h };
      const uExtAt = (k) =>
        userMarkerExtent(
          uCard,
          userCardPlacement(
            { x: 0, y: 0 },
            uCard,
            this.userCardObstacles(k * (ps.x - pu.x), k * (ps.y - pu.y)),
            null,
            0,
          ),
        );
      const sExt = this.markerExtent(s);
      // the dashed line (map units: it grows with the zoom)
      const line = routeBox(pu, ps);

      // content box (px, map pixels) at zoom 'k'
      const boxAt = (k, onlyServer) => {
        const b = {
          l: k * ps.x + sExt.l,
          t: k * ps.y + sExt.t,
          r: k * ps.x + sExt.r,
          b: k * ps.y + sExt.b,
        };
        if (onlyServer) return b;
        const uExt = uExtAt(k);
        b.l = Math.min(b.l, k * pu.x + uExt.l, k * line.l);
        b.t = Math.min(b.t, k * pu.y + uExt.t, k * line.t);
        b.r = Math.max(b.r, k * pu.x + uExt.r, k * line.r);
        b.b = Math.max(b.b, k * pu.y + uExt.b, k * line.b);
        return b;
      };
      const fits = (b) => b.r - b.l <= room.w && b.b - b.t <= room.h;

      // the closest zoom (not closer than the default) at which both fit
      let scale = minFrameScale;
      let fitsAll = false;
      const step = 0.005;
      for (let k = defaultZoomScale; k >= minFrameScale - 1e-9; k -= step) {
        if (fits(boxAt(k))) {
          scale = k;
          fitsAll = true;
          break;
        }
      }
      scale = Math.round(scale * 1000) / 1000;

      // centre the middle of the two points, moved just enough to keep the content in view
      const box = boxAt(scale, !fitsAll);
      let cx = (scale * (pu.x + ps.x)) / 2;
      let cy = (scale * (pu.y + ps.y)) / 2;
      cx = clampCentre(cx, box.l, box.r, area.width / 2, margin);
      cy = clampCentre(cy, box.t, box.b, area.height / 2, margin);
      // ('frame': once the map is there, it is the framed view: see onUserCardSize())
      return { scale, x: cx / scale, y: cy / scale, frame: true };
    },

    // Room a server marker takes around its point (px): pin, leader line and label card.
    // Geometry: components/map/map-marker.vue (the same as in markerAreas()).
    // (The user's marker: userMarkerExtent().)
    markerExtent(m) {
      const cardW = this.estimateCardWidth(m);
      // ripple rings (68 x 26 at most), card at +40 / -100
      return { l: -34, t: -100, r: 40 + cardW, b: 13 };
    },

    // Connected: zoom in on the country (the outline around the server's point) until it
    // takes about 'countryViewPart' of the visible map; a big country stays at the default zoom.
    getCountryScale(server) {
      const box = countryBoxOfLocation(server);
      if (!box) return defaultZoomScale;
      const area = this.getVisibleMapArea();
      const w = Math.max(box.maxX - box.minX, 1);
      const h = Math.max(box.maxY - box.minY, 1);
      let scale = Math.min(
        (countryViewPart * area.width) / w,
        (countryViewPart * area.height) / h,
      );
      if (!(scale > defaultZoomScale)) scale = defaultZoomScale;
      if (scale > maxCountryScale) scale = maxCountryScale;
      return Math.round(scale * 1000) / 1000;
    },

    // Moves the map to 'target': { scale, x, y, isPopupRequired, durationMs }. (x, y) is a
    // point in map units placed in the middle of the visible map; the zoom changes along
    // the way, in 'durationMs' (default: moveDurationMs).
    startView(target, noAnimation) {
      if (!this.combinedDiv || !this.canvas || !target) return;
      const centerY = this.getVisibleMapCenterY();
      const scale = target.scale > 0 ? target.scale : this.scale;
      const to = { scale, x: target.x, y: target.y };

      if (noAnimation) {
        this.stopScroll();
        this.isPopupVisible = false;
        if (scale !== this.scale) {
          this.applyScale(scale);
          this.updateCities();
        }
        this.scrollToView(to, centerY);
        this.framedView = target.frame === true ? this.currentView() : null;
        // Show popup for centered location
        if (target.location)
          this.showPopupForGeoLocation(target.location, target.isPopupRequired);
        return;
      }

      // the same move is running already (the same point, zoom and place above the card;
      // the card can grow while the map moves, e.g. the speed section on connect)
      const a = this.scrollTo;
      if (
        a &&
        a.to.scale === to.scale &&
        Math.abs(a.to.x - to.x) < 0.5 &&
        Math.abs(a.to.y - to.y) < 0.5 &&
        Math.abs(a.centerY - centerY) < 0.5
      ) {
        a.isPopupRequired = target.isPopupRequired;
        a.frame = target.frame === true;
        return;
      }
      this.framedView = null;

      // hide popup (if visible)
      this.isPopupVisible = false;
      this.hoverTip = null;

      // the point in the middle of the visible map now (map units)
      const from = {
        scale: this.scale,
        x:
          (this.combinedDiv.scrollLeft -
            this.mapPos.mapLeftOffset +
            this.canvas.width / 2) /
          this.scale,
        y:
          (this.combinedDiv.scrollTop - this.mapPos.mapTopOffset + centerY) /
          this.scale,
      };
      const zooming = to.scale !== from.scale;
      if (zooming) this.isZooming = true;
      this.scrollTo = {
        from,
        to,
        centerY,
        isPopupRequired: target.isPopupRequired,
        frame: target.frame === true,
        startTimeMs: performance.now(),
        // already there: done at the first step
        durationMs:
          !zooming &&
          Math.abs(to.x - from.x) * to.scale <= 1 &&
          Math.abs(to.y - from.y) * to.scale <= 1
            ? 0
            : target.durationMs > 0
              ? target.durationMs
              : moveDurationMs,
      };
      this.scrollingTick(this.scrollTo);
    },
    // the zoom and the scroll position of the map now
    currentView() {
      return {
        scale: this.scale,
        left: this.combinedDiv.scrollLeft,
        top: this.combinedDiv.scrollTop,
      };
    },
    // scroll so that 'view' (scale, x, y in map units) is in the middle of the visible map
    scrollToView(view, centerY) {
      this.combinedDiv.scrollLeft =
        this.mapPos.mapLeftOffset + view.x * view.scale - this.canvas.width / 2;
      this.combinedDiv.scrollTop =
        this.mapPos.mapTopOffset + view.y * view.scale - centerY;
    },
    stopScroll() {
      this.scrollTo = null;
      this.endZooming();
    },
    // a move that changed the zoom ended (or was stopped): place the server dots and names
    endZooming() {
      if (!this.isZooming) return;
      this.isZooming = false;
      this.updateCities();
    },
    scrollingTick(move) {
      // stopped, or replaced by another move
      if (move == null || this.scrollTo !== move) return;
      if (!this.combinedDiv || !this.combinedDiv.isConnected) {
        this.scrollTo = null;
        this.isZooming = false;
        return;
      }

      let koef =
        move.durationMs > 0
          ? (performance.now() - move.startTimeMs) / move.durationMs
          : 1;
      if (koef > 1) koef = 1;
      const k = notLinear(koef);

      const from = move.from;
      const to = move.to;
      // zoom evenly (in steps of the same ratio)
      const scale =
        koef >= 1 || from.scale === to.scale
          ? to.scale
          : from.scale * Math.pow(to.scale / from.scale, k);
      if (scale !== this.scale) this.applyScale(scale);
      this.scrollToView(
        {
          scale,
          x: from.x + (to.x - from.x) * k,
          y: from.y + (to.y - from.y) * k,
        },
        move.centerY,
      );

      if (koef >= 1) {
        this.scrollTo = null;
        if (move.frame) this.framedView = this.currentView();
        this.endZooming();
        // Show popup for centered location
        this.showPopup(
          this.combinedDiv.scrollLeft + this.canvas.width / 2,
          this.combinedDiv.scrollTop + move.centerY,
          move.isPopupRequired,
        );
        return;
      }

      const next = () => this.scrollingTick(move);
      if (typeof requestAnimationFrame === "function")
        requestAnimationFrame(next);
      else setTimeout(next, 1000 / 60);
    },

    // ================= POPUP ====================
    onPopupMouseClick() {
      // AR-APP-20 - Tap / click on the tooltip or any other part of the UI closes the tooltip.
      this.isPopupVisible = false;
    },
    showPopupForGeoLocation(location, isPopupRequired) {
      if (location == null) return;
      let point = this.getLocationVisibleXYCoordinates(location);
      this.showPopup(point.x, point.y, isPopupRequired);
    },
    showPopup(x, y, isPopupRequired) {
      // hide popup (if visible)
      this.isPopupVisible = false;
      if (x == null || y == null) return;

      const mLOffset = this.mapPos.mapLeftOffset;
      const mTOffset = this.mapPos.mapTopOffset;

      // looking for visible locations under map coordinates (x,y)
      x -= mLOffset;
      y -= mTOffset;
      let mapLocation = isUse(this.locationsToDisplay, x, y, 1, 0, 0, 0, 0);

      if (mapLocation == null) return;

      if (isPopupRequired !== true) return;
      // the user's own location already has its NOT PROTECTED card on the map: no second label
      const own = mapLocation.location;
      if (own != null && (own === this.$store.state.location || own === this.$store.state.locationIPv6))
        return;

      // save selected location info: server(or current user location info)
      this.selectedPopupLocation = mapLocation.location;
      // set popup coordinates
      this.popup.style.left =
        mapLocation.x - (this.combinedDiv.scrollLeft - mLOffset) + "px";
      this.popup.style.top =
        mapLocation.y - (this.combinedDiv.scrollTop - mTOffset) + "px";

      // show popup
      this.isPopupVisible = true;
    },
    // ================= ZOOMING ====================
    wheel(e) {
      this.isPopupVisible = false;
      this.hoverTip = null;
      if (e.deltaY > 0) this.zoomIn(e);
      else if (e.deltaY < 0) this.zoomOut(e);
    },

    zoomIn(e) {
      const step = 0.025;
      const minScale = 0.09;
      let newScale = this.scale - step;

      if (this.scale <= minScale) return;
      if (newScale < minScale) newScale = minScale;

      this.updateScale(newScale, e);
    },
    zoomOut(e) {
      const step = 0.025;
      const maxScale = 1.0;
      let newScale = this.scale + step;

      if (this.scale >= maxScale) return;
      if (newScale > maxScale) newScale = maxScale;

      this.updateScale(newScale, e);
    },

    // the map and the locations layer at zoom 'scale' (the scroll position is the caller's)
    applyScale(scale) {
      this.scale = scale;
      const w = `${MAP_WIDTH * scale}px`;
      const h = `${MAP_HEIGHT * scale}px`;
      this.map.style.width = w;
      this.map.style.height = h;
      this.mapLocationsContainer.style.width = w;
      this.mapLocationsContainer.style.height = h;
    },

    updateScale(newScale, zoomPoint) {
      const scaleDiff = newScale - this.scale;

      if (Math.abs(scaleDiff) < 0.001) return;
      // the user zooms: a running move of the map stops here
      this.stopScroll();
      const l = this.combinedDiv.scrollLeft;
      const t = this.combinedDiv.scrollTop;

      if (zoomPoint && zoomPoint.srcElement != this.canvas) {
        // if event come from non-canvas element (mouse is over location point\text)
        // - necessary to recalculate mouse position accourding canvas area
        // (relative to the map container: the window title bar sits above the map)
        const rect = this.combinedDiv.getBoundingClientRect();
        zoomPoint = {
          offsetX: zoomPoint.clientX - rect.left,
          offsetY: zoomPoint.clientY - rect.top,
        };
      }
      // save geo coordinates of center point (to be able to center same point after scalling)
      else if (zoomPoint == null) {
        zoomPoint = {
          offsetX: this.canvas.width / 2,
          offsetY: this.canvas.height / 2,
        };
      }

      const mapFullW = MAP_WIDTH;
      const mapFullH = MAP_HEIGHT;
      const mLOffset = this.mapPos.mapLeftOffset;
      const mTOffset = this.mapPos.mapTopOffset;

      const centerCoord = getPosFromCoordinates(
        l + zoomPoint.offsetX - mLOffset,
        t + zoomPoint.offsetY - mTOffset,
        this.scale * mapFullW,
        this.scale * mapFullH,
      );

      // change scale
      this.applyScale(newScale);

      // keep scroll positions
      let newPoint = getCoordinatesBy(
        centerCoord.longitude,
        centerCoord.latitude,
        this.scale * mapFullW,
        this.scale * mapFullH,
      );

      this.combinedDiv.scrollLeft = mLOffset + newPoint.x - zoomPoint.offsetX;
      this.combinedDiv.scrollTop = mTOffset + newPoint.y - zoomPoint.offsetY;

      // redraw locations (the markers follow the scale by themselves)
      this.updateCities();
    },

    // ================= DRAWING ====================
    getLocationXYCoordinates(location) {
      if (location == null) return null;
      const lon = Number(location.longitude);
      const lat = Number(location.latitude);
      if (!Number.isFinite(lon) || !Number.isFinite(lat)) return null;
      let point = getCoordinatesBy(
        lon,
        lat,
        this.scale * MAP_WIDTH,
        this.scale * MAP_HEIGHT,
      );
      return point;
    },

    getLocationVisibleXYCoordinates(location) {
      if (location == null) return null;
      let point = getCoordinatesBy(
        location.longitude,
        location.latitude,
        this.scale * MAP_WIDTH,
        this.scale * MAP_HEIGHT,
      );
      if (point == null) return null;
      point.x = point.x - this.combinedDiv.scrollLeft;
      point.y = point.y - this.combinedDiv.scrollTop;
      return point;
    },

    updateCities() {
      if (!this.hiddenTestTextMeter) return;
      let cities = [];
      const settings = this.$store.state.settings;

      // The markers have the highest priority: other names keep clear of their pins and cards.
      // (The user's location stays first: showPopup() looks the popup location up in this list.)
      if (this.userMarker != null) {
        // its card first takes its place in the view (a zoom moves the pin)
        this.placeUserCard(false);
        cities.push(...this.markerAreas(this.userMarker));
      }
      if (this.serverMarker != null)
        cities.push(...this.markerAreas(this.serverMarker));

      let city = null;
      // if MultiHop - just ensure that entry- server vill be visible
      if (settings.isMultiHop) {
        city = this.createCity(settings.serverEntry, cities, PointRadius);
        if (city != null) cities.push(city);
      }

      let skippedCities = [];
      // all the rest locations
      (this.servers || []).forEach((s) => {
        city = this.createCity(s, cities, PointRadius);
        if (city == null) {
          skippedCities.push(s);
          return;
        }
        cities.push(city);
      });

      // if there is no space to show location -> trying to show at least points (without name)
      const doNotShowName = true;
      skippedCities.forEach((s) => {
        city = this.createCity(s, cities, PointRadius, doNotShowName);
        if (city == null) return;
        cities.push(city);
      });
      this.locationsToDisplay = cities;

      // the hovered server may have moved (zoom) or gone
      if (
        this.hoverTip &&
        !cities.some((c) => !c.marker && c.location === this.hoverTip.location)
      )
        this.hoverTip = null;
    },

    // The areas a marker takes (its point, pin and label card), as entries of 'locationsToDisplay'.
    // Geometry: components/map/map-marker.vue. ('knownCardW': a server card's width, if known)
    markerAreas(m, knownCardW) {
      if (m.kind === "user") {
        // user location: the pin and its ripples (a 44 px square around the pin), and
        // the card where it is now (see placeUserCard())
        const card = this.userCardBox(m);
        const gap = USER_PIN.cardGap;
        return [
          {
            location: m.location,
            marker: true,
            x: m.x,
            y: m.y - 6,
            pointRadius: 22,
            left: this.userCardSide === "left" ? m.x - gap - card.w : m.x + gap,
            top: m.y + USER_PIN.headY - card.h / 2 + this.userCardDy,
            width: card.w,
            height: card.h,
          },
        ];
      }
      const cardW = knownCardW > 0 ? knownCardW : this.estimateCardWidth(m);
      const cardH = 51;
      return [
        // ripple rings + the card (up and right, at the end of the leader line)
        {
          location: m.location,
          marker: true,
          x: m.x,
          y: m.y,
          pointRadius: 16,
          left: m.x + 40,
          top: m.y - 100,
          width: cardW,
          height: cardH,
        },
        // the pin and the leader line
        {
          location: m.location,
          marker: true,
          x: m.x,
          y: m.y - 24,
          pointRadius: 18,
          left: m.x + 8,
          top: m.y - 60,
          width: 32,
          height: 32,
        },
      ];
    },
    // approximate width of a marker's label card (it is laid out by map-marker.vue)
    estimateCardWidth(m) {
      this.hiddenTestTextMeter.innerText = m.title || "";
      if (m.kind === "user") {
        // the user's card: 13 px semibold place, 10 px caption after a 12 px icon,
        // 11 px note (after a 10 px spinner while connecting); a little generous
        const placeW =
          21 + 7 + Math.min(168, this.hiddenTestTextMeter.clientWidth * 1.3);
        const captionW =
          (m.tone === "danger" ? 12 + 5 : 0) + (m.caption || "").length * 7.6;
        const noteW = m.note ? (m.pulse ? 15 : 0) + m.note.length * 5.4 : 0;
        return Math.ceil(
          2 + 20 + Math.max(placeW + (m.code ? 7 + 21 : 0), captionW, noteW),
        );
      }
      // the meter uses the 10.5 px name font; the card title is 12.5 px semibold
      const titleW = Math.min(168, this.hiddenTestTextMeter.clientWidth * 1.25);
      const placeW = 21 + 7 + titleW + (m.code ? 7 + 21 : 0);
      let tierW = 0;
      if (m.tier === "Premium") tierW = 10 + 66;
      else if (m.tier === "Free") tierW = 10 + 33;
      else if (m.tier === "Mixed") tierW = 10 + 52;
      const captionW = (m.caption || "").length * 7.6 + tierW;
      return Math.ceil(2 + 16 + Math.max(placeW, captionW));
    },

    createCity(location, locations, pointRadius, doNotShowName) {
      let point = this.getLocationXYCoordinates(location);
      if (point == null) return;
      let x = point.x;
      let y = point.y;

      let textWidth = 0;
      let textHeight = 0;
      if (doNotShowName == null || doNotShowName == false) {
        this.hiddenTestTextMeter.innerText = location.city;
        textWidth = this.hiddenTestTextMeter.clientWidth;
        textHeight = this.hiddenTestTextMeter.clientHeight;
      }

      let textPos = calcTextLocation(
        x,
        y,
        pointRadius,
        textWidth,
        textHeight,
        locations,
      );
      if (textPos == null) {
        //console.log(`Skipped '${location.city}' due to overlapping`);
        return;
      }
      return {
        location,
        x,
        y,
        left: textPos.textX,
        top: textPos.textY,
        pointRadius,
        width: textWidth,
        height: textHeight,
        locked:
          !!location.gateway && IsServerLocked(location, this.isPremiumAccount),
      };
    },
  },
};

// Position of a server name next to its point: right (as in the design), then
// left, above, below and the four diagonals; null when every place is taken.
function calcTextLocation(
  x,
  y,
  pointRadius,
  textWidth,
  textHeight,
  drawedCities,
) {
  const space = 4.5;
  const width = textWidth;
  const height = textHeight;

  // right
  let left = x + space + pointRadius;
  let top = y - height / 2;
  if (!isUse(drawedCities, x, y, pointRadius, left, top, width, height) == true)
    return { textX: left, textY: top };

  // left
  left = x - pointRadius - space - width;
  top = y - height / 2;
  if (!isUse(drawedCities, x, y, pointRadius, left, top, width, height) == true)
    return { textX: left, textY: top };

  // up (above the point)
  left = x - width / 2;
  top = y - (pointRadius + space + height);
  if (!isUse(drawedCities, x, y, pointRadius, left, top, width, height) == true)
    return { textX: left, textY: top };

  // buttom (under the point)
  left = x - width / 2;
  top = y + (pointRadius + space);
  if (!isUse(drawedCities, x, y, pointRadius, left, top, width, height) == true)
    return { textX: left, textY: top };

  // up + right
  left = x - pointRadius;
  top = y - (pointRadius + space + height);
  if (!isUse(drawedCities, x, y, pointRadius, left, top, width, height) == true)
    return { textX: left, textY: top };

  // up + left
  left = x - width + pointRadius;
  top = y - (pointRadius + space + height);
  if (!isUse(drawedCities, x, y, pointRadius, left, top, width, height) == true)
    return { textX: left, textY: top };

  // buttom + right
  left = x - pointRadius;
  top = y + (pointRadius + space);
  if (!isUse(drawedCities, x, y, pointRadius, left, top, width, height) == true)
    return { textX: left, textY: top };

  // buttom + left
  left = x - width + pointRadius;
  top = y + (pointRadius + space);
  if (!isUse(drawedCities, x, y, pointRadius, left, top, width, height) == true)
    return { textX: left, textY: top };

  return null;
}

function isUse(drawedCities, x, y, pointRadius, left, top, width, height) {
  let isRectInside = function (r1, r2) {
    return (
      r1.left + r1.width >= r2.left &&
      r1.left <= r2.left + r2.width &&
      r1.top <= r2.top + r2.height &&
      r1.top + r1.height >= r2.top
    );
  };

  let r1 = { left, top, width, height };
  for (let i = 0; i < drawedCities.length; i++) {
    let r2 = drawedCities[i];
    let p1 = {
      left: x - pointRadius,
      top: y - pointRadius,
      width: pointRadius * 2,
      height: pointRadius * 2,
    };
    let p2 = {
      left: r2.x - r2.pointRadius,
      top: r2.y - r2.pointRadius,
      width: r2.pointRadius * 2,
      height: r2.pointRadius * 2,
    };

    if (isRectInside(r1, r2)) return drawedCities[i];
    if (isRectInside(p1, r2)) return drawedCities[i];
    if (isRectInside(p1, p2)) return drawedCities[i];
    if (isRectInside(r1, p2)) return drawedCities[i];
  }
  return null;
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
//$shadow: 0px 4px 24px rgba(37, 51, 72, 0.25);

$shadow: 0px 3px 12px rgba(var(--shadow-color-rgb), var(--shadow-opacity));

@import "@/components/scss/constants";

#main {
  // Map colours (light theme; dark values below). The child map components
  // (components/map/*) read the --wm-* tokens from here.
  --wm-ocean: var(--map-background-color);
  // faint graticule on the ocean, and the layered vignette along the map edges
  --wm-grid: #d8d8dd;
  --wm-vignette: rgba(0, 0, 0, 0.018);
  --wm-coast-halo: rgba(255, 255, 255, 0.6);
  // two-tone land: countries with servers are lighter, with a brighter border
  --wm-land: #f4f4f5;
  --wm-border: #d4d4d8;
  --wm-land-servers: #ffffff;
  --wm-border-servers: #c4c4cc;
  // the user's own country while not protected: a soft tint of the danger colour
  --wm-user-fill: #fcecea;
  --wm-user-border: #efbcb7;
  --wm-on-fill: #d9f2e1;
  --wm-on-border: #16a34a;
  --wm-on-halo: rgba(22, 163, 74, 0.18);
  // server dots: gold (3:1 on the land), in a gap and a thin ring
  --wm-dot: #ba7800;
  --wm-dot-gap: #ffffff;
  --wm-dot-ring: #ddba7a;
  --wm-dot-hover: #a15f00;
  --wm-dot-hover-border: #ffffff;
  --wm-dot-hover-halo: rgba(196, 127, 0, 0.18);
  --wm-name: var(--text-muted);
  // name of a server a Free account cannot use: fainter, still 4.5:1 on land and ocean
  --wm-name-locked: #62626b;
  --wm-name-halo: #ffffff;
  --wm-route: #c47f00;

  position: relative;
  width: 100%;
  height: 100%;
  background: var(--wm-ocean);
}
@media (prefers-color-scheme: dark) {
  #main {
    --wm-grid: #1b1b21;
    --wm-vignette: rgba(0, 0, 0, 0.07);
    --wm-coast-halo: rgba(138, 138, 153, 0.06);
    --wm-land: #17181d;
    --wm-border: #2b2c33;
    --wm-land-servers: #1f2129;
    --wm-border-servers: #3a3c47;
    --wm-user-fill: #21171a;
    --wm-user-border: #57292e;
    --wm-on-fill: #14261b;
    --wm-on-border: #86efac;
    --wm-on-halo: rgba(134, 239, 172, 0.2);
    --wm-dot: #ffb000;
    --wm-dot-gap: #0b0b0d;
    --wm-dot-ring: #6b4e12;
    --wm-dot-hover: #ffc94d;
    --wm-dot-hover-border: #0b0b0d;
    --wm-dot-hover-halo: rgba(255, 176, 0, 0.18);
    --wm-name: #b4b4bc;
    --wm-name-locked: #8e8e96;
    --wm-name-halo: #0b0b0d;
    --wm-route: #ffb000;
  }
}

.mapcontainer {
  height: inherit;
  width: inherit;

  display: block;
  overflow-x: hidden;
  overflow-y: hidden;
}

.canvas {
  position: absolute;
  z-index: 2;
  height: inherit;
  width: inherit;
}

.canvasTop {
  @extend .canvas;
  z-index: 5;
  pointer-events: none;
}

.blured {
  filter: blur(7px);
  backdrop-filter: blur(5px);
}
// the ocean (the graticule on it is drawn with the map: components/map/map-world.vue)
.bigMapArea {
  position: relative;
  background-color: var(--wm-ocean);
}
// the vignette: five bands of the same faint shade, each narrower than the last
// (7 to 44 px from the edges), not a gradient wash; over the land, under the locations
.mapVignette {
  position: absolute;
  z-index: 2;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  box-shadow:
    inset 0 0 0 44px var(--wm-vignette),
    inset 0 0 0 32px var(--wm-vignette),
    inset 0 0 0 22px var(--wm-vignette),
    inset 0 0 0 14px var(--wm-vignette),
    inset 0 0 0 7px var(--wm-vignette);
}
.map {
  position: relative;
  z-index: 1;

  user-select: none;
}

// ============== bottom panel: "Connection details" card =================
// NOTE: if the 20 px gap changes, update 'bottomPanelGapPx' in the script (map centring uses it).
.bottomPanel {
  position: absolute;
  z-index: 4;
  left: 20px;
  right: 20px;
  bottom: 20px;

  display: flex;
  flex-direction: column;

  // let map dragging pass through the free space; the card and buttons take the pointer
  pointer-events: none;
}

.detailsCard {
  box-sizing: border-box;
  padding: 14px 16px;
  border-radius: 14px;
  background: var(--surface-color);
  border: 1px solid var(--surface-border);

  display: flex;
  flex-direction: column;

  pointer-events: auto;
}

.cardDivider {
  height: 1px;
  margin: 12px 0;
  background: var(--surface-divider);
}

// ============== account expiration =================
div.upgradeBase {
  min-height: 40px;
  box-sizing: border-box;
  border-radius: 12px;

  display: flex;
  align-items: center;

  font-size: 12px;
  line-height: 14px;
  letter-spacing: -0.4px;

  margin-bottom: 8px;
  padding-left: 12px;
  padding-right: 12px;
}
div.upgradeBase button {
  font-size: 12px;
  line-height: 14px;
  letter-spacing: -0.4px;
  pointer-events: auto;
  //cursor: pointer;
}
div.accountWillExpire {
  @extend .upgradeBase;
  background: var(--accent-tint);
  border: 1px solid var(--accent-ring);
  color: var(--text-color);
}
div.accountWillExpire button {
  color: var(--link-color);
  font-weight: 600;
}
div.trialWillExpire {
  @extend .upgradeBase;
  background: var(--accent-tint);
  border: 1px solid var(--accent-ring);
  color: var(--text-color);
}
div.trialWillExpire button {
  color: var(--link-color);
  font-weight: 600;
}

// ============== POPUP =================
// Popup container: placed (left/top) at the map point by showPopup()
.popup {
  position: absolute;
  z-index: 5;
  user-select: none;
}

// The actual popup: a card under the point (clear of the 36 px location marker)
.popup .popuptext {
  visibility: hidden;
  position: absolute;
  box-sizing: border-box;
  width: 248px;
  margin-left: -124px;
  margin-top: 30px;
  padding: 12px 14px;
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  background-color: var(--surface-color);
  box-shadow: $shadow;
  text-align: left;
}

// Popup arrow: a rotated square that carries the card border on its two outer sides
.popup .popuptext::after {
  content: "";
  position: absolute;
  top: -6px;
  left: 50%;
  width: 10px;
  height: 10px;
  // centred on the card (and on the map point): 11 px box with its border
  margin-left: -5.5px;
  background-color: var(--surface-color);
  border-left: 1px solid var(--surface-border);
  border-top: 1px solid var(--surface-border);
  transform: rotate(45deg);
}

// Toggle this class - hide and show the popup
.popup .show {
  visibility: visible;
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
// ========== LOCATIONS ===========
.mapLocationsContainer {
  position: absolute;
  z-index: 3;
  pointer-events: none;
}

.mapLocationElement {
  position: absolute;
  cursor: pointer;
  pointer-events: all;
  white-space: nowrap;
}

// server name next to its dot
.mapLocationName {
  @extend .mapLocationElement;
  font-size: 10.5px;
  font-weight: 500;
  line-height: 13px;
  display: inline-block;

  color: var(--wm-name);
  text-shadow:
    0 0 3px var(--wm-name-halo),
    0 0 2px var(--wm-name-halo);
}
// the hover label shows the name instead.
// (Transparent, not "visibility: hidden": a hidden name stops taking the mouse, which
// fires "mouseleave" at once, so the label would flash and vanish on every move.)
.mapLocationName.mapLocationNameHovered {
  opacity: 0;
}

// a 28 x 28 hit area centred on the map point; the dot is drawn inside it
.mapLocationPoint {
  @extend .mapLocationElement;
  width: 28px;
  height: 28px;
  margin-left: -14px;
  margin-top: -14px;
  display: block;
}
// a 6 px gold dot in a 2 px gap (the border) and a 1 px ring
.mapLocationPoint::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 50%;
  box-sizing: border-box;
  width: 10px;
  height: 10px;
  margin-left: -5px;
  margin-top: -5px;
  border: 2px solid var(--wm-dot-gap);
  border-radius: 50%;
  background: var(--wm-dot);
  box-shadow: 0 0 0 1px var(--wm-dot-ring);
}
.mapLocationPointHovered::before {
  width: 14px;
  height: 14px;
  margin-left: -7px;
  margin-top: -7px;
  background: var(--wm-dot-hover);
  border-color: var(--wm-dot-hover-border);
  box-shadow:
    0 0 0 1px var(--wm-dot-ring),
    0 0 0 4px var(--wm-dot-hover-halo);
}
// a server a Free account cannot use (a click opens the "<City> is Premium" prompt)
.mapLocationLocked {
  opacity: 0.55;
}
// its name is text: a fainter colour instead of the see-through look
// (at 55 % it was 3:1 on the dark map and 2.3:1 on the light one)
.mapLocationName.mapLocationLocked {
  color: var(--wm-name-locked);
}
.mapLocationName.mapLocationLocked:not(.mapLocationNameHovered) {
  opacity: 1;
}

// dashed line: the user's location -> the selected server
.routeLine {
  position: absolute;
  display: block;
  overflow: visible;
  pointer-events: none;
}
.routeLine path {
  fill: none;
  stroke: var(--wm-route);
  stroke-opacity: 0.75;
  stroke-width: 1.5;
  stroke-dasharray: 4 5;
  stroke-linecap: round;
}
// connecting: the dashes run towards the server
.routeLineMoving path {
  animation: routeFlow 0.9s linear infinite;
}
@keyframes routeFlow {
  to {
    stroke-dashoffset: -9;
  }
}
@media (prefers-reduced-motion: reduce) {
  .routeLineMoving path {
    animation: none;
  }
}
</style>
