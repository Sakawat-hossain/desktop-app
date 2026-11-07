<template>
  <div class="speedGraph">
    <div class="graphHead">
      <span class="graphTitle">SPEED · LAST 60 S</span>
      <span class="graphSession">Session {{ sessionText }}</span>
    </div>
    <svg
      class="graph"
      width="100%"
      height="56"
      viewBox="0 0 216 56"
      preserveAspectRatio="none"
      role="img"
      :aria-label="ariaText"
    >
      <path d="M0 55.5H216" class="baseLine" vector-effect="non-scaling-stroke" />
      <polyline :points="rxPoints" class="lineDown" vector-effect="non-scaling-stroke" />
      <polyline :points="txPoints" class="lineUp" vector-effect="non-scaling-stroke" />
    </svg>
    <div class="legend">
      <span class="legendItem">
        <span class="swatch swatchDown" aria-hidden="true"></span>
        Download
        <span class="legendValue">{{ down.value }} {{ down.unit }}</span>
      </span>
      <span class="legendItem">
        <span class="swatch swatchUp" aria-hidden="true"></span>
        Upload
        <span class="legendValue">{{ up.value }} {{ up.unit }}</span>
      </span>
    </div>
  </div>
</template>

<script>
import { formatSpeed, formatBytes, sparklinePoints } from "@/helpers/traffic";

export default {
  computed: {
    traffic() {
      return this.$store.state.vpnState.traffic;
    },
    maxValue() {
      let max = 1;
      for (const s of this.traffic.history) max = Math.max(max, s.rx, s.tx);
      return max * 1.1;
    },
    rxPoints() {
      return sparklinePoints(this.traffic.history, "rx", 216, 56, this.maxValue);
    },
    txPoints() {
      return sparklinePoints(this.traffic.history, "tx", 216, 56, this.maxValue);
    },
    down() {
      return formatSpeed(this.traffic.rxBps);
    },
    up() {
      return formatSpeed(this.traffic.txBps);
    },
    sessionText() {
      return formatBytes(this.traffic.sessionRx + this.traffic.sessionTx);
    },
    ariaText() {
      return `Speed over the last minute: download ${this.down.value} ${this.down.unit}, upload ${this.up.value} ${this.up.unit}`;
    },
  },
};
</script>

<style scoped lang="scss">
// The speed section of the map's "Connection details" card (the card itself is drawn by Component-Map).
// NOTE: every element gets an explicit colour because App.vue sets "html * { color }" for all elements.
.speedGraph {
  display: flex;
  flex-direction: column;
}
.graphHead {
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.graphTitle {
  font-size: 11px;
  font-weight: 600;
  line-height: 16px;
  letter-spacing: 0.06em;
  white-space: nowrap;
  color: var(--text-faint);
}
.graphSession {
  font-size: 11px;
  line-height: 16px;
  white-space: nowrap;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
.graph {
  display: block;
  margin-top: 10px;
}
.baseLine {
  stroke: var(--surface-border);
  stroke-width: 1;
  fill: none;
}
.lineDown,
.lineUp {
  fill: none;
  stroke-linejoin: round;
  stroke-linecap: round;
}
.lineDown {
  stroke: var(--accent-color);
  stroke-width: 2;
}
.lineUp {
  stroke: var(--text-faint);
  stroke-width: 1.6;
}
.legend {
  height: 16px;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 18px;
  white-space: nowrap;
}
.legendItem {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  line-height: 16px;
  color: var(--text-muted);
}
.legendValue {
  font-weight: 600;
  color: var(--text-color);
  font-variant-numeric: tabular-nums;
}
.swatch {
  width: 10px;
  height: 3px;
  flex: none;
  border-radius: 2px;
}
.swatchDown {
  background: var(--accent-color);
}
.swatchUp {
  background: var(--text-faint);
}
</style>
