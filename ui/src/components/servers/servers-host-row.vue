<template>
  <div class="hostItem">
    <!-- a host of an open city (28 px): short name, tier, latency, star -->
    <div class="hostRow">
      <svg
        class="tree"
        width="42"
        height="28"
        viewBox="0 0 42 28"
        aria-hidden="true"
      >
        <path :d="treePath" />
      </svg>
      <div class="hostBox" :class="{ bottom: isCardEnd }">
        <button
          ref="hostMain"
          type="button"
          class="hostMain"
          :class="{
            selected: isSelected,
            inaccessible: isInaccessible,
            locked: isLocked,
          }"
          :aria-current="isSelected ? 'true' : null"
          :aria-label="ariaLabel"
          :aria-expanded="isLocked ? (isUpgradeOpen ? 'true' : 'false') : null"
          :aria-controls="isUpgradeOpen ? upgradeCardId : null"
          :title="tooltip"
          v-on:click="onClick"
        >
          <span class="hostTexts">
            <!-- a name wider than the row alone ends in an ellipsis and is
                 named in the tooltip -->
            <span ref="hostName" class="hostName">{{ shortName }}</span>
            <ServerChips :tier="tier" shrinkWord />
            <!-- ISP (optional setting): shown whole or not at all -->
            <span v-if="isp" class="ispBox"
              ><span class="ispText">{{ isp }}</span></span
            >
          </span>
          <ServerPing :ms="ping" :locked="isLocked" />
        </button>
        <StarBtn
          :pressed="isFavorite"
          :label="favoriteLabel"
          v-on:click="$emit('favorite', $event, location, host)"
        />
        <span class="slot" aria-hidden="true"></span>
      </div>
    </div>

    <UpgradeCard
      v-if="isUpgradeOpen"
      :cardId="upgradeCardId"
      :name="fullName"
      :indent="46"
      :lines="upgradeLines"
      v-on:dismiss="onDismissUpgrade"
    />
  </div>
</template>

<script>
import ServerChips from "@/components/servers/servers-chips.vue";
import ServerPing from "@/components/servers/servers-ping.vue";
import StarBtn from "@/components/servers/servers-star-btn.vue";
import UpgradeCard from "@/components/servers/servers-upgrade-card.vue";
import { IsHostLocked, HostShortName } from "@/helpers/helpers_premium";
import { CheckIsInaccessibleServer } from "@/helpers/helpers_servers";
import {
  HostTier,
  HostPing,
  TierText,
  PingText,
  UpgradeKeyForHost,
  UpgradeCardDomId,
} from "@/components/servers/servers-helpers";

