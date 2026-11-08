<template>
  <div
    class="mapMarker"
    :class="['kind-' + kind, 'tone-' + cardTone, { pulsing: pulse }]"
    :style="{ left: x + 'px', top: y + 'px' }"
    role="group"
    :aria-label="label"
  >
    <!--
      A map marker with its label card, anchored at (x, y): the map point.
        kind "connected": gold teardrop pin on elliptical ripple rings + leader line + card
        kind "selected":  outlined pin (selected / connecting / paused server) + leader line + card
        kind "user":      the user's own location (danger colour) + card on its right
      Only the pin, the dot and the card take the pointer; their clicks and wheel events
      bubble to this root element, where the parent's @click / @wheel listeners sit.
      (No comment above the root element: the component must keep one root node.)
    -->
    <!-- connecting: the user's outer ring breathes (an HTML ring: see .udPulse) -->
    <span
      v-if="kind === 'user' && pulse"
      class="udPulse"
      aria-hidden="true"
    ></span>
    <svg
      v-if="kind === 'user'"
      class="userDot hit"
      width="36"
      height="36"
      viewBox="0 0 36 36"
      aria-hidden="true"
    >
      <circle class="udOuter" cx="18" cy="18" r="16.5" />
      <circle class="udHalo" cx="18" cy="18" r="10.5" />
      <circle class="udCore" cx="18" cy="18" r="5" />
    </svg>

    <template v-else>
      <svg
        class="rings"
        :width="g.ringsW"
        :height="g.ringsH"
        :viewBox="`0 0 ${g.ringsW} ${g.ringsH}`"
        :style="{ left: -g.ringsW / 2 + 'px', top: -g.ringsH / 2 + 'px' }"
        aria-hidden="true"
      >
        <ellipse
          class="ringShadow"
          :cx="g.ringsW / 2"
          :cy="g.ringsH / 2"
          :rx="g.shadow[0]"
          :ry="g.shadow[1]"
        />
        <ellipse
          v-if="wave"
          class="ringWave"
          :cx="g.ringsW / 2"
          :cy="g.ringsH / 2"
          :rx="g.rings[0].rx"
          :ry="g.rings[0].ry"
          stroke-width="1.4"
        />
        <ellipse
          v-for="(r, i) in g.rings"
          :key="i"
          class="ring"
          :cx="g.ringsW / 2"
          :cy="g.ringsH / 2"
          :rx="r.rx"
          :ry="r.ry"
          :stroke-opacity="r.o"
          :stroke-width="r.w"
          :style="pulse ? { animationDelay: i * 0.15 + 's' } : null"
        />
      </svg>

      <!-- teardrop with a real round hole (even-odd fill) -->
      <svg
        class="pin hit"
        :width="g.pinW"
        :height="g.pinH"
        viewBox="0 0 44 56"
        :style="{ left: -g.pinW / 2 + 'px', top: -g.pinTip + 'px' }"
        aria-hidden="true"
      >
        <path
          fill-rule="evenodd"
          :stroke-width="g.pinStroke"
          stroke-linejoin="round"
          d="M22 54C22 54 4 36.5 4 21a18 18 0 0 1 36 0c0 15.5-18 33-18 33zM15 21a7 7 0 1 0 14 0a7 7 0 1 0-14 0z"
        />
      </svg>

      <!-- leader line from the pin to the card -->
      <svg
        class="leader"
        width="34"
        :height="g.leaderH"
        :viewBox="`0 0 34 ${g.leaderH}`"
        aria-hidden="true"
      >
        <polyline
          :points="g.leader"
          stroke-width="1"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </template>

    <div class="markerCard hit">
      <span class="cardTop">
        <span class="caption">{{ caption }}</span>
        <MapTierChips v-if="tier" :tier="tier" />
      </span>
      <span class="cardPlace">
        <MapFlag :countryCode="countryCode" />
        <span class="placeName">{{ title }}</span>
        <span v-if="code" class="codeChip">{{ code }}</span>
      </span>
    </div>
  </div>
</template>

<script>
import MapFlag from "./map-flag.vue";
import MapTierChips from "./map-tier-chips.vue";

