<template>
  <div
    class="mapMarker"
    :class="[
      'kind-' + kind,
      'tone-' + cardTone,
      { pulsing: pulse, cardLeft: kind === 'user' && cardSide === 'left' },
    ]"
    :style="{ left: x + 'px', top: y + 'px' }"
    role="group"
    :aria-label="label"
  >
    <!--
      A map marker with its label card, anchored at (x, y): the map point.
        kind "connected": gold teardrop pin on elliptical ripple rings + leader line + card
        kind "selected":  outlined pin (selected / connecting / paused server) + leader line + card
        kind "user":      the user's own location: a red teardrop pin on two elliptical
                          ripples, a short stem to its card beside the pin (right, or left
                          near the right edge of the map: 'cardSide')
      Only the pins and the cards take the pointer; their clicks and wheel events
      bubble to this root element, where the parent's @click / @wheel listeners sit.
      (No comment above the root element: the component must keep one root node.)
    -->
    <template v-if="kind === 'user'">
      <!-- connecting: a third, wider ripple breathes (an HTML ring: see .uRingPulse) -->
      <span v-if="pulse" class="uRingPulse" aria-hidden="true"></span>
      <svg
        class="uRings"
        width="72"
        height="28"
        viewBox="0 0 72 28"
        aria-hidden="true"
      >
        <ellipse class="uShadow" cx="36" cy="14" rx="5.5" ry="2" />
        <ellipse
          class="uRingOuter"
          cx="36"
          cy="14"
          rx="22"
          ry="8"
          stroke-width="1.1"
        />
        <ellipse
          class="uRingInner"
          cx="36"
          cy="14"
          rx="12"
          ry="4.4"
          stroke-width="1.3"
        />
      </svg>

      <!-- teardrop with a real round hole (even-odd fill); its tip is the map point -->
      <svg
        class="uPin hit"
        width="22"
        height="28"
        viewBox="0 0 44 56"
        aria-hidden="true"
      >
        <path
          fill-rule="evenodd"
          stroke-width="2.4"
          stroke-linejoin="round"
          d="M22 54C22 54 4 36.5 4 21a18 18 0 0 1 36 0c0 15.5-18 33-18 33zM15 21a7 7 0 1 0 14 0a7 7 0 1 0-14 0z"
        />
      </svg>

      <!-- the stem from the pin head to the card -->
      <span class="uStem" aria-hidden="true"></span>

      <div
        ref="userCard"
        class="userCard hit"
        :style="{ top: pin.headY + cardDy + 'px' }"
      >
        <span class="uCaptionRow">
          <svg
            v-if="cardTone === 'danger'"
            class="uShieldOff"
            width="12"
            height="12"
            viewBox="0 0 24 24"
            stroke-width="2.2"
            aria-hidden="true"
          >
            <path
              class="uShield"
              d="M12 3 4 6v6c0 4.5 3.4 8.2 8 9 4.6-.8 8-4.5 8-9V6z"
            />
            <!-- the slash cuts the shield: a gap in the card colour under it -->
            <path class="uSlashGap" stroke-width="5.4" d="M3.5 3.5 20.5 20.5" />
            <path class="uSlash" d="M3.5 3.5 20.5 20.5" />
          </svg>
          <span class="caption">{{ caption }}</span>
        </span>
        <span class="uPlaceRow">
          <MapFlag :countryCode="countryCode" />
          <span class="placeName uPlaceName">{{ title }}</span>
          <span v-if="code" class="codeChip">{{ code }}</span>
        </span>
        <!-- "Your real IP is visible"; connecting: a gold spinner + "Connecting..." -->
        <span v-if="note" class="uNote" :class="{ busy: pulse }">
          <svg
            v-if="pulse"
            class="uSpinner"
            width="10"
            height="10"
            viewBox="0 0 10 10"
            stroke-width="1.6"
            aria-hidden="true"
          >
            <circle class="uSpinTrack" cx="5" cy="5" r="3.8" />
            <path class="uSpinArc" d="M5 1.2A3.8 3.8 0 0 1 8.8 5" />
          </svg>
          <span class="uNoteText">{{ note }}</span>
        </span>
      </div>
    </template>

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
    </template>
  </div>
</template>

