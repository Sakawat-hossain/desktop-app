<template>
  <div>
    <div class="switchButton">
      <div align="left" tabindex="0">
        <button
          v-if="onTextClick"
          class="noBordersTextBtnEx"
          v-on:click="onTextClick"
          :title="textClickTooltip"
        >
          <div class="large_text">{{ text }}</div>
        </button>
        <div v-else class="large_text">{{ text }}</div>

        <div style="height: 2px" />
        <div class="small_text">
          {{ description }}
        </div>
      </div>

      <div>
        <SwitchProgress
          :title="(isChecked)?'Disable '+text:'Enable '+text"
          :style="switcherStyle"
          :onChecked="onChecked"
          :isChecked="isChecked"
          :isProgress="isProgress"
          :checkedColor="checkedColor"
        />
      </div>
    </div>
  </div>
</template>

<script>
import SwitchProgress from "@/components/controls/control-switch-small.vue";

export default {
  components: {
    SwitchProgress,
  },
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
  computed: {
    switcherStyle: function () {
      if (!this.switcherOpacity) return "";
      return `opacity: ${this.switcherOpacity}`;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/components/scss/constants";

.large_text {
  font-size: 13.5px;
  line-height: 17px;
  font-weight: 500;
}

.small_text {
  font-size: 11.5px;
  line-height: 14px;
  color: var(--text-faint);
}

.switchButton {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  min-height: 54px;
  box-sizing: border-box;
  padding: 0 14px;
  text-align: left;
}

button.noBordersTextBtnEx {
  @extend .noBordersTextBtn;

  display: flex;
  justify-content: space-between;
  align-items: center;

  width: 100%;
}
</style>
