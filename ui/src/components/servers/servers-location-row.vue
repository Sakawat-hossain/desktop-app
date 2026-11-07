<template>
  <div class="locItem">
    <!-- the location (44 px); a locked one grows to hold the upgrade card -->
    <div
      class="locBox"
      :class="{
        selected: isSelected && !isUpgradeOpen,
        upgradeOpen: isUpgradeOpen,
      }"
    >
      <div class="locRow">
        <button
          v-if="canExpand"
          type="button"
          class="chevronBtn"
          :class="{ expanded: isExpanded }"
          :aria-expanded="isExpanded ? 'true' : 'false'"
          :aria-label="(isExpanded ? 'Hide hosts in ' : 'Show hosts in ') + title"
          :title="isExpanded ? 'Hide hosts' : 'Show hosts'"
          v-on:click="$emit('toggle-expand', entry)"
        >
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke-width="2.4"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path :d="isExpanded ? 'm6 9 6 6 6-6' : 'm9 6 6 6-6 6'" />
          </svg>
        </button>
        <span v-else class="chevronSpace" aria-hidden="true"></span>

        <button
          ref="locMain"
          type="button"
          class="locMain"
          :class="{ inaccessible: isInaccessible, locked: isLocked }"
          :aria-current="isSelected ? 'true' : null"
          :aria-label="isLocked ? title + ', Premium, locked' : null"
          :aria-expanded="isLocked ? (isUpgradeOpen ? 'true' : 'false') : null"
          :aria-controls="isUpgradeOpen ? upgradeCardId : null"
          :title="mainTooltip"
          v-on:click="onMainClick"
        >
          <ServerFlag :countryCode="countryCode" :dim="isLocked" />
          <span class="locTexts">
            <span class="locTitle">{{ title }}</span>
            <span class="locSub">
              <ServerChips
                fit
                :countryCode="countryCode"
                :tier="tier"
                :ipv6="isShowIPv6"
                :extra="ispText"
                :dim="isLocked"
              />
            </span>
          </span>
          <ServerPing :ms="ping" :locked="isLocked" :hint="pingHint" />
        </button>

        <button
          type="button"
          class="starBtn"
          :class="{ fav: isFavorite }"
          :aria-pressed="isFavorite ? 'true' : 'false'"
          :aria-label="favoriteLabel(title, isFavorite)"
          :title="favoriteLabel(title, isFavorite)"
          v-on:click="$emit('favorite', $event, entry)"
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            stroke-width="1.8"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z" />
          </svg>
        </button>
      </div>

      <UpgradeCard
        v-if="isUpgradeOpen"
        :cardId="upgradeCardId"
        :name="title"
        v-on:dismiss="onDismissUpgrade(-1)"
      />
    </div>

    <!-- hosts of the location (30 px rows): flag + display name, never the address -->
    <div
      v-if="canExpand && isExpanded"
      class="hosts"
      role="group"
      :aria-label="'Hosts in ' + title"
    >
      <template v-for="(host, i) of hosts" :key="host.hostname || i">
        <div class="hostRow">
          <svg class="tree" width="24" height="30" viewBox="0 0 24 30" aria-hidden="true">
            <path
              :d="i === hosts.length - 1 ? 'M12.5 0V15H21' : 'M12.5 0V30M12.5 15H21'"
            />
          </svg>
          <button
            type="button"
            class="hostMain"
            :class="{
              selected: isHostSelected(host),
              inaccessible: isHostInaccessible(host),
              locked: isHostLocked(host),
            }"
            :aria-current="isHostSelected(host) ? 'true' : null"
            :aria-label="isHostLocked(host) ? hostName(host) + ', Premium, locked' : null"
            :aria-expanded="
              isHostLocked(host)
                ? upgradeKey === hostUpgradeKey(host)
                  ? 'true'
                  : 'false'
                : null
            "
            :aria-controls="
              upgradeKey === hostUpgradeKey(host) ? hostUpgradeCardId(host) : null
            "
            :title="hostTooltip(host)"
            v-on:click="onHostClick(host)"
          >
            <ServerFlag :countryCode="countryCode" :dim="isHostLocked(host)" />
            <span class="hostTexts">
              <!-- the full name on hover: a long name is shortened in the row -->
              <span class="hostName" :title="hostName(host)"
                ><span class="hostNameHead">{{ hostNameParts(host)[0] }}</span
                ><span v-if="hostNameParts(host)[1]" class="hostNameTail">{{
                  hostNameParts(host)[1]
                }}</span></span
              >
              <ServerChips :tier="hostTier(host)" shrinkWord />
              <span v-if="hostIsp(host)" class="ispBox"
                ><span class="ispText">{{ hostIsp(host) }}</span></span
              >
            </span>
            <ServerPing :ms="hostPing(host)" :locked="isHostLocked(host)" />
          </button>
          <button
            type="button"
            class="starBtn"
            :class="{ fav: isHostFavorite(host) }"
            :aria-pressed="isHostFavorite(host) ? 'true' : 'false'"
            :aria-label="favoriteLabel(hostName(host), isHostFavorite(host))"
            :title="favoriteLabel(hostName(host), isHostFavorite(host))"
            v-on:click="$emit('favorite', $event, entry, host)"
          >
            <svg
              width="15"
              height="15"
              viewBox="0 0 24 24"
              stroke-width="1.8"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z" />
            </svg>
          </button>
        </div>

        <UpgradeCard
          v-if="upgradeKey === hostUpgradeKey(host)"
          class="hostUpgrade"
          standalone
          :cardId="hostUpgradeCardId(host)"
          :name="hostName(host)"
          v-on:dismiss="onDismissUpgrade(i)"
        />
      </template>
    </div>
  </div>
