<template>
  <span v-if="tier" class="tierChips" :title="title">
    <!-- Free / Premium mark of a server: "Free", "Premium", or both for a location with both kinds of hosts -->
    <span v-if="tier !== 'Premium'" class="tierChip tierFree">Free</span>
    <span
      v-if="tier !== 'Free'"
      class="tierChip tierPremium"
      :class="{ crownOnly: tier === 'Mixed' }"
    >
      <svg
        class="crown"
        width="10"
        height="10"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path d="M2.8 7.6 7.7 11.6 12 4.6 16.3 11.6 21.2 7.6 19.3 17.2H4.7z" />
        <rect x="4.7" y="18.8" width="14.6" height="2.6" rx="1.3" />
      </svg>
      <span v-if="tier !== 'Mixed'" class="chipText">Premium</span>
      <span v-else class="srOnly">Premium</span>
    </span>
  </span>
</template>

<script>
export default {
  props: {
    // "Free" | "Premium" | "Mixed" (Free and Premium hosts) | null
    tier: String,
  },
  computed: {
    title() {
      if (this.tier === "Premium") return "Premium server";
      if (this.tier === "Mixed") return "Free and Premium servers";
      if (this.tier === "Free") return "Free server";
      return null;
    },
  },
};
</script>

<style scoped lang="scss">
.tierChips {
  // light theme; the dark value is below
  --map-free-border: #bfe3cb;

  flex: none;
  display: flex;
  align-items: center;
  gap: 3px;
}
@media (prefers-color-scheme: dark) {
  .tierChips {
    --map-free-border: #1f3d2a;
  }
}
.tierChip {
  position: relative;
  flex: none;
  box-sizing: border-box;
  height: 16px;
  padding: 0 5px;
  border: 1px solid;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
  line-height: 14px;
  letter-spacing: 0.02em;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 2px;
}
.tierFree {
  border-color: var(--map-free-border);
  background: var(--good-background);
  color: var(--good-text);
}
.tierPremium {
  padding-left: 3px;
  border-color: var(--accent-ring);
  background: var(--accent-tint);
  color: var(--link-color);
}
// App.vue gives every element the text colour: the chip text follows the chip
.chipText {
  color: inherit;
}
// a location with Free and Premium hosts: "Free" + a crown-only chip
.tierPremium.crownOnly {
  width: 16px;
  padding: 0;
  justify-content: center;
}
.crown {
  display: block;
  flex: none;
  fill: var(--link-color);
}
.srOnly {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
</style>
