<template>
  <svg
    class="worldMap"
    :viewBox="viewBox"
    preserveAspectRatio="none"
    aria-hidden="true"
    focusable="false"
  >
    <!--
      The world map, drawn inline so countries can be styled. The parent sizes it
      (width/height in px); the viewBox maps the map units onto that size.
      Stroke widths are screen pixels at every zoom (non-scaling strokes).
      (No comment above the root element: the component must keep one root node.)
    -->
    <!-- faint graticule on the ocean: a line every 10 degrees -->
    <path class="graticule" :d="graticule" />

    <!-- soft halo along the coasts: a wide, faint stroke under the land -->
    <g class="coastHalo">
      <path v-for="(d, i) in paths" :key="'h' + i" :d="d" />
    </g>

    <!-- land -->
    <g class="land">
      <path v-for="(d, i) in paths" :key="'l' + i" :d="d" />
    </g>

    <!-- countries that have servers: a lighter land with a brighter border (drawn over
         the borders of their neighbours) -->
    <g class="landServers">
      <path v-for="i in serverCountries" :key="'s' + i" :d="paths[i]" />
    </g>

    <!-- the user's own country while not protected: softly tinted in the danger colour -->
    <path
      v-if="userPath"
      :key="'u' + userCountryIndex"
      class="userCountry"
      :d="userPath"
    />

    <!-- the country of the connected server: filled, brighter border, soft halo -->
    <g v-if="highlightPath" class="countryOn">
      <path class="countryOnHalo" :d="highlightPath" />
      <path class="countryOnShape" :d="highlightPath" />
    </g>
  </svg>
</template>

<script>
import {
  MAP_PATHS,
  MAP_WIDTH,
  MAP_HEIGHT,
  GRATICULE_PATH,
} from "./map-geometry";

export default {
  props: {
    // index (in MAP_PATHS) of the country to highlight, -1 for none
    highlightIndex: { type: Number, default: -1 },
    // index (in MAP_PATHS) of the user's own country to tint, -1 for none
    userCountryIndex: { type: Number, default: -1 },
    // indexes (in MAP_PATHS) of the countries that have servers
    serverCountries: { type: Array, default: () => [] },
  },
  setup() {
    // plain (not reactive) constants: 176 long path strings
    return {
      paths: MAP_PATHS,
      graticule: GRATICULE_PATH,
      viewBox: `0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`,
    };
  },
  computed: {
    highlightPath() {
      if (this.highlightIndex < 0) return null;
      return MAP_PATHS[this.highlightIndex] || null;
    },
    userPath() {
      if (this.userCountryIndex < 0) return null;
      return MAP_PATHS[this.userCountryIndex] || null;
    },
  },
};
</script>

<style scoped lang="scss">
// Colours come from the map tokens (--wm-*) set on the map view (Component-Map.vue).
.worldMap {
  display: block;
  overflow: visible;
  pointer-events: none;
  user-select: none;
}

.worldMap path {
  vector-effect: non-scaling-stroke;
  stroke-linejoin: round;
}

.graticule {
  fill: none;
  stroke: var(--wm-grid);
  stroke-width: 1px;
}

.coastHalo path {
  fill: none;
  stroke: var(--wm-coast-halo);
  stroke-width: 9px;
}

.land path {
  fill: var(--wm-land);
  stroke: var(--wm-border);
  stroke-width: 1px;
}
.landServers path {
  fill: var(--wm-land-servers);
  stroke: var(--wm-border-servers);
  stroke-width: 1px;
}

// the user's country fades in with its marker (the location arrives after a disconnect)
.userCountry {
  fill: var(--wm-user-fill);
  stroke: var(--wm-user-border);
  stroke-width: 1px;
  animation: wmCountryOn 0.6s ease-out;
}

// the connected country fades in (with the move of the map into it)
.countryOn {
  animation: wmCountryOn 0.9s ease-out;
}
@keyframes wmCountryOn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@media (prefers-reduced-motion: reduce) {
  .userCountry,
  .countryOn {
    animation: none;
  }
}
.countryOnHalo {
  fill: none;
  stroke: var(--wm-on-halo);
  stroke-width: 10px;
}
.countryOnShape {
  fill: var(--wm-on-fill);
  stroke: var(--wm-on-border);
  stroke-width: 1.5px;
}
</style>
