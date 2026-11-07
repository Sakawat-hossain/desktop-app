<template>
  <div class="hoverTip" role="tooltip">
    <!-- Label of the server under the mouse: flag, city, Free/Premium mark (and a lock when the account cannot use it) -->
    <MapFlag :countryCode="countryCode" />
    <span class="tipName">{{ title }}</span>
    <MapTierChips v-if="tier" :tier="tier" />
    <span v-if="locked" class="tipLocked">
      <svg
        class="tipLockIcon"
        width="13"
        height="13"
        viewBox="0 0 24 24"
        stroke-width="2.2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <rect x="5" y="10.5" width="14" height="10" rx="2" />
        <path d="M8.5 10.5V7.5a3.5 3.5 0 0 1 7 0v3" />
      </svg>
      <span class="tipLockedText">Locked</span>
    </span>
  </div>
</template>

<script>
import MapFlag from "./map-flag.vue";
import MapTierChips from "./map-tier-chips.vue";

export default {
  components: { MapFlag, MapTierChips },
  props: {
    title: String,
    countryCode: String,
    tier: String, // "Free" | "Premium" | "Mixed" | null
    locked: Boolean,
  },
};
</script>

<style scoped lang="scss">
.hoverTip {
  // light theme; the dark values are below
  --tip-border: #d4d4d8;
  --tip-shadow: 0 1px 2px rgba(0, 0, 0, 0.06), 0 2px 8px rgba(0, 0, 0, 0.08);

  position: absolute;
  height: 28px;
  box-sizing: border-box;
  padding: 0 5px 0 6px;
  border: 1px solid var(--tip-border);
  border-radius: 8px;
  background: var(--surface-color);
  box-shadow: var(--tip-shadow);
  display: flex;
  align-items: center;
  gap: 7px;
  white-space: nowrap;
  pointer-events: none;
}
@media (prefers-color-scheme: dark) {
  .hoverTip {
    --tip-border: #34343a;
    --tip-shadow: none;
  }
}
.tipName {
  display: block;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
  font-weight: 600;
  line-height: 16px;
  color: var(--text-color);
}
// same lock and "Locked" as a locked row of the server list (servers-ping.vue)
.tipLocked {
  flex: none;
  display: flex;
  align-items: center;
  gap: 4px;
}
.tipLockIcon {
  display: block;
  flex: none;
  fill: none;
  stroke: var(--text-muted);
}
.tipLockedText {
  font-size: 11px;
  font-weight: 500;
  line-height: 16px;
  color: var(--text-muted);
}
</style>
