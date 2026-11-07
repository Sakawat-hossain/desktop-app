<template>
  <footer v-if="planName" class="planBar">
    <span class="planPill">{{ planName }}</span>
    <span class="planText">{{ planText }}</span>
    <button v-if="isUpgradable" class="planLink" v-on:click="onUpgrade">
      Upgrade
    </button>
  </footer>
</template>

<script>
const sender = window.ipcSender;
import config from "@/config";
import { dateDefaultFormat } from "@/helpers/helpers";

export default {
  computed: {
    status() {
      return this.$store.state.account.accountStatus;
    },
    planName() {
      const name = (this.status?.CurrentPlan || "").trim();
      return name.replace(/\s+plan$/i, "").toUpperCase();
    },
    planText() {
      const s = this.status;
      if (!s) return "";
      if (s.Active === false && s.ActiveUntil) return "Expired";
      if (!s.ActiveUntil) return "No end date";
      try {
        return "Active until " + dateDefaultFormat(new Date(s.ActiveUntil * 1000));
      } catch (e) {
        return "";
      }
    },
    isUpgradable() {
      return this.status?.Upgradable === true;
    },
  },
  methods: {
    onUpgrade() {
      sender.shellOpenExternal(config.URLAccount);
    },
  },
};
</script>

<style scoped lang="scss">
.planBar {
  flex: none;
  height: 46px;
  box-sizing: border-box;
  padding: 0 16px;
  border-top: 1px solid var(--surface-divider);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
.planPill {
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--neutral-tint);
  color: var(--text-color);
  font-weight: 600;
  font-size: 10.5px;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.planText {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
}
.planLink {
  border: 0;
  background: none;
  padding: 4px 2px;
  font-size: 12px;
  font-weight: 600;
  color: var(--link-color);
  cursor: pointer;
}
.planLink:hover {
  text-decoration: underline;
}
</style>
