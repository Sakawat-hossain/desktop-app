<template>
  <div class="cityItem">
    <!-- a location of an open card (28 px): city, tier chip, server count, latency -->
    <div class="cityRow">
      <svg
        class="tree"
        width="30"
        height="28"
        viewBox="0 0 30 28"
        aria-hidden="true"
      >
        <path
          :d="isLast ? 'M19.5 0V9Q19.5 14 24.5 14H30' : 'M19.5 0V28M19.5 14H30'"
        />
      </svg>
      <div class="cityBox" :class="{ selected: isSelected, bottom: isCardEnd }">
        <button
          ref="cityMain"
          type="button"
          class="cityMain"
          :class="{ locked: isLocked, inaccessible: isInaccessible }"
          :aria-current="isSelected ? 'location' : null"
          :aria-label="ariaLabel"
          :aria-expanded="isLocked ? (isUpgradeOpen ? 'true' : 'false') : null"
          :aria-controls="isUpgradeOpen ? upgradeCardId : null"
          :title="tooltip"
          v-on:click="onClick"
        >
          <!-- the city (one the header names already: the row starts with
               the count); a city wider than the row alone steps down to 11
               px, then takes two lines (the items after it left out, named
               in the tooltip); more than two lines end in an ellipsis -->
          <span ref="cityName" class="cityName" :class="nameClass">{{
            nameText
          }}</span>
          <!-- Items right to left by importance: the latency, the count, the
               tier chip, the ISP (setting). One that does not fit wraps to the
               hidden second line (with all after it), so each is shown whole
               or not at all. -->
          <span class="cityMeta">
            <span class="metaKeep"></span>
            <span v-if="isLocked" class="metaItem">
              <span class="metaDot" aria-hidden="true">&middot;</span>
              <svg
                class="lockIcon"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <rect x="5" y="10.5" width="14" height="10" rx="2" />
                <path d="M8.5 10.5V7.5a3.5 3.5 0 0 1 7 0v3" />
              </svg>
              <span class="metaLocked">Locked</span>
            </span>
            <span v-else-if="ping != null" class="metaItem">
              <span class="metaDot" aria-hidden="true">&middot;</span>
              <span class="metaMs" :class="'q-' + quality">{{ pingText }}</span>
            </span>
            <span v-if="!sameAsHeader" class="metaItem">
              <span class="metaDot" aria-hidden="true">&middot;</span>
              <span class="metaCount">{{ countText }}</span>
            </span>
            <ServerChips
              v-if="showTier"
              class="metaChips"
              :tier="tier"
              :premiumTitle="premiumTitle"
              shrinkWord
            />
            <span v-if="ispText" class="metaItem">
              <span class="metaDot" aria-hidden="true">&middot;</span>
              <span class="metaIsp">{{ ispText }}</span>
            </span>
          </span>
        </button>
        <ChevronBtn
          v-if="canExpand"
          :class="{ bottom: isCardEnd }"
          :expanded="isHostsOpen"
          :label="
            (isHostsOpen ? 'Hide servers in ' : 'Show servers in ') + city
          "
          v-on:click="$emit('toggle-hosts', location)"
        />
        <span v-else class="slot" aria-hidden="true"></span>
      </div>
    </div>

    <UpgradeCard
      v-if="isUpgradeOpen"
      :cardId="upgradeCardId"
      :name="city"
      :indent="isHostsShown ? 46 : 38"
      :lines="upgradeLines"
      v-on:dismiss="onDismissUpgrade"
    />

    <template v-if="isHostsShown">
      <HostRow
        v-for="(host, i) of hosts"
        :key="host.hostname || i"
        :location="location"
        :host="host"
        :isExitServer="isExitServer"
        :isPremiumAccount="isPremiumAccount"
        :funcGetPing="funcGetPing"
        :isLast="i === hosts.length - 1"
        :isCityLast="isLast"
        :isSelected="
          isSelected && !!selectedHostId && hostId(host) === selectedHostId
        "
        :upgradeKey="upgradeKey"
        v-on:select-host="(s, h) => $emit('select-host', s, h)"
        v-on:favorite="(e, s, h) => $emit('favorite', e, s, h)"
        v-on:toggle-upgrade="(k) => $emit('toggle-upgrade', k)"
        v-on:close-upgrade="$emit('close-upgrade')"
      />
    </template>
  </div>
</template>

<script>
import ServerChips from "@/components/servers/servers-chips.vue";
import ChevronBtn from "@/components/servers/servers-chevron-btn.vue";
import UpgradeCard from "@/components/servers/servers-upgrade-card.vue";
import HostRow from "@/components/servers/servers-host-row.vue";
import { HostId } from "@/helpers/helpers_premium";
import {
  CheckIsInaccessibleServer,
  IsServerSupportIPv6,
  GetSreverISPs,
} from "@/helpers/helpers_servers";
import {
  EntryTier,
  IsEntryLocked,
  EntryPing,
  HostsByPing,
  TierText,
  ServersCountText,
  PingText,
  PingQualityName,
  UpgradeKeyForEntry,
  UpgradeCardDomId,
} from "@/components/servers/servers-helpers";

