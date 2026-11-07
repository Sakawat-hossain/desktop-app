<template>
  <!-- Decorative: the text next to it already names the server -->
  <span class="serverFlag" :style="boxStyle" aria-hidden="true">
    <span
      class="flagFace"
      :class="{
        modeFastest: kind === 'fastest',
        modeRandom: kind === 'random',
        unknownTile: !isModeIcon && !isFlagShown,
        flagTile: !isModeIcon && isFlagShown,
        withRing: ring,
      }"
      :style="faceStyle"
    >
      <!-- Fastest server: bolt -->
      <svg
        v-if="kind === 'fastest'"
        class="tileIcon"
        :width="iconSize"
        :height="iconSize"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M13 2 4 14h7l-1 8 9-12h-7z" />
      </svg>

      <!-- Random server: shuffle -->
      <svg
        v-else-if="kind === 'random'"
        class="tileIcon"
        :width="iconSize"
        :height="iconSize"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5" />
      </svg>

      <!-- Country flag: 21x15 artwork, drawn at the same 7:5 proportion -->
      <img
        v-else-if="isFlagShown"
        class="flagImg"
        :src="flagSrc"
        alt=""
        draggable="false"
        @error="onFlagLoadError"
      />

      <!-- No country known (or the flag file is missing): globe -->
      <svg
        v-else
        class="tileIcon"
        :width="iconSize"
        :height="iconSize"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="12" r="9" />
        <path
          d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"
        />
      </svg>

      <!-- 1 px inner outline: keeps white and dark flag edges visible on the card -->
      <span v-if="isFlagShown && !isModeIcon && outline" class="flagOutline" />
    </span>

    <!-- Fastest/Random: small flag of the server in use, on the tile's corner -->
    <span v-if="isBadgeShown" class="flagBadge" :style="badgeStyle">
      <img
        class="flagImg"
        :src="badgeSrc"
        alt=""
        draggable="false"
        @error="onBadgeLoadError"
      />
      <span class="flagOutline" />
    </span>
  </span>
</template>

<script>
function flagPath(countryCode) {
  if (!countryCode || typeof countryCode !== "string") return null;
  const cc = countryCode.trim().toUpperCase();
  if (!cc) return null;
  return `flags/svg/${cc}.svg`;
}

export default {
  props: {
    // ISO country code of the server ("BD", "us", ...)
    countryCode: String,
    // "flag" (default), "fastest" or "random"
    kind: { type: String, default: "flag" },
    // box size in px; the height defaults to the flag's 7:5 proportion
    width: { type: Number, default: 0 },
    height: { type: Number, default: 0 },
    // older name of "width"
    size: { type: Number, default: 0 },
    // corner radius in px (default: 4 for big flags, 3 for small ones;
    // icon tiles are rounder)
    radius: { type: Number, default: null },
    // draw a 2px surface gap + 1px gold ring around the box
    ring: { type: Boolean, default: false },
    // 1px inner outline around a flag
    outline: { type: Boolean, default: true },
    // Fastest/Random tiles: country of the server in use (small flag badge)
    badgeCountryCode: String,
  },
  data: () => ({
    isLoadError: false,
    isBadgeLoadError: false,
  }),
  watch: {
    countryCode() {
      // a new country gets a new chance to load its flag
      this.isLoadError = false;
    },
    badgeCountryCode() {
      this.isBadgeLoadError = false;
    },
  },
  computed: {
    isModeIcon() {
      return this.kind === "fastest" || this.kind === "random";
    },
    flagSrc() {
      return flagPath(this.countryCode);
    },
    isFlagShown() {
      return this.flagSrc != null && this.isLoadError !== true;
    },
    badgeSrc() {
      return flagPath(this.badgeCountryCode);
    },
    isBadgeShown() {
      return (
        this.isModeIcon &&
        this.badgeSrc != null &&
        this.isBadgeLoadError !== true
      );
    },

    boxWidth() {
      return this.width > 0 ? this.width : this.size > 0 ? this.size : 42;
    },
    boxHeight() {
      return this.height > 0
        ? this.height
        : Math.round((this.boxWidth * 5) / 7);
    },
    faceRadius() {
      if (this.radius != null) return this.radius;
      // icon tiles: 8 px at 30 px tall, like the 28 px Quick connect tiles
      if (this.isModeIcon || !this.isFlagShown)
        return Math.max(3, Math.round(this.boxHeight / 3.75));
      return this.boxWidth >= 36 ? 4 : this.boxWidth >= 18 ? 3 : 2;
    },
    boxStyle() {
      return { width: `${this.boxWidth}px`, height: `${this.boxHeight}px` };
    },
    faceStyle() {
      return { borderRadius: `${this.faceRadius}px` };
    },
    iconSize() {
      // 16 px inside the 30 px tall tile
      return Math.max(10, Math.round(this.boxHeight * 0.53));
    },
    badgeStyle() {
      // 14 x 10 on a 42 px box, reaching 3 px past its corner
      const w = Math.max(10, Math.round(this.boxWidth / 3));
      const h = Math.round((w * 5) / 7);
      const out = Math.round(w * 0.2);
      return {
        width: `${w}px`,
        height: `${h}px`,
        right: `${-out}px`,
        bottom: `${-out}px`,
      };
    },
  },
  methods: {
    onFlagLoadError() {
      this.isLoadError = true;
    },
    onBadgeLoadError() {
      this.isBadgeLoadError = true;
    },
  },
};
</script>

<style scoped lang="scss">
// the global 'html *' rule gives every element the text colour:
// let the icons take the colour of their tile instead
svg,
svg * {
  color: inherit;
}

.serverFlag {
  // outline of a flag: dark line on the light card, light line on the dark one
  --server-flag-outline: rgba(22, 22, 26, 0.14);

  position: relative;
  flex: none;
  display: block;
}
@media (prefers-color-scheme: dark) {
  .serverFlag {
    --server-flag-outline: rgba(255, 255, 255, 0.18);
  }
}

.flagFace {
  position: absolute;
  inset: 0;
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.flagFace.withRing {
  box-shadow:
    0 0 0 2px var(--surface-color),
    0 0 0 3px var(--accent-ring);
}

.flagImg {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
}

.flagOutline {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: inset 0 0 0 1px var(--server-flag-outline);
  pointer-events: none;
}

.tileIcon {
  display: block;
  flex: none;
}

// shown behind a flag while its file loads
.flagTile {
  background: var(--neutral-tint);
}

// the same tiles as the Fastest and Random cards in the server list
.modeFastest {
  border: 1px solid var(--accent-ring);
  background: var(--accent-tint);
  color: var(--link-color);
}
.modeRandom {
  border: 1px solid var(--control-border);
  background: var(--neutral-tint);
  color: var(--text-soft);
}
.unknownTile {
  border: 1px solid var(--control-border);
  background: var(--neutral-tint);
  color: var(--text-muted);
}

.flagBadge {
  position: absolute;
  box-sizing: border-box;
  border-radius: 2px;
  overflow: hidden;
  background: var(--neutral-tint);
  // separates the badge from the tile it sits on
  box-shadow: 0 0 0 1.5px var(--server-flag-badge-ring, var(--surface-color));
}
</style>