// Pin geometry (px). The teardrop artwork is 44 x 56 with its tip at y = 54.
const GEOMETRY = {
  connected: {
    ringsW: 68,
    ringsH: 26,
    shadow: [9, 3.2],
    rings: [
      { rx: 32, ry: 11.5, o: 0.2, w: 1.1 },
      { rx: 23.2, ry: 8.4, o: 0.36, w: 1.3 },
      { rx: 15.2, ry: 5.5, o: 0.62, w: 1.6 },
      { rx: 8, ry: 2.9, o: 1, w: 1.9 },
    ],
    pinW: 35.2, // 44 x 0.8
    pinH: 44.8,
    pinTip: 43.2, // 54 x 0.8
    pinStroke: 1.5,
    leaderH: 30,
    leader: "6,28 20,2 32,2",
  },
  selected: {
    ringsW: 60,
    ringsH: 24,
    shadow: [7.5, 2.7],
    rings: [
      { rx: 28, ry: 10.1, o: 0.16, w: 1 },
      { rx: 20.3, ry: 7.3, o: 0.28, w: 1.2 },
      { rx: 13.3, ry: 4.8, o: 0.48, w: 1.4 },
      { rx: 7, ry: 2.5, o: 0.8, w: 1.6 },
    ],
    pinW: 30.8, // 44 x 0.7
    pinH: 39.2,
    pinTip: 37.8, // 54 x 0.7
    pinStroke: 2.6,
    leaderH: 34,
    leader: "4.5,31 18,2 32,2",
  },
};

export default {
  components: { MapFlag, MapTierChips },
  props: {
    // "connected" | "selected" | "user"
    kind: { type: String, default: "selected" },
    // map point (px in the locations layer)
    x: { type: Number, default: 0 },
    y: { type: Number, default: 0 },
    // card: state caption ("CONNECTED", "SELECTED", "UNPROTECTED", ...), place and its marks
    caption: String,
    title: String,
    countryCode: String,
    code: String,
    tier: String, // "Free" | "Premium" | "Mixed" | null
    // card colours: "accent" | "neutral" | "danger" (default by kind)
    tone: String,
    // connected: an expanding ripple; connecting: the rings pulse
    // (the user's location: its outer ring breathes)
    wave: Boolean,
    pulse: Boolean,
    // accessible name of the marker group
    label: String,
  },
  computed: {
    g() {
      return GEOMETRY[this.kind] || GEOMETRY.selected;
    },
    cardTone() {
      if (this.tone) return this.tone;
      if (this.kind === "connected") return "accent";
      if (this.kind === "user") return "danger";
      return "neutral";
    },
  },
};
</script>

<style scoped lang="scss">
// Marker colours (light theme; dark values below). Gold is darkened in the
// light theme so the rings and the outlined pin keep their contrast on the pale map.
.mapMarker {
  --mk-ring: #d18f00;
  --mk-pin-ring: #c47f00;
  --mk-pin-outline: #ffffff;
  // edge of the gold (connected) pin: a white edge vanishes on the pale map (1.2:1),
  // dark gold keeps it 4.3:1 even on the filled (connected) country
  --mk-pin-edge: #a15f00;
  --mk-shadow: rgba(0, 0, 0, 0.16);
  --mk-leader-neutral: #a1a1aa;
  --mk-card-shadow: 0 1px 2px rgba(0, 0, 0, 0.06), 0 2px 8px rgba(0, 0, 0, 0.06);
  --mk-border-neutral: #d4d4d8;
  --mk-border-danger: #f4c7c3;
  --mk-danger-ring: rgba(229, 72, 77, 0.3);
  --mk-danger-halo: #fdeceb;
  --mk-danger-halo-ring: rgba(229, 72, 77, 0.5);

  position: absolute;
  width: 0;
  height: 0;
  pointer-events: none;
}
@media (prefers-color-scheme: dark) {
  .mapMarker {
    --mk-ring: #ffb000;
    --mk-pin-ring: #ffb000;
    --mk-pin-outline: #0b0b0d;
    --mk-pin-edge: #0b0b0d;
    --mk-shadow: rgba(0, 0, 0, 0.45);
    --mk-leader-neutral: #52525b;
    --mk-card-shadow: none;
    --mk-border-neutral: #34343a;
    --mk-border-danger: #4a2323;
    --mk-danger-ring: rgba(252, 165, 165, 0.28);
    --mk-danger-halo: #2a1515;
    --mk-danger-halo-ring: rgba(252, 165, 165, 0.55);
  }
}

.mapMarker svg {
  position: absolute;
  display: block;
  overflow: visible;
}
.hit {
  pointer-events: auto;
  cursor: pointer;
}