export default {
  components: { ServerChips, ChevronBtn, UpgradeCard, HostRow },
  emits: [
    "select",
    "select-host",
    "toggle-hosts",
    "favorite",
    "toggle-upgrade",
    "close-upgrade",
  ],
  props: {
    location: { type: Object, required: true },
    isExitServer: [String, Boolean],
    isPremiumAccount: Boolean,
    funcGetPing: Function,
    // the card holds more than one location: the row names its tier
    showTier: Boolean,
    // the card's header names the city already ("Hong Kong"; "India" with
    // "Kolkata" after it)
    sameAsHeader: Boolean,
    // the last location of the card (the tree line ends here)
    isLast: Boolean,
    // the host rows may be shown (the "show hosts" setting)
    hostsEnabled: Boolean,
    isHostsOpen: Boolean,
    // the selected / connected location, and the host the user chose of it
    isSelected: Boolean,
    selectedHostId: String,
    upgradeKey: String,
  },
  data: () => ({
    // a name wider than the row: 0 = 12.5 px, 1 = 11 px, 2 = two lines of 11 px
    nameStep: 0,
    // ... and more than two lines even then (an ellipsis)
    isNameCut: false,
  }),
  computed: {
    settings() {
      return this.$store.state.settings;
    },
    city() {
      return this.location.city || this.location.country || "";
    },
    nameText() {
      return this.sameAsHeader ? this.countText : this.city;
    },
    nameClass() {
      return { fs11: this.nameStep >= 1, wrap2: this.nameStep === 2 };
    },
    tier() {
      return EntryTier(this.location);
    },
    premiumTitle() {
      return this.tier === "Mixed"
        ? `${this.city} also has Premium servers`
        : null;
    },
    hostCount() {
      return (this.location.hosts || []).length;
    },
    countText() {
      return ServersCountText(this.hostCount);
    },
    isLocked() {
      return IsEntryLocked(this.location, this.isPremiumAccount);
    },
    ping() {
      return EntryPing(this.location, this.funcGetPing, this.isPremiumAccount);
    },
    pingText() {
      return PingText(this.ping);
    },
    quality() {
      return PingQualityName(this.ping);
    },
    canExpand() {
      return this.hostsEnabled && this.hostCount >= 2;
    },
    isHostsShown() {
      return this.canExpand && this.isHostsOpen;
    },
    hosts() {
      return HostsByPing(
        this.location,
        this.funcGetPing,
        this.isPremiumAccount,
      );
    },
    inaccessibleText() {
      const r = CheckIsInaccessibleServer(this.isExitServer, this.location);
      return r ? r.message || "" : null;
    },
    isInaccessible() {
      return this.inaccessibleText !== null;
    },
    isShowIPv6() {
      return (
        this.settings.enableIPv6InTunnel === true &&
        this.settings.showGatewaysWithoutIPv6 === true &&
        IsServerSupportIPv6(this.location) === true
      );
    },
    ispText() {
      if (this.settings.showISPInfo !== true) return "";
      const isps = GetSreverISPs(this.location);
      return isps.length === 1 ? isps[0] : "";
    },
    tooltip() {
      const t = [
        // a name on two lines leaves no room for the count and the latency
        this.nameStep === 2 ? this.ariaLabel : "",
        this.inaccessibleText,
        this.isShowIPv6 ? "IPv6 supported" : "",
        this.ispText ? "ISP: " + this.ispText : "",
      ];
      return t.filter((v) => !!v).join("\n") || null;
    },
    // "Tokyo, Premium, 1 server, 124 ms" / "Dhaka District, 2 servers, fastest 198 ms"
    ariaLabel() {
      const t = [this.city];
      if (this.showTier || this.isLocked) t.push(TierText(this.tier));
      t.push(this.countText);
      if (this.isLocked) t.push("locked");
      else if (this.ping != null)
        t.push((this.hostCount > 1 ? "fastest " : "") + this.pingText);
      return t.join(", ");
    },
    upgradeLines() {
      const t = [];
      if (!this.isLast) t.push(19);
      if (this.isHostsShown) t.push(36);
      return t;
    },
    // the row ends the card: its corner follows the card's rounded corner
    isCardEnd() {
      return this.isLast && !this.isHostsShown && !this.isUpgradeOpen;
    },
    upgradeKeyOwn() {
      return UpgradeKeyForEntry(this.location);
    },
    isUpgradeOpen() {
      return this.isLocked && this.upgradeKey === this.upgradeKeyOwn;
    },
    upgradeCardId() {
      return UpgradeCardDomId(this.upgradeKeyOwn);
    },
  },
  watch: {
    nameText() {
      this.$nextTick(this.refitName);
    },
  },
  mounted() {
    // the row's width (not the name's, which the steps change)
    if (typeof ResizeObserver !== "undefined" && this.$refs.cityMain) {
      this.nameObserver = new ResizeObserver((entries) => {
        const e = entries[entries.length - 1];
        const w = e ? e.contentRect.width : null;
        if (w === this.mainWidth) return;
        this.mainWidth = w;
        this.refitName();
      });
      this.nameObserver.observe(this.$refs.cityMain);
    }
    this.refitName();
  },
  beforeUnmount() {
    if (this.nameObserver) this.nameObserver.disconnect();
    this.nameObserver = null;
  },
  methods: {
    hostId(host) {
      return HostId(host);
    },
    // the row's width or the name changed: measure again from 12.5 px
    refitName() {
      if (this.nameStep === 0 && !this.isNameCut) {
        this.checkNameCut();
        return;
      }
      this.nameStep = 0;
      this.isNameCut = false;
      this.$nextTick(this.checkNameCut);
    },
    // a name wider than the row (on two lines: needing a third): one step
    // on, then measure again
    checkNameCut() {
      const el = this.$refs.cityName;
      if (!el || this.isNameCut) return;
      // (a third line adds 13 px; the glyphs may reach a pixel past the second)
      const over =
        this.nameStep === 2
          ? el.scrollHeight > el.clientHeight + 6.5
          : el.scrollWidth > el.clientWidth + 0.5;
      if (!over) return;
      if (this.nameStep < 2) {
        this.nameStep++;
        this.$nextTick(this.checkNameCut);
        return;
      }
      this.isNameCut = true;
    },
    onClick() {
      if (this.isLocked) {
        this.$emit("toggle-upgrade", this.upgradeKeyOwn);
        return;
      }
      this.$emit("select", this.location);
    },
    // "Not now": the card goes and the focus returns to the row that opened it
    onDismissUpgrade() {
      this.$emit("close-upgrade");
      this.$nextTick(() => {
        if (this.$refs.cityMain) this.$refs.cityMain.focus();
      });
    },
  },
};
</script>

