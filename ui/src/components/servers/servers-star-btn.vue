<template>
  <button
    type="button"
    class="starBtn"
    :class="{ fav: pressed }"
    :aria-pressed="pressed ? 'true' : 'false'"
    :aria-label="label"
    :title="label"
    v-on:click="$emit('click', $event)"
  >
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      stroke-width="1.8"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path
        d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"
      />
    </svg>
  </button>
</template>

<script>
// Favourite star (28 px), the column before the chevron column of a card.
export default {
  emits: ["click"],
  props: {
    pressed: Boolean,
    // "Add Japan to favorites" / "Remove Japan from favorites"
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

.starBtn {
  width: 28px;
  height: 28px;
  flex: none;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 7px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.starBtn svg {
  display: block;
  fill: none;
  stroke: var(--text-faint);
}
.starBtn:hover {
  background: var(--neutral-tint);
}
.starBtn:hover svg {
  stroke: var(--text-soft);
}
.starBtn.fav svg,
.starBtn.fav:hover svg {
  fill: var(--accent-color);
  stroke: var(--accent-color);
}
.starBtn:focus {
  outline: none;
}
.starBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
</style>