</template>

<script>
import ServerFlag from "@/components/servers/servers-flag.vue";
import ServerChips from "@/components/servers/servers-chips.vue";
import ServerPing from "@/components/servers/servers-ping.vue";
import UpgradeCard from "@/components/servers/servers-upgrade-card.vue";
import {
  IsHostLocked,
  IsServerMixed,
  HostDisplayName,
  HostId,
} from "@/helpers/helpers_premium";
import {
  CheckIsInaccessibleServer,
  IsServerSupportIPv6,
  GetSreverISPs,
} from "@/helpers/helpers_servers";
import {
  GatewayId,
  IsFavHostEntry,
  EntryLocation,
  EntryTier,
  HostTier,
  IsEntryLocked,
  EntryPing,
  HostPing,
  UpgradeKeyForEntry,
  UpgradeKeyForHost,
  UpgradeCardDomId,
  IsPremiumAccountFor,
} from "@/components/servers/servers-helpers";

export default {
  components: { ServerFlag, ServerChips, ServerPing, UpgradeCard },
  emits: [
    "select",
    "select-host",
    "toggle-expand",
    "favorite",
    "toggle-upgrade",
    "close-upgrade",
  ],
  props: {
    // a location, or a favourite host entry of the Favorites list
    entry: { type: Object, required: true },
    isExitServer: [String, Boolean],
    // this location (or favourite host) is the selected / connected one
    isSelected: Boolean,
    // host id ("dhaka1") of the selected host when the location is selected
    selectedHostId: String,
    // the location shows the expand chevron (more than one host)
    canExpand: Boolean,
    isExpanded: Boolean,
    // key of the open upgrade card in the list (one at a time)
    upgradeKey: String,
  },
  computed: {
    isFavHost() {
      return IsFavHostEntry(this.entry);
    },
    location() {
      return EntryLocation(this.entry);
    },
    hosts() {
      if (this.isFavHost) return [];
      return this.entry.hosts || [];
    },
    isPremiumAccount() {
      return IsPremiumAccountFor(this.$store.getters);
    },
    funcGetPing() {
      return this.$store.getters["vpnState/funcGetPing"];
    },
    settings() {
      return this.$store.state.settings;
    },

    title() {
      if (this.isFavHost)
        return HostDisplayName(this.location, this.entry.favHost);
      const s = this.entry;
      return s.city || s.country || "";
    },
    countryCode() {
      return this.location ? this.location.country_code : "";
    },
    tier() {
      return EntryTier(this.entry);
    },
    isLocked() {
      return IsEntryLocked(this.entry, this.isPremiumAccount);
    },
    ping() {
      return EntryPing(this.entry, this.funcGetPing, this.isPremiumAccount);
    },
    pingHint() {
      if (
        !this.isPremiumAccount &&
        !this.isFavHost &&
        IsServerMixed(this.entry)
      )
        return "Best ping among the Free hosts you can use";
      return null;
    },
    inaccessibleInfo() {
      return CheckIsInaccessibleServer(
        this.isExitServer,
        this.location,
        this.isFavHost ? this.entry.favHost : null,
      );
    },
    isInaccessible() {
      return this.inaccessibleInfo !== null && this.inaccessibleInfo !== undefined;
    },
    inaccessibleText() {
      return this.isInaccessible ? this.inaccessibleInfo.message || null : null;
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
      if (this.isFavHost) return this.entry.favHost.isp || "";
      const isps = GetSreverISPs(this.entry);
      return isps.length === 1 ? isps[0] : "";
    },
    // multi-hop warning and, when the settings show them, IPv6 and the ISP (the
    // inline IPv6 chip and ISP text are left out when the row is too narrow)
    mainTooltip() {
      const t = [
        this.inaccessibleText,
        this.isShowIPv6 ? "IPv6 supported" : "",
        this.ispText ? "ISP: " + this.ispText : "",
      ];
      return t.filter((v) => !!v).join("\n") || null;
    },
    isFavorite() {
      if (this.isFavHost)
        return this.settings.hostsFavoriteListDnsNames.includes(
          this.entry.favHost.dns_name,
        );
      return this.settings.serversFavoriteList.includes(
        GatewayId(this.entry.gateway),
      );
    },
    upgradeKeyOwn() {
      return UpgradeKeyForEntry(this.entry);
    },
    isUpgradeOpen() {
      return this.isLocked && this.upgradeKey === this.upgradeKeyOwn;
    },
    upgradeCardId() {
      return UpgradeCardDomId(this.upgradeKeyOwn);
    },
  },
  methods: {
    favoriteLabel(name, isFav) {
      return isFav
        ? `Remove ${name} from favorites`
        : `Add ${name} to favorites`;
    },
    onMainClick() {
      if (this.isLocked) {
        this.$emit("toggle-upgrade", this.upgradeKeyOwn);
        return;
      }
      this.$emit("select", this.entry);
    },

    hostName(host) {
      return HostDisplayName(this.entry, host);
    },
    // "Dhaka District #12" => ["Dhaka District", " #12"]: when the name is too long
    // the start gets the ellipsis and the number stays readable
    hostNameParts(host) {
      const name = this.hostName(host) || "";
      const m = name.match(/^(.*\S)(\s+#?\d+)$/);
      if (!m) return [name, ""];
      return [m[1], m[2].replace(/^\s+/, "\u00a0")];
    },
    hostTier(host) {
      return HostTier(host);
    },
    hostPing(host) {
      return HostPing(host, this.funcGetPing, this.isPremiumAccount);
    },
    hostIsp(host) {
      if (this.settings.showISPInfo !== true) return "";
      return (host && host.isp) || "";
    },
    isHostLocked(host) {
      return IsHostLocked(host, this.isPremiumAccount);
    },
    isHostSelected(host) {
      return (
        this.isSelected === true &&
        !!this.selectedHostId &&
        HostId(host) === this.selectedHostId
      );
    },
    hostInaccessibleInfo(host) {
      return CheckIsInaccessibleServer(this.isExitServer, this.entry, host);
    },
    isHostInaccessible(host) {
      const r = this.hostInaccessibleInfo(host);
      return r !== null && r !== undefined;
    },
    hostInaccessibleText(host) {
      const r = this.hostInaccessibleInfo(host);
      return r ? r.message || null : null;
    },
    hostTooltip(host) {
      const isp = this.hostIsp(host);
      const t = [this.hostInaccessibleText(host), isp ? "ISP: " + isp : ""];
      return t.filter((v) => !!v).join("\n") || null;
    },
    isHostFavorite(host) {
      return this.settings.hostsFavoriteListDnsNames.includes(host.dns_name);
    },
    hostUpgradeKey(host) {
      return UpgradeKeyForHost(this.entry, host);
    },
    hostUpgradeCardId(host) {
      return UpgradeCardDomId(this.hostUpgradeKey(host));
    },
    // "Not now": the card goes and the focus returns to the row that opened it
    // (index -1: the location, else the host with that index)
    onDismissUpgrade(hostIndex) {
      this.$emit("close-upgrade");
      this.$nextTick(() => {
        const btn =
          hostIndex < 0
            ? this.$refs.locMain
            : this.$el.querySelectorAll(".hostMain")[hostIndex];
        if (btn && btn.focus) btn.focus();
      });
    },
    onHostClick(host) {
      if (this.isHostLocked(host)) {
        this.$emit("toggle-upgrade", this.hostUpgradeKey(host));
        return;
      }
      this.$emit("select-host", this.entry, host);
    },
  },
};
</script>

<style scoped lang="scss">
// Geometry (R4F): the row is 292 px inside the list's 14 px side padding.
// Location: 1 px border | 2 px | 24 px chevron | flag at 27 px | ... | ping column
// ends 6 px before the 28 px star | 4 px | 1 px border.
// Host: 3 px | 24 px tree | flag at 27 px | ... | the same right edge (5 px padding).
// The chevron's button is 28 px wide (hit target): 2 px on each side overlap the
// padding and the start of the row button, the visible part stays 24 px.
.locItem {
  display: flex;
  flex-direction: column;
}

.locBox {
  box-sizing: border-box;
  border: 1px solid transparent;
  border-radius: 10px;
  transition: background-color 0.15s;
}
.locBox.selected {
  border-color: var(--accent-ring);
  background: var(--accent-tint);
}
.locBox.upgradeOpen {
  border-color: var(--accent-ring);
  background: var(--surface-color);
}
.locBox:not(.selected):not(.upgradeOpen):hover {
  background: var(--srv-row-hover, var(--surface-color));
}

.locRow {
  height: 42px;
  box-sizing: border-box;
  padding: 0 4px 0 2px;
  display: flex;
  align-items: center;
}

// the global 'html * { color }' rule stops currentColor from inheriting
svg,
svg * {
  color: inherit;
}

button {
  margin: 0;
  font-family: inherit;
}
button:focus {
  outline: none;
}

.chevronBtn {
  position: relative;
  width: 28px;
  height: 28px;
  flex: none;
  margin: 0 -2px;
  padding: 0;
  border: 0;
  border-radius: 6px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
// the visible (24 px) part of the button
.chevronBtn::before {
  content: "";
  position: absolute;
  inset: 0 2px;
  border-radius: 6px;
  background: transparent;
  transition: background-color 0.15s;
}
.chevronBtn svg {
  position: relative;
  display: block;
  stroke: var(--text-muted);
}
.chevronBtn.expanded svg {
  stroke: var(--text-soft);
}
.chevronBtn:hover::before {
  background: var(--neutral-tint);
}
.chevronBtn:hover svg {
  stroke: var(--text-color);
}
.chevronSpace {
  width: 24px;
  flex: none;
  display: block;
}

.locMain {
  flex: 1;
  min-width: 0;
  height: 42px;
  box-sizing: border-box;
  padding: 0 6px 0 0;
  border: 0;
  border-radius: 8px;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 10px;
  text-align: left;
  cursor: pointer;
}
.locTexts {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.locTitle {
  display: block;
  font-size: 13.5px;
  font-weight: 600;
  line-height: 18px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
// the chips fill this line ("fit": the crown of a Mixed row gives way when narrow)
.locSub {
  min-width: 0;
  height: 16px;
  display: flex;
  align-items: center;
  overflow: hidden;
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

.locMain.locked .locTitle {
  color: var(--text-muted);
}
.inaccessible {
  opacity: 0.5;
}

.starBtn {
  width: 28px;
  height: 28px;
  flex: none;
  padding: 0;
  border: 0;
  border-radius: 7px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.starBtn svg {
  display: block;
  fill: none;
  stroke: var(--text-faint);
}
.starBtn:hover {
  background: var(--neutral-tint);
}
.starBtn:hover svg {
  stroke: var(--text-soft);
}
.starBtn.fav svg,
.starBtn.fav:hover svg {
  fill: var(--accent-color);
  stroke: var(--accent-color);
}

.chevronBtn:focus-visible,
.starBtn:focus-visible,
.locMain:focus-visible,
.hostMain:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
.chevronBtn:focus-visible {
  outline-offset: -3px;
}

// ---------- hosts ----------
.hosts {
  display: flex;
  flex-direction: column;
}
.hostRow {
  height: 30px;
  box-sizing: border-box;
  padding: 0 5px 0 3px;
  display: flex;
  align-items: center;
  border-radius: 8px;
}
.hostRow:hover {
  background: var(--srv-row-hover, var(--surface-color));
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
.hostMain {
  flex: 1;
  min-width: 0;
  height: 30px;
  box-sizing: border-box;
  padding: 0 6px 0 0;
  border: 0;
  border-radius: 6px;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 8px;
  text-align: left;
  cursor: pointer;
}
.hostTexts {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  overflow: hidden;
}
.hostName {
  min-width: 0;
  display: flex;
  font-size: 12px;
  font-weight: 500;
  line-height: 16px;
  color: var(--text-soft);
  white-space: nowrap;
}
.hostNameHead {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}
.hostNameTail {
  flex: none;
}
// the global 'html * { color }' rule: the two parts take the name's colour and weight
.hostNameHead,
.hostNameTail {
  color: inherit;
  font-weight: inherit;
}
.hostMain.selected .hostName {
  font-weight: 600;
  color: var(--link-color);
}
.hostMain.locked .hostName {
  color: var(--text-faint);
}

.hostUpgrade {
  margin: 2px 0 6px 27px;
}
</style>
