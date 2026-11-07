<template>
  <!-- Inline window buttons: placed inside a view's own title bar
       (main window, views/Component-Main.vue). 28x28 icon buttons. -->
  <div v-if="inline" class="winBtnsInline" v-show="!isWindowHasFrame">
    <button
      type="button"
      title="Minimize"
      aria-label="Minimize"
      v-if="minimizable"
      class="winBtnInline"
      v-on:click="onMinimize()"
    >
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 12h16" /></svg>
    </button>

    <button
      type="button"
      title="Close"
      aria-label="Close"
      v-if="closable"
      class="winBtnInline winBtnInlineClose"
      v-on:click="onClose()"
    >
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19" /></svg>
    </button>
  </div>

  <!-- 24 px title strip at the top of the window (settings, update and other windows) -->
  <div v-else class="titleBar" v-show="!isWindowHasFrame">
    <button
      title="Minimize"
      style="margin-top: 1px"
      v-if="minimizable"
      class="noBordersBtn winBtns winBtnMinimize"
      v-on:click="onMinimize()"
    >
      <svg width="11" height="1" viewBox="0 0 11 1">
        <path d="m11 0v1h-11v-1z" stroke-width=".26208" fill="#888888" />
      </svg>
    </button>

    <button
      title="Close"
      style="margin-top: 1px; margin-right: 1px"
      v-if="closable"
      class="noBordersBtn winBtns winBtnClose"
      v-on:click="onClose()"
    >
      <svg width="11" height="11" viewBox="0 0 12 12" color="red">
        <path
          d="m6.8496 6 5.1504 5.1504-0.84961 0.84961-5.1504-5.1504-5.1504 5.1504-0.84961-0.84961 5.1504-5.1504-5.1504-5.1504 0.84961-0.84961 5.1504 5.1504 5.1504-5.1504 0.84961 0.84961z"
          stroke-width=".3"
          fill="#888888"
        />
      </svg>
    </button>
  </div>
</template>

<script>
import { IsWindowHasFrame } from "@/platform/platform";
const sender = window.ipcSender;

export default {
  props: {
    // true: only the Minimize / Close buttons, laid out inline (no absolute 24 px strip)
    inline: {
      type: Boolean,
      default: false,
    },
  },
  data: function () {
    return {
      closable: true,
      maximizable: true,
      minimizable: true,
    };
  },
  mounted() {
    let t = this;
    setTimeout(() => {
      const props = sender.getCurrentWindowProperties();
      if (!props) return;
      if (props.closable !== undefined) t.closable = props.closable;
      if (props.maximizable !== undefined) t.maximizable = props.maximizable;
      if (props.minimizable !== undefined) t.minimizable = props.minimizable;
    }, 0);
  },
  computed: {
    isWindowHasFrame: function () {
      return IsWindowHasFrame();
    },
  },
  watch: {},
  methods: {
    onMinimize: function () {
      sender.minimizeCurrentWindow();
    },
    onClose: function () {
      sender.closeCurrentWindow();
    },
  },
};
</script>

<style lang="scss">
@import "@/components/scss/constants";

.titleBar {
  // Panel can be dragable by mouse
  // (we need this because using no title style for main window (for  macOS))
  -webkit-app-region: drag;

  height: 24px;
  width: 100%;

  position: absolute;

  z-index: 100;

  display: flex;
  justify-content: flex-end;
}

.winBtns {
  z-index: 101;
  -webkit-app-region: no-drag;
  cursor: pointer;
  width: 46px;
}

.winBtnMinimize:hover {
  background: #e5e5e5;
  @media (prefers-color-scheme: dark) {
    background: #404040;
  }
}

.winBtnClose:hover {
  background: #e81123;
}

// ===== Inline window buttons (title bar of the main window) =====
.winBtnsInline {
  flex: none;
  display: flex;
  align-items: center;
}

.winBtnInline {
  -webkit-app-region: no-drag;
  flex: none;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
// the global 'html *' color rule would otherwise give the icon the text colour
.winBtnInline svg,
.winBtnInline svg * {
  color: inherit;
}
.winBtnInline:hover {
  background: var(--neutral-tint);
  color: var(--text-color);
}
.winBtnInline.winBtnInlineClose:hover {
  background: #c42b1c;
  color: #ffffff;
}
.winBtnInline:focus {
  outline: none;
}
.winBtnInline:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
</style>
