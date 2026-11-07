<template>
  <span
    class="srvChips"
    :class="{ mixed: tier === 'Mixed', fit: fit, shrinkWord: shrinkWord && isPremium && !isFree }"
  >
    <span v-if="cc" class="srvChip ccChip" :class="{ dim: dim }">{{ cc }}</span>
    <!-- "fit" mode: the room left after the country code (a size container) -->
    <span class="tierBox">
      <span v-if="isFree" class="srvChip freeChip">Free</span>
      <span
        v-if="isPremium"
        class="srvChip premiumChip"
        :title="tier === 'Mixed' ? 'This location also has Premium hosts' : shrinkWord ? 'Premium' : null"
      >
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
      <!-- optional extras: each one is shown whole or not at all -->
      <span v-if="fit && (ipv6 || extra)" class="extraBox">
        <span v-if="ipv6" class="srvChip ccChip" :class="{ dim: dim }"
          >IPv6</span
        >
        <span v-if="extra" class="extraText">{{ extra }}</span>
      </span>
    </span>
  </span>
</template>

<script>
// Country-code chip and the Free / Premium word chips (Mixed = both).
export default {
  props: {
    countryCode: String,
    // "Free" | "Premium" | "Mixed" | null (no tier chip)
    tier: String,
    // the chips fill the rest of their line (location rows): the crown of a
    // Mixed row gives way when the line is narrow, and the extras below are
    // shown only when they fit (never cut off)
    fit: Boolean,
    // "fit" mode only: the IPv6 chip and a short text (the ISP)
    ipv6: Boolean,
    extra: String,
    // locked rows: the country-code chip text is fainter
    dim: Boolean,
    // host rows: a Premium chip takes the room the host name leaves; when that is
    // too little the word gives way to the crown (still read out, "Premium" on hover),
    // so the name is not cut off
    shrinkWord: Boolean,
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
  },
};
</script>

<style scoped lang="scss">
// R4F chips, 1 px tighter (padding 4, gap 3): with the wider app font a Mixed
// row (BD + Free + Premium) then still fits beside a 3-digit latency
.srvChips {
  flex: none;
  height: 16px;
  display: flex;
  align-items: center;
  gap: 3px;
}
// without "fit" the box adds nothing to the layout
.tierBox {
  display: contents;
}

.srvChips.fit {
  flex: 1 1 0;
  min-width: 0;
}
.srvChips.fit .tierBox {
  flex: 1 1 0;
  min-width: 0;
  height: 16px;
  display: flex;
  align-items: center;
  gap: 3px;
  container-type: inline-size;
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

// host rows ("shrinkWord"): the chip box is the room after the name (a size
// container, never less than the 18 px crown-only chip)
.srvChips.shrinkWord {
  flex: 1 1 0;
  min-width: 18px;
  container-type: inline-size;
}
// the whole Premium chip is 65 px in the app font
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

// Extras (IPv6 chip, ISP): a 0-wide first item keeps the first line, so an
// extra that does not fit wraps to the second line, which is hidden
.extraBox {
  flex: 1 1 0;
  min-width: 0;
  height: 16px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  align-content: flex-start;
  overflow: hidden;
}
.extraBox::before {
  content: "";
  flex: none;
  width: 0;
  height: 16px;
}
.extraBox > * + * {
  margin-left: 4px;
}
.extraText {
  flex: none;
  font-size: 11px;
  line-height: 16px;
  color: var(--text-faint);
  white-space: nowrap;
}

// Mixed row in a narrow line: the crown goes, the words stay. The container is
// the room after the country code, so the rule holds for any code ("BD", "MM").
// Free (31) + gap (3) + Premium with the crown (65) = 99 px in the app font.
@container (max-width: 99.5px) {
  .srvChips.mixed .crown {
    display: none;
  }
  .srvChips.mixed .premiumChip {
    padding-left: 4px;
  }
}
</style>