<style scoped lang="scss">
// R6B city row: 30 px tree | box (button: 8 px | city, meta ... | 4 px)
// | 24 px chevron column
.cityItem {
  display: flex;
  flex-direction: column;
}
.cityRow {
  height: 28px;
  flex: none;
  display: flex;
  align-items: center;
}

// the global 'html * { color }' rule stops currentColor from inheriting
svg,
svg * {
  color: inherit;
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

.cityBox {
  flex: 1;
  min-width: 0;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  transition: background-color 0.15s;
}
.cityBox.selected {
  background: var(--accent-tint);
}
// not while the chevron is hovered: its own box shows then
.cityBox:not(.selected):not(:has(.chevronBtn:hover)):hover {
  background: var(--neutral-tint);
}
// the last row of the card: the corner follows the card's (12 px, 1 px border),
// and so does the chevron's own hover box in that corner
.cityBox.bottom,
.chevronBtn.bottom {
  border-bottom-right-radius: 11px;
}

button {
  margin: 0;
  font-family: inherit;
}
button:focus {
  outline: none;
}

.cityMain {
  flex: 1;
  min-width: 0;
  height: 28px;
  box-sizing: border-box;
  padding: 0 4px 0 8px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 5px;
  text-align: left;
  cursor: pointer;
}
.cityMain:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
// shrinks only when the name alone is wider than the row (the meta items
// drop out whole first, as .cityMeta's basis is 0)
.cityName {
  flex: 0 1 auto;
  min-width: 0;
  display: block;
  font-size: 12.5px;
  font-weight: 600;
  line-height: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cityName.fs11 {
  font-size: 11px;
}
// two lines of 13 px in the 28 px row (more end in an ellipsis)
.cityName.wrap2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-height: 13px;
  white-space: normal;
  overflow-wrap: anywhere;
}
.cityMain.locked .cityName {
  color: var(--text-muted);
}
.inaccessible {
  opacity: 0.5;
}

// right-to-left placement, packed to the left: the chips grow from their
// smallest form to the whole chips with the room that is left
.cityMeta {
  flex: 1 1 0;
  min-width: 0;
  height: 16px;
  display: flex;
  flex-direction: row-reverse;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  column-gap: 5px;
  overflow: hidden;
}
.metaKeep {
  flex: none;
  width: 0;
  height: 16px;
}
.metaItem {
  flex: none;
  height: 16px;
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
}
.metaDot {
  font-size: 11.5px;
  line-height: 16px;
  color: var(--text-faint);
}
.metaCount {
  font-size: 11.5px;
  line-height: 16px;
  color: var(--text-muted);
}
.metaIsp {
  font-size: 11.5px;
  line-height: 16px;
  color: var(--text-faint);
}
.metaMs {
  font-size: 11.5px;
  font-weight: 600;
  line-height: 16px;
  font-variant-numeric: tabular-nums;
}
.metaMs.q-good {
  color: var(--good-text);
}
.metaMs.q-moderate {
  color: var(--srv-moderate, #b45309);
}
.metaMs.q-bad {
  color: var(--danger-text);
}
.lockIcon {
  display: block;
  flex: none;
  margin-right: -2px; // lock and word read as one mark (3 px apart)
  fill: none;
  stroke: var(--text-muted);
}
.metaLocked {
  font-size: 11.5px;
  font-weight: 500;
  line-height: 16px;
  color: var(--text-muted);
}

.slot {
  width: 24px;
  flex: none;
  display: block;
}
</style>
