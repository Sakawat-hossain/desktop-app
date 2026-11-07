<template>
  <!-- right column of a row: signal bars + latency, or a lock for a locked row -->
  <span class="srvPing" :class="[qualityClass, { locked: locked }]" :title="tooltip">
    <template v-if="locked">
      <svg
        class="lockIcon"
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
      <span class="lockedText">Locked</span>
    </template>
    <template v-else-if="quality">
      <span class="bars" role="img" :aria-label="qualityLabel">
        <span class="bar bar1 on"></span>
        <span class="bar bar2" :class="{ on: quality !== 'bad' }"></span>
        <span class="bar bar3" :class="{ on: quality === 'good' }"></span>
      </span>
      <span class="msText">{{ text }}</span>
    </template>
  </span>
</template>

<script>
import { PingQualityName, PingText } from "@/components/servers/servers-helpers";

export default {
  props: {
    ms: Number,
    locked: Boolean,
    // tooltip (for example "Best ping among the Free hosts you can use")
    hint: String,
  },
  computed: {
    quality() {
      return PingQualityName(this.ms);
    },
    qualityClass() {
      return this.quality ? "q-" + this.quality : "";
    },
    qualityLabel() {
      switch (this.quality) {
        case "good":
          return "Good connection";
        case "moderate":
          return "Moderate connection";
        case "bad":
          return "Poor connection";
      }
      return "";
    },
    text() {
      return PingText(this.ms);
    },
    tooltip() {
      if (this.locked) return "Premium: upgrade to connect";
      if (!this.quality) return null;
      return this.hint || null;
    },
  },
};
</script>

<style scoped lang="scss">
// Sized by its content and right-aligned by the row, so the bars and the
// latency sit exactly where R4F's 62 px right-aligned column puts them, and the
// text column keeps the room a shorter latency leaves
.srvPing {
  min-width: 0;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}
.srvPing.locked {
  gap: 4px;
}

.bars {
  height: 10px;
  flex: none;
  display: flex;
  align-items: flex-end;
  gap: 2px;
}
.bar {
  width: 3px;
  display: block;
  border-radius: 1px;
  background: var(--srv-bar-off, #d4d4d8);
}
.bar1 {
  height: 4px;
}
.bar2 {
  height: 7px;
}
.bar3 {
  height: 10px;
}

.msText {
  font-size: 12px;
  font-weight: 600;
  line-height: 16px;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.q-good .bar.on {
  background: var(--good-text);
}
.q-good .msText {
  color: var(--good-text);
}
.q-moderate .bar.on {
  background: var(--srv-moderate, #b45309);
}
.q-moderate .msText {
  color: var(--srv-moderate, #b45309);
}
.q-bad .bar.on {
  background: var(--danger-text);
}
.q-bad .msText {
  color: var(--danger-text);
}

.lockIcon {
  display: block;
  flex: none;
  fill: none;
  stroke: var(--text-muted);
}
.lockedText {
  font-size: 11px;
  font-weight: 500;
  line-height: 16px;
  white-space: nowrap;
  color: var(--text-muted);
}
</style>
