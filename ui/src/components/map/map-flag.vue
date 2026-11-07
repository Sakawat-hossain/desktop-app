<template>
  <span class="mapFlag" aria-hidden="true">
    <!-- Decorative: the text next to it names the place -->
    <img
      v-if="src && !isLoadError"
      class="mapFlagImg"
      :src="src"
      alt=""
      draggable="false"
      @error="isLoadError = true"
    />
    <span class="mapFlagOutline"></span>
  </span>
</template>

<script>
// Rectangular 21 x 15 flag (7:5, the size of the artwork in public/flags/svg)
// with 3 px corners and a 1 px inner outline. A missing flag leaves a neutral tile.
export default {
  props: {
    countryCode: String,
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
    src() {
      if (!this.countryCode || typeof this.countryCode !== "string")
        return null;
      const cc = this.countryCode.trim().toUpperCase();
      if (!/^[A-Z]{2}$/.test(cc)) return null;
      return `flags/svg/${cc}.svg`;
    },
  },
};
</script>

<style scoped lang="scss">
.mapFlag {
  // light theme outline; the dark value is below
  --map-flag-outline: rgba(0, 0, 0, 0.12);

  position: relative;
  width: 21px;
  height: 15px;
  flex: none;
  display: block;
  border-radius: 3px;
  overflow: hidden;
  background: var(--neutral-tint);
}
@media (prefers-color-scheme: dark) {
  .mapFlag {
    --map-flag-outline: rgba(255, 255, 255, 0.18);
  }
}
.mapFlagImg {
  display: block;
  width: 21px;
  height: 15px;
  object-fit: cover;
  pointer-events: none;
}
.mapFlagOutline {
  position: absolute;
  inset: 0;
  display: block;
  border-radius: 3px;
  box-shadow: inset 0 0 0 1px var(--map-flag-outline);
  pointer-events: none;
}
</style>
