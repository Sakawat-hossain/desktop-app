<template>
  <!-- Fastest server settings: one location per row, the whole row is the switch -->
  <button
    type="button"
    class="fastRow"
    :class="{ off: !isOn && !isLocked, locked: isLocked }"
    role="switch"
    :aria-checked="isOn && !isLocked ? 'true' : 'false'"
    :aria-disabled="isLocked ? 'true' : null"
    :aria-label="ariaLabel"
    :title="tooltip"
    v-on:click="onClick"
  >
    <ServerFlag :countryCode="server.country_code" :dim="isLocked" />
    <span class="fastTexts">
      <span class="fastTitle">{{ title }}</span>
      <ServerChips :countryCode="server.country_code" :tier="tier" :dim="isLocked" />
    </span>

    <span v-if="isLocked" class="lockedMark">
      <svg
        width="13"
        height="13"
        viewBox="0 0 24 24"
        fill="none"
        stroke-width="2.2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <rect x="5" y="10.5" width="14" height="10" rx="2" />
        <path d="M8.5 10.5V7.5a3.5 3.5 0 0 1 7 0v3" />
      </svg>
      <span class="lockedText">Locked</span>
    </span>
    <span v-else class="switchVis" :class="{ on: isOn }" aria-hidden="true">
      <span class="knob"></span>
    </span>
  </button>
</template>

<script>
import ServerFlag from "@/components/servers/servers-flag.vue";
import ServerChips from "@/components/servers/servers-chips.vue";
import { GetSreverISPs } from "@/helpers/helpers_servers";
import {
  EntryTier,
  IsEntryLocked,
  IsPremiumAccountFor,
} from "@/components/servers/servers-helpers";

export default {
  components: { ServerFlag, ServerChips },
  emits: ["toggle"],
  props: {
    server: { type: Object, required: true },
    // the location may be chosen as the fastest server
    isOn: Boolean,
  },
  computed: {
    isPremiumAccount() {
      return IsPremiumAccountFor(this.$store.getters);
    },
    title() {
      return this.server.city || this.server.country || "";
    },
    tier() {
      return EntryTier(this.server);
    },
    // a Free account never gets a Premium-only location as the fastest server
    isLocked() {
      return IsEntryLocked(this.server, this.isPremiumAccount);
    },
    ariaLabel() {
      if (this.isLocked) return `${this.title}, Premium, locked`;
      return `Use ${this.title} for Fastest server`;
    },
    // the ISP of the location when the "show ISP" setting is on (as the old list did)
    ispText() {
      if (this.$store.state.settings.showISPInfo !== true) return "";
      const isps = GetSreverISPs(this.server);
      return isps.length === 1 ? isps[0] : "";
    },
    tooltip() {
      let t = "";
      if (this.isLocked) t = "Premium location: Fastest never picks it on a Free plan";
      else
        t = this.isOn
          ? "Fastest server may pick this location"
          : "Fastest server skips this location";
      return this.ispText ? t + "\nISP: " + this.ispText : t;
    },
  },
  methods: {
    onClick(event) {
      if (this.isLocked) return;
      this.$emit("toggle", this.server, event);
    },
  },
};
</script>

<style scoped lang="scss">
svg,
svg * {
  color: inherit;
}

.fastRow {
  width: 100%;
  height: 44px;
  box-sizing: border-box;
  margin: 0;
  padding: 0 10px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 10px;
  text-align: left;
  font-family: inherit;
  cursor: pointer;
  transition: background-color 0.15s;
}
.fastRow:hover {
  background: var(--srv-row-hover, var(--surface-color));
}
.fastRow:focus {
  outline: none;
}
.fastRow:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
.fastRow.locked {
  cursor: default;
}

.fastTexts {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.fastTitle {
  display: block;
  font-size: 13.5px;
  font-weight: 600;
  line-height: 18px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.fastRow.off .fastTitle {
  color: var(--text-muted);
}
.fastRow.locked .fastTitle {
  color: var(--text-muted);
}

// same switch as the kill switch card (40 x 24, 18 px knob)
.switchVis {
  position: relative;
  width: 40px;
  height: 24px;
  flex: none;
  display: block;
  border-radius: 12px;
  background: var(--switch-off-color);
  transition: background-color 0.2s;
}
.knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  display: block;
  border-radius: 50%;
  background: var(--background-color);
  transition: left 0.2s, background-color 0.2s;
}
.switchVis.on {
  background: var(--accent-color);
}
.switchVis.on .knob {
  left: 19px;
  background: var(--accent-text-color);
}

.lockedMark {
  flex: none;
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}
.lockedMark svg {
  display: block;
  flex: none;
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
