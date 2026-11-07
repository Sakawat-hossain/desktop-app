<template>
  <div class="sortWrap" v-click-outside="onClickOutside">
    <button
      ref="sortBtn"
      type="button"
      class="sortBtn"
      :class="{ open: isOpen }"
      :aria-label="'Sort servers, current: ' + sortType"
      title="Sort by: City, Country, Latency, Proximity"
      aria-haspopup="menu"
      :aria-expanded="isOpen ? 'true' : 'false'"
      :aria-controls="isOpen ? menuId : null"
      v-on:click="toggle"
      v-on:keydown.down.prevent="openAndFocus(0)"
      v-on:keydown.up.prevent="openAndFocus(types.length - 1)"
      v-on:keydown.esc="onClickOutside"
    >
      <svg
        width="17"
        height="17"
        viewBox="0 0 24 24"
        fill="none"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M4 7h16M7 12h10M10 17h4" />
      </svg>
    </button>

    <transition name="srvMenu">
      <div
        v-if="isOpen"
        :id="menuId"
        class="sortMenu"
        role="menu"
        aria-label="Sort servers by"
        v-on:keydown="onMenuKeydown"
      >
        <div class="menuTitle" aria-hidden="true">Sort by</div>
        <button
          v-for="t of types"
          :key="t"
          type="button"
          role="menuitemradio"
          class="menuItem"
          :class="{ checked: t === sortType }"
          :aria-checked="t === sortType ? 'true' : 'false'"
          tabindex="-1"
          v-on:click="select(t)"
        >
          <span class="menuCheck" aria-hidden="true">
            <svg
              v-if="t === sortType"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke-width="2.4"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M5 12.5l4.5 4.5L19 7.5" />
            </svg>
          </span>
          <span class="menuLabel">{{ t }}</span>
        </button>
      </div>
    </transition>
  </div>
</template>

<script>
import vClickOutside from "click-outside-vue3";

// the order and names of ServersSortTypeEnum
const SortTypes = ["City", "Country", "Latency", "Proximity"];

export default {
  directives: {
    clickOutside: vClickOutside.directive,
  },
  emits: ["select"],
  props: {
    // "City" | "Country" | "Latency" | "Proximity"
    sortType: String,
  },
  data: () => ({
    isOpen: false,
    menuId: "srvSortMenu",
  }),
  computed: {
    types() {
      return SortTypes;
    },
  },
  methods: {
    toggle() {
      if (this.isOpen) this.close(false);
      else this.openAndFocus(-1);
    },
    // index -1: open and focus the checked item
    openAndFocus(index) {
      this.isOpen = true;
      this.$nextTick(() => {
        const items = this.menuItems();
        if (!items.length) return;
        let i = index;
        if (i < 0) i = Math.max(0, this.types.indexOf(this.sortType));
        if (items[i]) items[i].focus();
      });
    },
    close(returnFocus) {
      this.isOpen = false;
      if (returnFocus && this.$refs.sortBtn) this.$refs.sortBtn.focus();
    },
    onClickOutside() {
      if (this.isOpen) this.close(false);
    },
    select(t) {
      this.$emit("select", t);
      this.close(true);
    },
    // in document order (refs inside v-for do not keep the order)
    menuItems() {
      if (!this.$el || !this.$el.querySelectorAll) return [];
      return Array.from(this.$el.querySelectorAll(".menuItem"));
    },
    onMenuKeydown(e) {
      const items = this.menuItems();
      const i = items.indexOf(document.activeElement);
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          if (items.length) items[(i + 1) % items.length].focus();
          break;
        case "ArrowUp":
          e.preventDefault();
          if (items.length)
            items[(i - 1 + items.length) % items.length].focus();
          break;
        case "Home":
          e.preventDefault();
          if (items.length) items[0].focus();
          break;
        case "End":
          e.preventDefault();
          if (items.length) items[items.length - 1].focus();
          break;
        case "Escape":
          e.preventDefault();
          e.stopPropagation();
          this.close(true);
          break;
        case "Tab":
          this.close(false);
          break;
      }
    },
  },
};
</script>

<style scoped lang="scss">
svg,
svg * {
  color: inherit;
}

.sortWrap {
  position: relative;
  flex: none;
}

.sortBtn {
  width: 38px;
  height: 38px;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  border: 1px solid var(--control-border);
  border-radius: 10px;
  background: var(--surface-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
}
.sortBtn svg {
  display: block;
  stroke: var(--text-soft);
}
.sortBtn:hover {
  background: var(--neutral-tint);
}
.sortBtn.open {
  border-color: var(--accent-ring);
  background: var(--accent-tint);
}
.sortBtn.open svg {
  stroke: var(--link-color);
}
.sortBtn:focus {
  outline: none;
}
.sortBtn:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}

// under the button, right edges aligned
.sortMenu {
  position: absolute;
  z-index: 30;
  top: 44px;
  right: 0;
  width: 176px;
  box-sizing: border-box;
  padding: 6px;
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  background: var(--surface-color);
  box-shadow: 0 10px 30px rgba(0, 0, 0, var(--srv-menu-shadow, 0.14));
  display: flex;
  flex-direction: column;
}
.menuTitle {
  height: 24px;
  box-sizing: border-box;
  padding: 0 10px;
  display: flex;
  align-items: center;
  font-size: 10.5px;
  font-weight: 600;
  line-height: 14px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-faint);
}
.menuItem {
  height: 32px;
  margin: 0;
  box-sizing: border-box;
  padding: 0 10px 0 8px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 8px;
  text-align: left;
  font-family: inherit;
  cursor: pointer;
}
.menuItem:hover,
.menuItem:focus-visible {
  background: var(--neutral-tint);
}
.menuItem:focus {
  outline: none;
}
.menuItem:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
.menuCheck {
  width: 16px;
  height: 16px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
}
.menuCheck svg {
  display: block;
  stroke: var(--link-color);
}
.menuLabel {
  font-size: 13px;
  font-weight: 500;
  line-height: 16px;
  color: var(--text-soft);
  white-space: nowrap;
}
.menuItem.checked .menuLabel {
  font-weight: 600;
  color: var(--link-color);
}
// the gold label keeps its contrast on the gold tint (not on the grey hover)
.menuItem.checked:hover,
.menuItem.checked:focus-visible {
  background: var(--accent-tint);
}

.srvMenu-enter-active {
  transition: opacity 0.12s, transform 0.12s;
}
.srvMenu-leave-active {
  transition: opacity 0.08s;
}
.srvMenu-enter-from {
  opacity: 0;
  transform: translateY(-4px);
}
.srvMenu-leave-to {
  opacity: 0;
}
</style>
