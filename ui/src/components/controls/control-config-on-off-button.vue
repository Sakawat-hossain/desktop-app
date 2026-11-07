<template>
  <!-- A 48 px card row: [icon] title + description, then a switch -->
  <div class="row">
    <span
      v-if="$slots.icon"
      class="rowIcon"
      v-bind:class="{ rowIconOn: isOn }"
      aria-hidden="true"
    >
      <slot name="icon" />
    </span>

    <!-- the title opens the related settings when a handler is given -->
    <button
      v-if="onTextClick"
      type="button"
      class="rowText rowTextBtn"
      v-on:click="onTextClick"
      :title="textClickTooltip"
    >
      <span class="rowTitle">{{ text }}</span>
      <span v-if="description" :id="descriptionId" class="rowDesc">
        {{ description }}
      </span>
    </button>
    <div v-else class="rowText">
      <span class="rowTitle">{{ text }}</span>
      <span v-if="description" :id="descriptionId" class="rowDesc">
        {{ description }}
      </span>
    </div>

    <label
      class="switch"
      v-bind:class="{ on: isOn, busy: isProgress, customColor: isCustomColor }"
      :style="switcherStyle"
      :title="isChecked ? 'Disable ' + text : 'Enable ' + text"
    >
      <input
        ref="input"
        type="checkbox"
        role="switch"
        :checked="isOn"
        :aria-label="text"
        :aria-describedby="description ? descriptionId : null"
        :aria-busy="isProgress ? 'true' : null"
        v-on:click="DoSwitch($event)"
      />
      <span class="track" :style="trackStyle" aria-hidden="true" />
      <span class="knob" aria-hidden="true" />
    </label>
  </div>
</template>

<script>
let nextId = 0;

export default {
  props: [
    "onChecked",
    "isChecked",
    "isProgress",
    "text",
    "description",
    "checkedColor",
    "switcherOpacity",
    "onTextClick",
    "textClickTooltip",
  ],
  data: function () {
    nextId += 1;
    return {
      descriptionId: `onOffRowDesc${nextId}`,
    };
  },
  computed: {
    // same rule as the old switch: while in progress the switch shows "off" with a spinner
    isOn: function () {
      if (this.isProgress) return false;
      return this.isChecked === true;
    },
    isCustomColor: function () {
      return this.checkedColor != null && this.isOn === true;
    },
    trackStyle: function () {
      if (!this.isCustomColor) return "";
      return `background: ${this.checkedColor}`;
    },
    switcherStyle: function () {
      if (!this.switcherOpacity) return "";
      return `opacity: ${this.switcherOpacity}`;
    },
  },
  methods: {
    DoSwitch(e) {
      // Turning on: keep the box unchecked until the new state arrives from the daemon.
      // Turning off: the switch goes off at once (the progress state shows it as off too).
      if (!this.isOn) e.preventDefault();
      if (this.onChecked) {
        if (this.isProgress) this.onChecked(false, e);
        else this.onChecked(!this.isOn, e);
      }
      // After the click has finished, make the checkbox match the state again
      // (for example when the handler only opened a settings view).
      setTimeout(() => {
        const input = this.$refs.input;
        if (input && input.checked !== this.isOn) input.checked = this.isOn;
      }, 0);
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

.row {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 48px;
  box-sizing: border-box;
  padding: 6px 14px;
  text-align: left;
}

.rowIcon {
  width: 18px;
  height: 18px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: color 0.2s;
}
.rowIconOn {
  color: var(--link-color);
}

.rowText {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1px;
}
button.rowTextBtn {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}
button.rowTextBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
  border-radius: 4px;
}
.rowTitle {
  font-size: 13.5px;
  font-weight: 500;
  line-height: 18px;
}
.rowDesc {
  font-size: 11.5px;
  line-height: 15px;
  color: var(--text-faint);
  overflow-wrap: anywhere;
}

// ---------- switch (40 x 24, 18 px knob) ----------
.switch {
  position: relative;
  width: 40px;
  height: 24px;
  flex: none;
  margin: 0;
  cursor: pointer;
}
.switch input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  opacity: 0;
  cursor: pointer;
  z-index: 1;
}
.track {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  background: var(--switch-off-color);
  pointer-events: none;
  transition: background-color 0.2s, opacity 0.2s;
}
.knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  box-sizing: border-box;
  border-radius: 50%;
  background: var(--background-color);
  pointer-events: none;
  transition: left 0.2s, background-color 0.2s;
}
.switch.on .track {
  background: var(--accent-color);
}
.switch.on .knob {
  left: 19px;
  background: var(--accent-text-color);
}
// a custom (dark) checked colour needs a light knob
.switch.on.customColor .knob {
  background: #ffffff;
}
.switch.busy .knob {
  left: 11px;
  background: transparent;
  border: 2px solid var(--text-faint);
  border-top-color: var(--accent-color);
  animation: switchSpin 0.9s linear infinite;
}
@keyframes switchSpin {
  to {
    transform: rotate(360deg);
  }
}
.switch:hover .track {
  opacity: 0.85;
}
.switch input:focus-visible ~ .track {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}
</style>