// ---------- user location ----------
.userDot {
  left: -18px;
  top: -18px;
}
.udOuter {
  fill: none;
  stroke: var(--mk-danger-ring);
  stroke-width: 1;
}
.udHalo {
  fill: var(--mk-danger-halo);
  stroke: var(--mk-danger-halo-ring);
  stroke-width: 1;
}
.udCore {
  fill: var(--danger-dot);
  stroke: var(--mk-pin-outline);
  stroke-width: 2;
}

// ---------- pin ----------
.ringShadow {
  fill: var(--mk-shadow);
}
.ring,
.ringWave {
  fill: none;
  stroke: var(--mk-ring);
}
.kind-connected .pin path {
  fill: var(--accent-color);
  stroke: var(--mk-pin-edge);
}
.kind-selected .pin path {
  fill: var(--surface-color);
  stroke: var(--mk-pin-ring);
}
.leader {
  left: 8px;
  top: -60px;
}
.leader polyline {
  fill: none;
  stroke: var(--mk-leader-neutral);
}
.kind-connected .leader polyline {
  stroke: var(--mk-ring);
}

// connected: one ring keeps expanding from the pin (every 5 s, as the old waves)
.ringWave {
  opacity: 0;
  transform-box: fill-box;
  transform-origin: center;
  animation: mkWave 5s ease-out infinite;
}
@keyframes mkWave {
  0% {
    opacity: 0.9;
    transform: scale(0.25);
  }
  60% {
    opacity: 0;
    transform: scale(1.25);
  }
  100% {
    opacity: 0;
    transform: scale(1.25);
  }
}
// connecting: the rings pulse
// (each ring starts 0.15 s after the previous one: inline animation-delay)
.pulsing .ring {
  animation: mkPulse 1.2s ease-in-out infinite alternate;
}
@keyframes mkPulse {
  from {
    opacity: 1;
  }
  to {
    opacity: 0.3;
  }
}
// connecting: the outer ring of the user's location breathes, softly. It is drawn by
// an HTML ring in place of the SVG one (.udOuter, same place and size): its transform
// runs on the compositor, where a transform on an SVG shape lays it out every frame.
.udPulse {
  position: absolute;
  left: -17px;
  top: -17px;
  width: 34px;
  height: 34px;
  box-sizing: border-box;
  border: 1px solid var(--mk-danger-ring);
  border-radius: 50%;
  pointer-events: none;
  animation: mkUserPulse 1.6s ease-in-out infinite;
}
.kind-user.pulsing .udOuter {
  visibility: hidden;
}
@keyframes mkUserPulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.35;
    transform: scale(1.22);
  }
}
@media (prefers-reduced-motion: reduce) {
  .ringWave {
    display: none;
  }
  .pulsing .ring,
  .udPulse {
    animation: none;
  }
}

// ---------- label card ----------
.markerCard {
  position: absolute;
  left: 40px;
  top: -100px;
  box-sizing: border-box;
  padding: 6px 8px 7px;
  border: 1px solid var(--mk-border-neutral);
  border-radius: 9px;
  background: var(--surface-color);
  box-shadow: var(--mk-card-shadow);
  display: flex;
  flex-direction: column;
  gap: 4px;
  white-space: nowrap;
}
.kind-user .markerCard {
  left: 20px;
  top: -25px;
}
.tone-accent .markerCard {
  border-color: var(--accent-ring);
}
.tone-danger .markerCard {
  border-color: var(--mk-border-danger);
}

.cardTop {
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.caption {
  display: block;
  font-size: 10px;
  font-weight: 700;
  line-height: 12px;
  letter-spacing: 0.1em;
  white-space: nowrap;
  color: var(--text-muted);
}
.tone-accent .caption {
  color: var(--link-color);
}
.tone-danger .caption {
  color: var(--danger-text);
}

.cardPlace {
  height: 16px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.placeName {
  display: block;
  max-width: 168px;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12.5px;
  font-weight: 600;
  line-height: 16px;
  color: var(--text-color);
}
.codeChip {
  flex: none;
  display: block;
  height: 16px;
  box-sizing: border-box;
  padding: 0 4px;
  border-radius: 4px;
  background: var(--neutral-tint);
  color: var(--text-soft);
  font-size: 9.5px;
  font-weight: 700;
  line-height: 16px;
  letter-spacing: 0.04em;
}
</style>
