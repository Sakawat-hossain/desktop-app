<template>
  <div class="upSlot" :style="{ paddingLeft: indent + 'px' }">
    <!-- Shown inside a server card, under the locked row a Free account
         clicked. The card's tree lines that go on past it are drawn on its left. -->
    <span
      v-for="x of lines"
      :key="x"
      class="upLine"
      :style="{ left: x + 'px' }"
      aria-hidden="true"
    ></span>
    <div
      :id="cardId"
      class="upgradeCard"
      role="group"
      :aria-labelledby="cardId + '-t'"
    >
      <div class="upTop">
        <span class="upTile" aria-hidden="true">
          <svg class="crown" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M2.8 7.6 7.7 11.6 12 4.6 16.3 11.6 21.2 7.6 19.3 17.2H4.7z" />
            <rect x="4.7" y="18.8" width="14.6" height="2.6" rx="1.3" />
          </svg>
        </span>
        <span class="upTexts">
          <span :id="cardId + '-t'" class="upTitle">{{ name }} is Premium</span>
          <span class="upText"
            >Upgrade on your account page to connect. Free locations still
            work.</span
          >
        </span>
      </div>
      <div class="upActions">
        <button
          type="button"
          class="upBtn upPrimary"
          title="Opens your account page"
          v-on:click="onUpgrade"
        >
          Upgrade
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke-width="2.2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M5 12h14M13 6l6 6-6 6" />
          </svg>
        </button>
        <button type="button" class="upBtn upSecondary" v-on:click="$emit('dismiss')">
          Not now
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import config from "@/config";

export default {
  emits: ["dismiss"],
  props: {
    // id for aria-controls on the row that opened the card
    cardId: { type: String, required: true },
    // "<Name> is Premium"
    name: String,
    // left edge of the card inside the server card (px)
    indent: { type: Number, default: 9 },
    // x (px) of the server card's tree lines that pass the card on its left
    lines: { type: Array, default: () => [] },
  },
  methods: {
    onUpgrade() {
      const sender = window.ipcSender;
      if (sender && sender.shellOpenExternal)
        sender.shellOpenExternal(config.URLPricing);
    },
  },
};
</script>

<style scoped lang="scss">
.upSlot {
  position: relative;
  box-sizing: border-box;
  padding: 2px 8px 8px 9px;
}
// a tree line of the server card (same as the rows' 1 px lines at x + 0.5)
.upLine {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  display: block;
  background: var(--srv-tree-line, #d4d4d8);
}

.upgradeCard {
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid var(--accent-ring);
  border-radius: 10px;
  background: var(--background-color);
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
}

.upTop {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.upTile {
  width: 32px;
  height: 32px;
  flex: none;
  box-sizing: border-box;
  border: 1px solid var(--accent-ring);
  border-radius: 9px;
  background: var(--accent-tint);
  display: flex;
  align-items: center;
  justify-content: center;
}
.crown {
  display: block;
  flex: none;
  fill: var(--link-color);
}

.upTexts {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.upTitle {
  font-size: 13.5px;
  font-weight: 600;
  line-height: 18px;
  overflow-wrap: anywhere;
}
.upText {
  font-size: 11.5px;
  line-height: 16px;
  color: var(--text-muted);
}

.upActions {
  height: 32px;
  flex: none;
  display: flex;
  align-items: center;
  gap: 8px;
}
.upBtn {
  height: 32px;
  box-sizing: border-box;
  margin: 0;
  scroll-margin: 8px; // focus scrolls the button into view with its ring
  border-radius: 8px;
  font-size: 12.5px;
  line-height: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  cursor: pointer;
}
.upBtn:focus {
  outline: none;
}
.upBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}
.upPrimary {
  padding: 0 12px 0 14px;
  gap: 6px;
  border: 0;
  background: var(--accent-color);
  color: var(--accent-text-color);
  font-weight: 600;
}
.upPrimary svg {
  display: block;
  flex: none;
  stroke: var(--accent-text-color);
}
.upPrimary:hover {
  background: var(--accent-color-hover);
}
.upSecondary {
  padding: 0 12px;
  border: 1px solid var(--control-border);
  background: transparent;
  color: var(--text-soft);
  font-weight: 500;
}
.upSecondary:hover {
  background: var(--neutral-tint);
}
</style>
