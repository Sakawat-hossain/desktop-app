<template>
  <span
    class="srvChips"
    :class="{ mixed: tier === 'Mixed', shrinkWord: shrinkWord && isPremium }"
  >
    <span v-if="cc" class="srvChip ccChip" :class="{ dim: dim }">{{ cc }}</span>
    <span v-if="isFree" class="srvChip freeChip">Free</span>
    <span v-if="isPremium" class="srvChip premiumChip" :title="premiumTooltip">
      <svg
        class="crown"
        width="10"
        height="10"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path d="M2.8 7.6 7.7 11.6 12 4.6 16.3 11.6 21.2 7.6 19.3 17.2H4.7z" />
        <rect x="4.7" y="18.8" width="14.6" height="2.6" rx="1.3" /></svg
      ><span class="chipWord">Premium</span></span
    >
  </span>
</template>

<script>
// Country-code chip and the Free / Premium word chips (Mixed = both).
export default {
  props: {
    countryCode: String,
    // "Free" | "Premium" | "Mixed" | null (no tier chip)
    tier: String,
    // locked rows: the country-code chip text is fainter
    dim: Boolean,
    // the chips take the room the row leaves them: when that is too little the
    // Premium word gives way to the crown (still read out, "Premium" on hover),
    // so nothing next to them is cut off. A Mixed pair then reads "Free" + crown.
    shrinkWord: Boolean,
    // tooltip of the Premium chip (for example "Japan also has Premium servers")
    premiumTitle: String,
  },
  computed: {
    cc() {
      if (!this.countryCode || typeof this.countryCode !== "string") return "";
      return this.countryCode.trim().toUpperCase();
    },
    isFree() {
      return this.tier === "Free" || this.tier === "Mixed";
    },
    isPremium() {
      return this.tier === "Premium" || this.tier === "Mixed";
    },
    premiumTooltip() {
      if (this.premiumTitle) return this.premiumTitle;
      if (this.tier === "Mixed") return "This location also has Premium hosts";
      return this.shrinkWord ? "Premium" : null;
    },
  },
};
</script>

<style scoped lang="scss">
// R4F chips, 1 px tighter (padding 4, gap 3): with the wider app font a Mixed
// pair still fits beside the name and a 3-digit latency
.srvChips {
  flex: none;
  height: 16px;
  display: flex;
  align-items: center;
  gap: 3px;
}

.srvChip {
  flex: none;
  height: 16px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  white-space: nowrap;
  font-weight: 700;
}

.ccChip {
  padding: 0 4px;
  border-radius: 4px;
  background: var(--neutral-tint);
  color: var(--text-soft);
  font-size: 9.5px;
  line-height: 16px;
  letter-spacing: 0.04em;
}
.ccChip.dim {
  color: var(--text-faint);
}

.freeChip,
.premiumChip {
  border: 1px solid;
  border-radius: 5px;
  font-size: 10px;
  line-height: 14px;
  letter-spacing: 0.02em;
}
.freeChip {
  padding: 0 4px;
  border-color: var(--srv-free-border, #bfe3cb);
  background: var(--good-background);
  color: var(--good-text);
}
.premiumChip {
  padding: 0 4px 0 3px;
  gap: 2px;
  border-color: var(--accent-ring);
  background: var(--accent-tint);
  color: var(--link-color);
}

.crown {
  display: block;
  flex: none;
  fill: var(--link-color);
}
// the global 'html * { color }' rule: the word keeps the chip's colour
.chipWord {
  color: inherit;
}

// "shrinkWord": the box is a size container that grows to the whole chips and
// shrinks to the crown form; the sizes are those of the app font:
// Premium 65 px (crown only 18), Mixed Free 31 + 3 + Premium 65 = 99 (Free +
// crown 52). Below its min-width a row may leave the chips out altogether.
.srvChips.shrinkWord {
  flex: 1 1 18px;
  min-width: 18px;
  max-width: 66px;
  container-type: inline-size;
}
.srvChips.shrinkWord.mixed {
  flex-basis: 52px;
  min-width: 52px;
  max-width: 100px;
}
@container (max-width: 65.5px) {
  .srvChips.shrinkWord .premiumChip {
    padding: 0 3px;
  }
  .srvChips.shrinkWord .chipWord {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }
}
@container (max-width: 99.5px) {
  .srvChips.shrinkWord.mixed .premiumChip {
    padding: 0 3px;
  }
  .srvChips.shrinkWord.mixed .chipWord {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }
}
</style>