<script>
import MapFlag from "./map-flag.vue";
import MapTierChips from "./map-tier-chips.vue";
import { USER_PIN } from "./map-geometry";

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
    // card: state caption ("PROTECTED", "SELECTED", "NOT PROTECTED", ...), place and its marks
    caption: String,
    title: String,
    countryCode: String,
    code: String,
    tier: String, // "Free" | "Premium" | "Mixed" | null
    // card colours: "accent" | "neutral" | "danger" (default by kind)
    tone: String,
    // connected: an expanding ripple; connecting: the rings pulse
    // (the user's location: a wider ripple breathes, its card says "Connecting...")
    wave: Boolean,
    pulse: Boolean,
    // accessible name of the marker group
    label: String,
    // the user's location only: the third line of the card ("Your real IP is visible"),
    // the side of the pin the card is on ("right" | "left") and how far (px) it slides
    // down (+) or up (-) from its place centred on the pin head, to stay in view
    note: String,
    cardSide: { type: String, default: "right" },
    cardDy: { type: Number, default: 0 },
  },
  // the user's location: the size of its card ({ w, h }, px) whenever it changes
  emits: ["cardSize"],
  setup() {
    return { pin: USER_PIN };
  },
  mounted() {
    const card = this.$refs.userCard;
    if (!card || typeof ResizeObserver === "undefined") return;
    // (the observer reports the first size at once, then every change: a new place
    // name, the "Connecting..." line, the font once it is loaded)
    this.cardObserver = new ResizeObserver(() => {
      if (!card.isConnected) return;
      this.$emit("cardSize", { w: card.offsetWidth, h: card.offsetHeight });
    });
    this.cardObserver.observe(card);
  },
  beforeUnmount() {
    if (this.cardObserver) {
      this.cardObserver.disconnect();
      this.cardObserver = null;
    }
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
  // the user's pin: its shadow and the ripple that breathes while connecting
  --mk-danger-shadow: rgba(0, 0, 0, 0.16);
  --mk-danger-pulse: rgba(229, 72, 77, 0.2);

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
    --mk-danger-shadow: rgba(0, 0, 0, 0.5);
    --mk-danger-pulse: rgba(248, 113, 113, 0.16);
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

// ---------- user location: red pin on two ripples ----------
.uRings {
  left: -36px;
  top: -14px;
}
.uShadow {
  fill: var(--mk-danger-shadow);
}
.uRingOuter {
  fill: none;
  stroke: var(--danger-dot);
  stroke-opacity: 0.32;
}
.pulsing .uRingOuter {
  stroke-opacity: 0.42;
}
.uRingInner {
  fill: var(--danger-dot);
  fill-opacity: 0.12;
  stroke: var(--danger-dot);
  stroke-opacity: 0.78;
}
// 44 x 56 artwork at half size: its tip (22, 54) on the map point
.uPin {
  left: -11px;
  top: -27px;
}
.uPin path {
  fill: var(--danger-dot);
  stroke: var(--mk-pin-outline);
}
// from the edge of the pin head (9.6 px) to the card (24 px: USER_PIN.cardGap),
// on the line of the head centre (USER_PIN.headY)
.uStem {
  position: absolute;
  left: 10px;
  top: -17px;
  width: 14px;
  height: 1px;
  background: var(--danger-dot);
  opacity: 0.65;
}
.cardLeft .uStem {
  left: -24px;
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
// connecting: a third, wider ripple around the user's pin breathes, softly. It is an
// HTML ring (an ellipse: 66 x 24, 50 % corners): its transform runs on the compositor,
// where a transform on an SVG shape lays it out every frame.
.uRingPulse {
  position: absolute;
  left: -33px;
  top: -12px;
  width: 66px;
  height: 24px;
  box-sizing: border-box;
  border: 1px solid var(--mk-danger-pulse);
  border-radius: 50%;
  pointer-events: none;
  animation: mkUserPulse 1.6s ease-in-out infinite;
}
@keyframes mkUserPulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.35;
    transform: scale(1.12);
  }
}
// connecting: the spinner on the card turns
.uSpinner {
  animation: mkSpin 0.9s linear infinite;
}
@keyframes mkSpin {
  to {
    transform: rotate(360deg);
  }
}
@media (prefers-reduced-motion: reduce) {
  .ringWave {
    display: none;
  }
  .pulsing .ring,
  .uRingPulse,
  .uSpinner {
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

// ---------- the user's card: beside the pin, centred on the pin head ----------
// ('top' is the head line, moved by cardDy; the card is centred on it by its transform)
.userCard {
  position: absolute;
  left: 24px; // USER_PIN.cardGap
  transform: translateY(-50%);
  box-sizing: border-box;
  padding: 7px 10px 8px;
  border: 1px solid var(--mk-border-neutral);
  border-radius: 10px;
  background: var(--surface-color);
  box-shadow: var(--mk-card-shadow);
  display: flex;
  flex-direction: column;
  gap: 5px;
  white-space: nowrap;
}
.cardLeft .userCard {
  left: auto;
  right: 24px;
}
.tone-danger .userCard {
  border-color: var(--mk-border-danger);
}
.uCaptionRow {
  height: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}
// shield-off: the shield and its slash in the danger colour, cut by a gap
// (".userCard" first: the icons of the card are not placed as the marker's own SVGs)
.userCard .uShieldOff {
  position: static;
  flex: none;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.uShield,
.uSlash {
  stroke: var(--danger-text);
}
.uSlashGap {
  stroke: var(--surface-color);
}
.uPlaceRow {
  height: 18px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.uPlaceName {
  font-size: 13px;
  line-height: 18px;
}
.uNote {
  height: 15px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  line-height: 15px;
  color: var(--text-muted);
}
.uNote.busy {
  font-weight: 500;
  color: var(--link-color);
}
// App.vue gives every element the text colour: the text follows its line
.uNoteText {
  display: block;
  color: inherit;
}
.userCard .uSpinner {
  position: static;
  flex: none;
  fill: none;
  stroke-linecap: round;
}
.uSpinTrack {
  stroke: var(--accent-ring);
}
.uSpinArc {
  stroke: var(--link-color);
}
</style>
