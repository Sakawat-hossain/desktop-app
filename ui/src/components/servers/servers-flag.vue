<template>
  <!-- Decorative: the text next to it names the location -->
  <span class="srvFlag" :class="{ dim: dim }" aria-hidden="true">
    <img
      v-if="src && !isLoadError"
      class="srvFlagImg"
      :src="src"
      alt=""
      draggable="false"
      @error="isLoadError = true"
    />
    <span class="srvFlagOutline"></span>
  </span>
</template>

<script>
// Rectangular 21 x 15 flag (7:5, the size of the flag artwork in public/flags/svg)
// with 3 px corners and a 1 px inner outline.
export default {
  props: {
    countryCode: String,
    // locked rows show the flag at 45 %
    dim: Boolean,
  },
  data: () => ({
    isLoadError: false,
  }),
  watch: {
    countryCode() {
      this.isLoadError = false;
    },
  },
  computed: {
    src() {
      if (!this.countryCode || typeof this.countryCode !== "string")
        return null;
      const cc = this.countryCode.trim().toUpperCase();
      if (!cc) return null;
      return `flags/svg/${cc}.svg`;
    },
  },
};
</script>

<style scoped lang="scss">
.srvFlag {
  position: relative;
  width: 21px;
  height: 15px;
  flex: none;
  display: block;
  border-radius: 3px;
  overflow: hidden;
  // shown when the flag file is missing
  background: var(--neutral-tint);
}
.srvFlag.dim {
  opacity: 0.45;
}
.srvFlagImg {
  display: block;
  width: 21px;
  height: 15px;
  object-fit: cover;
  pointer-events: none;
}
.srvFlagOutline {
  position: absolute;
  inset: 0;
  display: block;
  border-radius: 3px;
  box-shadow: inset 0 0 0 1px var(--srv-flag-outline, rgba(0, 0, 0, 0.12));
  pointer-events: none;
}
</style>
