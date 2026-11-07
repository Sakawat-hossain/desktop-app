<template>
  <div class="speedCard" role="group" aria-label="Tunnel speed">
    <div class="half">
      <span class="icon iconDown" aria-hidden="true">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v15M6 13l6 6 6-6" /></svg>
      </span>
      <span class="texts">
        <span class="label">Download</span>
        <span class="value">{{ down.value }} <span class="unit">{{ down.unit }}</span></span>
      </span>
    </div>
    <div class="half">
      <span class="icon iconUp" aria-hidden="true">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V5M6 11l6-6 6 6" /></svg>
      </span>
      <span class="texts">
        <span class="label">Upload</span>
        <span class="value">{{ up.value }} <span class="unit">{{ up.unit }}</span></span>
      </span>
    </div>
  </div>
</template>

<script>
import { formatSpeed } from "@/helpers/traffic";

export default {
  computed: {
    down() {
      return formatSpeed(this.$store.state.vpnState.traffic.rxBps);
    },
    up() {
      return formatSpeed(this.$store.state.vpnState.traffic.txBps);
    },
  },
};
</script>

<style scoped lang="scss">
.speedCard {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--surface-border);
  border-radius: 14px;
  background: var(--surface-color);
}
.half {
  padding: 9px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.half + .half {
  border-left: 1px solid var(--surface-divider);
}
.icon {
  width: 28px;
  height: 28px;
  flex: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.iconDown {
  background: var(--accent-tint);
  color: var(--link-color);
}
.iconUp {
  background: var(--neutral-tint);
  color: var(--text-muted);
}
.texts {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
  text-align: left;
}
.label {
  font-size: 11px;
  line-height: 13px;
  color: var(--text-faint);
}
.value {
  font-size: 14px;
  line-height: 17px;
  font-weight: 600;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.unit {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
}
</style>
