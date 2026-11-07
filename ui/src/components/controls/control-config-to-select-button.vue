<template>
  <!-- A 48 px card row: [icon] title + description, [marker], chevron -->
  <button type="button" class="row selectRow" v-on:click="click">
    <span v-if="$slots.icon" class="rowIcon" aria-hidden="true">
      <slot name="icon" />
    </span>

    <span class="rowText">
      <span class="rowTitle">{{ text }}</span>
      <span v-if="description" class="rowDesc">{{ description }}</span>
    </span>

    <span v-if="isShowMarker" class="marker" :style="markerStyle">
      {{ markerText }}
    </span>

    <svg
      class="chevron"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="m9 6 6 6-6 6" />
    </svg>
  </button>
</template>

<script>
export default {
  props: [
    "click",
    "text",
    "description",
    "markerText",
    "markerColor",
    "markerTextColor",
  ],
  computed: {
    isShowMarker: function () {
      return this.markerText != null && this.markerColor != null;
    },
    markerStyle: function () {
      let ret = `background: ${this.markerColor};`;
      if (this.markerTextColor) ret += ` color: ${this.markerTextColor};`;
      return ret;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

// the global 'html *' rule gives every element the text colour:
// let the chevron take the colour set on it
svg,
svg * {
  color: inherit;
}

.row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  min-height: 48px;
  box-sizing: border-box;
  margin: 0;
  padding: 6px 14px;
  border: 0;
  border-radius: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.15s;
}
.selectRow:hover {
  background: var(--neutral-tint);
}
// the card clips its children: draw the focus ring inside the row
.selectRow:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}

.rowIcon {
  width: 18px;
  height: 18px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.rowText {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.rowTitle {
  font-size: 13.5px;
  font-weight: 500;
  line-height: 18px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rowDesc {
  font-size: 11.5px;
  line-height: 15px;
  color: var(--text-faint);
  overflow-wrap: anywhere;
}

.marker {
  flex: none;
  padding: 3px 5px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  line-height: 12px;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.chevron {
  flex: none;
  color: var(--text-faint);
}
</style>