export default {
  components: { ServerChips, ServerPing, StarBtn, UpgradeCard },
  emits: ["select-host", "favorite", "toggle-upgrade", "close-upgrade"],
  props: {
    location: { type: Object, required: true },
    host: { type: Object, required: true },
    isExitServer: [String, Boolean],
    isPremiumAccount: Boolean,
    funcGetPing: Function,
    // the last host of its city / its city is the last one of the card
    isLast: Boolean,
    isCityLast: Boolean,
    // the user chose this host (it is the selected / connected one)
    isSelected: Boolean,
    // key of the open upgrade card in the list (one at a time)
    upgradeKey: String,
  },
  data: () => ({
    // the name is wider than the row and ends in an ellipsis
    isNameCut: false,
  }),
  computed: {
    settings() {
      return this.$store.state.settings;
    },
    city() {
      return this.location.city || this.location.country || "";
    },
    shortName() {
      return HostShortName(this.location, this.host);
    },
    // "Server 2 in Dhaka District"
    fullName() {
      return this.city ? `${this.shortName} in ${this.city}` : this.shortName;
    },
    tier() {
      return HostTier(this.host);
    },
    isLocked() {
      return IsHostLocked(this.host, this.isPremiumAccount);
    },
    ping() {
      return HostPing(this.host, this.funcGetPing, this.isPremiumAccount);
    },
    isp() {
      if (this.settings.showISPInfo !== true) return "";
      return this.host.isp || "";
    },
    inaccessibleText() {
      const r = CheckIsInaccessibleServer(
        this.isExitServer,
        this.location,
        this.host,
      );
      return r ? r.message || "" : null;
    },
    isInaccessible() {
      return this.inaccessibleText !== null;
    },
    tooltip() {
      const t = [
        this.isNameCut ? this.shortName : "",
        this.inaccessibleText,
        this.isp ? "ISP: " + this.isp : "",
      ];
      return t.filter((v) => !!v).join("\n") || null;
    },
    // "Server 2, Dhaka District, Premium, 198 ms"
    ariaLabel() {
      const t = [this.shortName, this.city, TierText(this.tier)];
      if (this.isLocked) t.push("locked");
      else if (this.ping != null) t.push(PingText(this.ping));
      return t.filter((v) => !!v).join(", ");
    },
    isFavorite() {
      return this.settings.hostsFavoriteListDnsNames.includes(
        this.host.dns_name,
      );
    },
    favoriteLabel() {
      return this.isFavorite
        ? `Remove ${this.fullName} from favorites`
        : `Add ${this.fullName} to favorites`;
    },
    // the city's line on the left; the hosts' line when more hosts follow
    treePath() {
      const city = this.isCityLast ? "" : "M19.5 0V28";
      const host = this.isLast
        ? "M36.5 0V10Q36.5 14 40.5 14H42"
        : "M36.5 0V28M36.5 14H42";
      return city + host;
    },
    upgradeLines() {
      const t = [];
      if (!this.isCityLast) t.push(19);
      if (!this.isLast) t.push(36);
      return t;
    },
    // the row ends the card: its corner follows the card's rounded corner
    isCardEnd() {
      return this.isCityLast && this.isLast && !this.isUpgradeOpen;
    },
    upgradeKeyOwn() {
      return UpgradeKeyForHost(this.location, this.host);
    },
    isUpgradeOpen() {
      return this.isLocked && this.upgradeKey === this.upgradeKeyOwn;
    },
    upgradeCardId() {
      return UpgradeCardDomId(this.upgradeKeyOwn);
    },
  },
  watch: {
    shortName() {
      this.$nextTick(this.checkNameCut);
    },
  },
  mounted() {
    if (typeof ResizeObserver !== "undefined" && this.$refs.hostName) {
      this.nameObserver = new ResizeObserver(() => this.checkNameCut());
      this.nameObserver.observe(this.$refs.hostName);
    }
    this.checkNameCut();
  },
  beforeUnmount() {
    if (this.nameObserver) this.nameObserver.disconnect();
    this.nameObserver = null;
  },
  methods: {
    checkNameCut() {
      const el = this.$refs.hostName;
      const cut = !!el && el.scrollWidth > el.clientWidth + 0.5;
      if (cut !== this.isNameCut) this.isNameCut = cut;
    },
    onClick() {
      if (this.isLocked) {
        this.$emit("toggle-upgrade", this.upgradeKeyOwn);
        return;
      }
      this.$emit("select-host", this.location, this.host);
    },
    // "Not now": the card goes and the focus returns to the row that opened it
    onDismissUpgrade() {
      this.$emit("close-upgrade");
      this.$nextTick(() => {
        if (this.$refs.hostMain) this.$refs.hostMain.focus();
      });
    },
  },
};
</script>

<style scoped lang="scss">
// R6B host row: 42 px tree | button (4 px | name, tier chip ... latency | 2 px)
// | 28 px star | 24 px empty column (the chevron column of the card)
.hostItem {
  display: flex;
  flex-direction: column;
}
.hostRow {
  height: 28px;
  flex: none;
  display: flex;
  align-items: center;
}

.tree {
  display: block;
  flex: none;
}
.tree path {
  fill: none;
  stroke: var(--srv-tree-line, #d4d4d8);
  stroke-width: 1;
}

.hostBox {
  flex: 1;
  min-width: 0;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  transition: background-color 0.15s;
}
// not while the star is hovered: its own box shows then
.hostBox:not(:has(.starBtn:hover)):hover {
  background: var(--neutral-tint);
}
// the last row of the card: the corner follows the card's (12 px, 1 px border)
.hostBox.bottom {
  border-bottom-right-radius: 11px;
}

button {
  margin: 0;
  font-family: inherit;
}
button:focus {
  outline: none;
}

.hostMain {
  flex: 1;
  min-width: 0;
  height: 28px;
  box-sizing: border-box;
  padding: 0 2px 0 4px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 6px;
  text-align: left;
  cursor: pointer;
}
.hostMain:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
.hostTexts {
  flex: 1;
  min-width: 0;
  height: 16px;
  display: flex;
  align-items: center;
  gap: 5px;
}
// shrinks only when the name alone is wider than the row
.hostName {
  flex: 0 1 auto;
  min-width: 0;
  display: block;
  font-size: 12px;
  font-weight: 500;
  line-height: 16px;
  color: var(--text-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.hostMain.selected .hostName {
  font-weight: 600;
  color: var(--link-color);
}
.hostMain.locked .hostName {
  color: var(--text-faint);
}
.inaccessible {
  opacity: 0.5;
}

// ISP of a host (optional setting): takes only the room the name and the chip
// leave, and shows the whole name or nothing: the 0-wide first item keeps the
// first line, so a name that does not fit wraps to the hidden second line
.ispBox {
  flex: 1 1 0;
  min-width: 0;
  height: 16px;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  overflow: hidden;
}
.ispBox::before {
  content: "";
  flex: none;
  width: 0;
  height: 16px;
}
.ispText {
  flex: none;
  font-size: 11px;
  line-height: 16px;
  color: var(--text-faint);
  white-space: nowrap;
}

.slot {
  width: 24px;
  flex: none;
  display: block;
}
</style>
