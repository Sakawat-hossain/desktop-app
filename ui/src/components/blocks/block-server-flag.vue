<template>
  <!-- Decorative: the text next to it already names the server -->
  <span
    class="serverFlag"
    :class="{
      modeTile: isModeIcon,
      unknownTile: !isModeIcon && !isFlagShown,
      withRing: ring,
    }"
    :style="tileStyle"
    aria-hidden="true"
  >
    <!-- Fastest server: bolt -->
    <svg
      v-if="kind === 'fastest'"
      class="tileIcon"
      :width="iconSize"
      :height="iconSize"
      viewBox="0 0 24 24"
      stroke-width="1.9"
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
      stroke-width="1.9"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5" />
    </svg>

    <!-- Country flag (21x15 artwork, cropped to the circle) -->
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
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z" />
    </svg>
  </span>
</template>

<script>
export default {
  props: {
    // ISO country code of the server ("BD", "us", ...)
    countryCode: String,
    // "flag" (default), "fastest" or "random"
    kind: { type: String, default: "flag" },
    // tile diameter in px
    size: { type: Number, default: 38 },
    // draw the 2px surface gap + 1px gold ring around the tile
    ring: { type: Boolean, default: true },
  },
  data: () => ({
    isLoadError: false,
  }),
  watch: {
    countryCode() {
      // a new country gets a new chance to load its flag
      this.isLoadError = false;
    },
  },
  computed: {
    isModeIcon() {
      return this.kind === "fastest" || this.kind === "random";
    },
    flagSrc() {
      if (!this.countryCode || typeof this.countryCode !== "string")
        return null;
      const cc = this.countryCode.trim().toUpperCase();
      if (!cc) return null;
      return `flags/svg/${cc}.svg`;
    },
    isFlagShown() {
      return this.flagSrc != null && this.isLoadError !== true;
    },
    tileStyle() {
      return { width: `${this.size}px`, height: `${this.size}px` };
    },
    iconSize() {
      // 18 px inside the 38 px tile
      return Math.max(12, Math.round((this.size * 18) / 38));
    },
  },
  methods: {
    onFlagLoadError() {
      this.isLoadError = true;
    },
  },
};
</script>

<style scoped lang="scss">
.serverFlag {
  flex: none;
  box-sizing: border-box;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--neutral-tint);
}
.serverFlag.withRing {
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

// The global "html * { color }" rule stops currentColor from inheriting,
// so the stroke colour is set here directly.
.tileIcon {
  display: block;
  flex: none;
  fill: none;
}

.modeTile {
  background: var(--accent-tint);
}
.modeTile .tileIcon {
  stroke: var(--link-color);
}

.unknownTile .tileIcon {
  stroke: var(--text-muted);
}
</style>
