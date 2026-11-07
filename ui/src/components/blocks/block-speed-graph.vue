<template>
  <div class="graphCard">
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
      <span class="legendItem"><span class="swatch swatchDown" />Download {{ down.value }} {{ down.unit }}</span>
      <span class="legendItem"><span class="swatch swatchUp" />Upload {{ up.value }} {{ up.unit }}</span>
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
      return `Speed over the last minute. Download ${this.down.value} ${this.down.unit}, upload ${this.up.value} ${this.up.unit}`;
    },
  },
};
</script>

<style scoped lang="scss">
.graphCard {
  box-sizing: border-box;
  width: 100%;
  padding: 14px 18px 12px;
  border-radius: 14px;
  background: var(--surface-color);
  border: 1px solid var(--surface-border);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.graphHead {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.graphTitle {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--text-faint);
}
.graphSession {
  font-size: 11px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
.graph {
  display: block;
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
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
.legendItem {
  display: flex;
  align-items: center;
  gap: 6px;
}
.swatch {
  width: 10px;
  height: 3px;
  border-radius: 2px;
}
.swatchDown {
  background: var(--accent-color);
}
.swatchUp {
  background: var(--text-faint);
}
</style>
