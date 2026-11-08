<template>
  <button
    type="button"
    class="chevronBtn"
    :class="{ expanded: expanded }"
    :aria-expanded="expanded ? 'true' : 'false'"
    :aria-label="label"
    :title="label"
    v-on:click="$emit('click', $event)"
  >
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke-width="2.4"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path :d="expanded ? 'm6 9 6 6 6-6' : 'm9 6 6 6-6 6'" />
    </svg>
  </button>
</template>

<script>
// Open / close chevron (24 x 28 px), the last column of a card.
export default {
  emits: ["click"],
  props: {
    expanded: Boolean,
    // "Show cities in Japan" / "Hide servers in Tokyo"
    label: String,
  },
};
</script>

<style scoped lang="scss">
// the global 'html * { color }' rule stops currentColor from inheriting
svg,
svg * {
  color: inherit;
}

.chevronBtn {
  position: relative;
  width: 24px;
  height: 28px;
  flex: none;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 6px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
// 28 px hit target: the extra 4 px lie over the card's edge, not over the star
.chevronBtn::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: -4px;
}
.chevronBtn svg {
  display: block;
  stroke: var(--text-muted);
}
.chevronBtn.expanded svg {
  stroke: var(--text-soft);
}
.chevronBtn:hover {
  background: var(--neutral-tint);
}
.chevronBtn:hover svg {
  stroke: var(--text-color);
}
.chevronBtn:focus {
  outline: none;
}
.chevronBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
</style>
