<template>
  <!-- Subscription card (72 px), pinned to the bottom of the left panel by Component-Control -->
  <div v-if="isVisible" class="planCard" role="group" aria-label="Subscription">
    <span class="planTile" aria-hidden="true">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 7.5l4.5 4L12 5l4.5 6.5L21 7.5 19 17H5z" />
        <path d="M5 20.5h14" />
      </svg>
    </span>

    <span class="planTexts">
      <span class="planName" :title="planTitle">{{ planTitle }}</span>
      <span class="planUntil">{{ untilText }}</span>
    </span>

    <span v-if="daysLeftText || actionText" class="planSide">
      <span v-if="daysLeftText" class="planDays" v-bind:class="daysClass">
        {{ daysLeftText }}
      </span>
      <button
        v-if="actionText"
        type="button"
        class="planAction"
        :title="actionTitle"
        v-on:click="onAction"
      >
        {{ actionText }}
      </button>
    </span>
  </div>
</template>

<script>
const sender = window.ipcSender;
import config from "@/config";
import { capitalizeFirstLetter } from "@/helpers/helpers";

const DAY_MS = 24 * 60 * 60 * 1000;
const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

// "7 Nov 2027" (day month year, as en-GB writes it)
function formatDay(unixSeconds) {
  const d = new Date(unixSeconds * 1000);
  if (isNaN(d.getTime())) return "";
  return `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

export default {
  data: () => ({
    now: Date.now(),
    clockTimer: null,
  }),
  mounted() {
    // the days-left count must move on while the app stays open
    this.clockTimer = setInterval(() => {
      this.now = Date.now();
    }, 60 * 1000);
  },
  unmounted() {
    if (this.clockTimer) clearInterval(this.clockTimer);
  },
  computed: {
    status() {
      return this.$store.state.account.accountStatus;
    },
    // plan name without a trailing "plan" ("Yearly plan" -> "Yearly")
    planBaseName() {
      const name = String(this.status?.CurrentPlan || "").trim();
      return name.replace(/(^|\s+)plan$/i, "").trim();
    },
    planTitle() {
      if (!this.planBaseName) return "Your plan";
      return `${capitalizeFirstLetter(this.planBaseName)} plan`;
    },
    // ActiveUntil: unix seconds; 0 = the plan has no end date
    activeUntil() {
      const until = Number(this.status?.ActiveUntil);
      return Number.isFinite(until) && until > 0 ? until : 0;
    },
    isVisible() {
      if (!this.status) return false;
      return !!this.planBaseName || this.activeUntil > 0;
    },
    isExpired() {
      if (!this.activeUntil) return false;
      return this.activeUntil * 1000 <= this.now;
    },
    // the account is switched off although its end date has not come yet
    // (the daemon calls this "not active", as opposed to "expired")
    isInactive() {
      return !this.isExpired && this.status?.Active === false;
    },
    daysLeft() {
      if (!this.activeUntil) return null;
      return Math.max(0, Math.ceil((this.activeUntil * 1000 - this.now) / DAY_MS));
    },
    untilText() {
      if (!this.activeUntil) return "No end date";
      const day = formatDay(this.activeUntil);
      if (!day) return "";
      const isPast = this.activeUntil * 1000 <= this.now;
      return isPast ? `Ended ${day}` : `Until ${day}`;
    },
    daysLeftText() {
      if (this.isInactive) return "Not active";
      if (!this.activeUntil) return "";
      if (this.isExpired) return "Expired";
      return this.daysLeft === 1 ? "1 day left" : `${this.daysLeft} days left`;
    },
    daysClass() {
      if (this.isExpired || this.isInactive) return "daysExpired";
      return this.daysLeft > 14 ? "daysGood" : "daysSoon";
    },
    // Renew when the plan has an end date; Upgrade for a plan without one
    actionText() {
      if (this.activeUntil) return "Renew";
      if (this.status?.Upgradable === true) return "Upgrade";
      return "";
    },
    actionTitle() {
      return this.activeUntil
        ? "Renew your subscription"
        : "Upgrade your subscription";
    },
  },
  methods: {
    onAction() {
      sender.shellOpenExternal(config.URLAccount);
    },
  },
};
</script>

<style scoped lang="scss">
// the global 'html *' rule gives every element the text colour:
// let the crown take the colour of its tile instead
svg,
svg * {
  color: inherit;
}

.planCard {
  flex: none;
  min-height: 72px;
  box-sizing: border-box;
  margin: 0 16px;
  padding: 8px 12px;
  border: 1px solid var(--surface-border);
  border-radius: 14px;
  background: var(--surface-color);
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
}

.planTile {
  width: 40px;
  height: 40px;
  flex: none;
  box-sizing: border-box;
  border-radius: 12px;
  border: 1px solid var(--accent-ring);
  background: var(--accent-tint);
  color: var(--link-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.planTexts {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.planName {
  font-size: 14px;
  font-weight: 600;
  line-height: 18px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.planUntil {
  font-size: 12px;
  line-height: 16px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-variant-numeric: tabular-nums;
}

.planSide {
  flex: none;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}
.planDays {
  font-size: 11.5px;
  font-weight: 600;
  line-height: 15px;
  white-space: nowrap;
}
.daysGood {
  color: var(--good-text);
}
.daysSoon {
  color: var(--link-color);
}
.daysExpired {
  color: var(--danger-text);
}

.planAction {
  height: 26px;
  box-sizing: border-box;
  margin: 0;
  padding: 0 12px;
  border: 1px solid var(--accent-ring);
  border-radius: 8px;
  background: var(--accent-tint);
  color: var(--link-color);
  font-size: 12px;
  font-weight: 600;
  line-height: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: border-color 0.15s;
  -webkit-app-region: no-drag;
}
.planAction:hover {
  border-color: var(--accent-color);
}
.planAction:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: 2px;
}
</style>
