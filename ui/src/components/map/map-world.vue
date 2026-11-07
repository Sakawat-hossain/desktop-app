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
    <!-- soft halo along the coasts: a wide, faint stroke under the land -->
    <g class="coastHalo">
      <path v-for="(d, i) in paths" :key="'h' + i" :d="d" />
    </g>

    <!-- land; countries that have servers are a little lighter -->
    <g class="land">
      <path
        v-for="(d, i) in paths"
        :key="'l' + i"
        :d="d"
        :class="{ hasServers: serverCountrySet[i] === true }"
      />
    </g>

    <!-- the country of the connected server: filled, brighter border, soft halo -->
    <g v-if="highlightPath" class="countryOn">
      <path class="countryOnHalo" :d="highlightPath" />
      <path class="countryOnShape" :d="highlightPath" />
    </g>
  </svg>
</template>

<script>
import { MAP_PATHS, MAP_WIDTH, MAP_HEIGHT } from "./map-geometry";

export default {
  props: {
    // index (in MAP_PATHS) of the country to highlight, -1 for none
    highlightIndex: { type: Number, default: -1 },
    // indexes (in MAP_PATHS) of the countries that have servers
    serverCountries: { type: Array, default: () => [] },
  },
  setup() {
    // plain (not reactive) constants: 176 long path strings
    return {
      paths: MAP_PATHS,
      viewBox: `0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`,
    };
  },
  computed: {
    serverCountrySet() {
      const set = {};
      for (const i of this.serverCountries) set[i] = true;
      return set;
    },
    highlightPath() {
      if (this.highlightIndex < 0) return null;
      return MAP_PATHS[this.highlightIndex] || null;
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

.coastHalo path {
  fill: none;
  stroke: var(--wm-coast-halo);
  stroke-width: 7px;
}

.land path {
  fill: var(--wm-land);
  stroke: var(--wm-border);
  stroke-width: 1px;
}
.land path.hasServers {
  fill: var(--wm-land-servers);
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
