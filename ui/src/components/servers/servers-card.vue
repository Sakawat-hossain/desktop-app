<template>
  <div
    class="srvCard"
    :class="{ selected: isCardSelected, tinted: isLine && isCardSelected }"
    role="group"
    :aria-label="groupLabel"
  >
    <!-- A card of the server list: one country (Country sort), one location
         (other sorts) or one favourite. A one-line card is its 40 px row only;
         a country card has a 40 px header and, when open, its city rows. -->
    <div class="head" :class="{ open: isBodyShown || isHeadUpgradeOpen }">
      <span v-if="isBodyShown" class="headStem" aria-hidden="true"></span>
      <button
        ref="headMain"
        type="button"
        class="headMain"
        :class="{ locked: isHeadLocked, inaccessible: isHeadInaccessible }"
        :aria-current="
          isCardSelected && (isLine || !isBodyShown)
            ? isFavHost
              ? 'true'
              : 'location'
            : null
        "
        :aria-label="headLabel"
        :aria-expanded="
          isHeadLocked ? (isHeadUpgradeOpen ? 'true' : 'false') : null
        "
        :aria-controls="isHeadUpgradeOpen ? headUpgradeCardId : null"
        :title="headTooltip"
        v-on:click="onHeadClick"
      >
        <ServerFlag :countryCode="countryCode" :dim="isHeadLocked" />
        <span
          ref="headTexts"
          class="headTexts"
          :class="{ nameWrap: isNameWrapped }"
        >
          <!-- the country, or the country and the city; a city that does not
               fit here moves to the second line -->
          <span ref="line1" class="line1">
            <!-- a country wider than the line steps down to 12, then 11 px;
                 one still too wide takes both lines (12, then 11 px) -->
            <span ref="country" class="country" :class="countryClass">{{
              card.country
            }}</span>
            <span
              v-if="lineCity && !isNameWrapped"
              ref="cityGroup"
              class="cityGroup"
              :style="{ visibility: isCityOnLine2 ? 'hidden' : null }"
              ><span class="cityDot" aria-hidden="true">&middot;</span
              ><span class="lineCity">{{ lineCity }}</span></span
            >
            <!-- a name on both lines: on its second line, each whole or not
                 at all, a favourite host's name (or the card's city), then
                 the tier chips, whose Premium word gives way to the crown
                 first -->
            <template v-if="isNameWrapped && !isCountryCut">
              <span
                v-if="nameExtraText && !isNameExtraOut"
                ref="nameExtra"
                class="nameExtra"
                ><span class="l2Dot" aria-hidden="true">&middot;</span
                >{{ nameExtraText }}</span
              >
              <ServerChips
                ref="nameChips"
                class="nameChips"
                :tier="headTier"
                :premiumTitle="premiumTitle"
                :shrinkWord="isNameChipsShrunk"
              />
            </template>
          </span>
          <template v-if="!isNameWrapped">
            <!-- a favourite host whose city moved here: items right to left by
                 importance (the city, the host's name, the tier chip), each
                 whole or not at all, so favourite hosts of different cities
                 differ -->
            <span v-if="isFavHost && isCityOnLine2" class="line2 l2Rev">
              <span class="l2Keep"></span>
              <span class="l2Text l2Place"
                ><span class="l2Dot" aria-hidden="true">&middot;</span
                >{{ lineCity }}</span
              >
              <span class="l2Text l2Host">{{ line2Text }}</span>
              <ServerChips
                :tier="headTier"
                :premiumTitle="premiumTitle"
                shrinkWord
              />
            </span>
            <!-- tier chips, then each whole or not at all: a one-line
                 location: the city when it moved here, the server count, the
                 ISP (setting); a favourite host: its name; a country card
                 naming its city: the city when it moved here -->
            <span v-else class="line2">
              <!-- with the city here the Premium word gives way to the crown first -->
              <ServerChips
                :tier="headTier"
                :premiumTitle="premiumTitle"
                :shrinkWord="isCityOnLine2"
              />
              <template v-if="isFavHost">
                <span class="l2Text l2Host">{{ line2Text }}</span>
              </template>
              <template v-else-if="isLine">
                <span v-if="isCityOnLine2" class="l2Text l2Place">{{
                  lineCity
                }}</span>
                <span class="l2Text"
                  ><span v-if="isCityOnLine2" class="l2Dot" aria-hidden="true"
                    >&middot;</span
                  >{{ line2Text }}</span
                >
                <span v-if="ispText" class="l2Text l2Isp"
                  ><span class="l2Dot" aria-hidden="true">&middot;</span
                  >{{ ispText }}</span
                >
              </template>
              <span
                v-else-if="isCityOnLine2"
                ref="l2City"
                class="l2Text l2Place"
                >{{ lineCity }}</span
              >
            </span>
          </template>
        </span>
        <ServerPing :ms="headPing" :locked="isHeadLocked" :hint="pingHint" />
      </button>
      <StarBtn
        :pressed="isHeadFavorite"
        :label="headFavoriteLabel"
        v-on:click="onHeadFavorite"
      />
      <ChevronBtn
        v-if="!isLine"
        :expanded="isOpen"
        :label="(isOpen ? 'Hide cities in ' : 'Show cities in ') + card.country"
        v-on:click="$emit('toggle-card', card)"
      />
      <span v-else class="slot" aria-hidden="true"></span>
    </div>

    <UpgradeCard
      v-if="isHeadUpgradeOpen"
      :cardId="headUpgradeCardId"
      :name="headUpgradeName"
      :indent="isBodyShown ? 38 : 9"
      :lines="isBodyShown ? [19] : []"
      v-on:dismiss="onDismissHeadUpgrade"
    />

    <template v-if="isBodyShown">
      <CityRow
        v-for="(loc, i) of card.locations"
        :key="loc.gateway"
        :location="loc"
        :isExitServer="isExitServer"
        :isPremiumAccount="isPremiumAccount"
        :funcGetPing="funcGetPing"
        :showTier="card.locations.length > 1"
        :sameAsHeader="
          card.locations.length === 1 &&
          (cityEqualsCountry(loc) || isHeadCityShown)
        "
        :isLast="i === card.locations.length - 1"
        :hostsEnabled="hostsEnabled"
        :isHostsOpen="openGateways.includes(loc.gateway)"
        :isSelected="gatewayId(loc) === markedGateway"
        :selectedHostId="chosenHostId"
        :upgradeKey="upgradeKey"
        v-on:select="(s) => $emit('select', s)"
        v-on:select-host="(s, h) => $emit('select-host', s, h)"
        v-on:toggle-hosts="(s) => $emit('toggle-hosts', s)"
        v-on:favorite="(e, s, h) => $emit('favorite', e, s, h)"
        v-on:toggle-upgrade="(k) => $emit('toggle-upgrade', k)"
        v-on:close-upgrade="$emit('close-upgrade')"
      />
    </template>
  </div>
</template>

<script>
import ServerFlag from "@/components/servers/servers-flag.vue";
import ServerChips from "@/components/servers/servers-chips.vue";
import ServerPing from "@/components/servers/servers-ping.vue";
import StarBtn from "@/components/servers/servers-star-btn.vue";
import ChevronBtn from "@/components/servers/servers-chevron-btn.vue";
import UpgradeCard from "@/components/servers/servers-upgrade-card.vue";
import CityRow from "@/components/servers/servers-city-row.vue";
import { HostId, HostShortName } from "@/helpers/helpers_premium";
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
  IsEntryLocked,
  EntryPing,
  BestPing,
  CountryName,
  CombinedTier,
  TierText,
  ServersCountText,
  PingText,
  UpgradeKeyForEntry,
  UpgradeKeyForCard,
  UpgradeCardDomId,
  IsPremiumAccountFor,
} from "@/components/servers/servers-helpers";

export default {
  components: {
    ServerFlag,
    ServerChips,
    ServerPing,
    StarBtn,
    ChevronBtn,
    UpgradeCard,
    CityRow,
  },
  emits: [
    "select",
    "select-host",
    "toggle-card",
    "toggle-hosts",
    "favorite",
    "favorite-many",
    "toggle-upgrade",
    "close-upgrade",
  ],
  props: {
    // { key, kind: "country" | "location" | "favorite", country, lineCity, locations,
    //   countryLocations }
    // (lineCity: the city of a one-location card, named after the country when
    // the country has other locations, or ""; countryLocations: a country
    // card: the number of locations of its country in the whole server list)
    card: { type: Object, required: true },
    isExitServer: [String, Boolean],
    // the host rows may be shown (the "show hosts" setting, All servers list)
    hostsEnabled: Boolean,
    // the country card is open (its city rows are shown)
    isOpen: Boolean,
    // gateways of the locations whose hosts are shown
    openGateways: { type: Array, default: () => [] },
    // gateway id of the selected / connected location, and the host the user chose
    markedGateway: String,
    chosenHostId: String,
    // key of the open upgrade card in the list (one at a time)
    upgradeKey: String,
  },
  data: () => ({
    // the city named after the country does not fit after it
    isCityOnLine2: false,
    // ... and (a country card) has no room on the second line either
    isLine2CityHidden: false,
    // a country name wider than the first line: 0 = 13.5 px, 1 = 12, 2 = 11;
    // wider still: on both lines (the second line's items left out, but see
    // checkNameLine2), 3 = 12 px, 4 = 11
    countryStep: 0,
    // ... and more than two lines even at 11 px (an ellipsis; the name is in
    // the tooltip)
    isCountryCut: false,
    // a name on both lines: at 11 px (step 4) only to give the item after it
    // room; that item does not fit its second line even so; and (then) the
    // tier chips did not fit there with their words
    isExtraStep: false,
    isNameExtraOut: false,
    isNameChipsShrunk: false,
  }),
  computed: {
    isPremiumAccount() {
      return IsPremiumAccountFor(this.$store.getters);
    },
    funcGetPing() {
      return this.$store.getters["vpnState/funcGetPing"];
    },
    settings() {
      return this.$store.state.settings;
    },
    locations() {
      return this.card.locations || [];
    },
    // the entry of a one-entry card (a location or a favourite host)
    entry() {
      return this.locations[0] || null;
    },
    isFavHost() {
      return this.card.kind === "favorite" && IsFavHostEntry(this.entry);
    },
    // one-line card: a favourite, or a single location with nothing to open
    isLine() {
      if (this.card.kind === "favorite") return true;
      if (this.locations.length !== 1) return false;
      const hosts = this.entry.hosts || [];
      return !(this.hostsEnabled && hosts.length >= 2);
    },
    isBodyShown() {
      return !this.isLine && this.isOpen;
    },
    // the city named after the country on the first line, which the card's
    // actions apply to: a card with one location whose country has others
    // (another sort, a search that left one city, a favourite)
    placeCity() {
      return this.locations.length === 1 ? this.card.lineCity || "" : "";
    },
    lineCity() {
      return this.placeCity;
    },
    // the header shows that city (on the first line, or on the second with
    // room for it), so the city row under it need not repeat it
    isHeadCityShown() {
      if (!this.lineCity) return false;
      // a name on both lines: the city follows it when it fits there
      if (this.isNameWrapped)
        return !this.isFavHost && !this.isCountryCut && !this.isNameExtraOut;
      return !this.isCityOnLine2 || !this.isLine2CityHidden;
    },
    // the country name on both lines (see countryStep)
    isNameWrapped() {
      return this.countryStep >= 3;
    },
    // ... the item after it: a favourite host's name, else the city named
    // after the country (so cards of that country still differ)
    nameExtraText() {
      return this.isFavHost ? this.line2Text : this.lineCity;
    },
    countryClass() {
      return {
        fs12: this.countryStep === 1 || this.countryStep === 3,
        fs11: this.countryStep === 2 || this.countryStep === 4,
        clamp: this.isNameWrapped && this.isCountryCut,
      };
    },
    // a country card that shows only some of its country's locations (a
    // search): "Tokyo and Kyoto", else ""
    shownCities() {
      if (this.isLine || this.locations.length < 2) return "";
      const total = this.card.countryLocations || 0;
      if (total <= this.locations.length) return "";
      const cities = this.locations.map((l) => {
        const loc = EntryLocation(l);
        return String((loc && loc.city) || "").trim() || CountryName(l);
      });
      return (
        cities.slice(0, -1).join(", ") + " and " + cities[cities.length - 1]
      );
    },
    countryCode() {
      const loc = EntryLocation(this.entry);
      return loc ? loc.country_code : "";
    },
    groupLabel() {
      return this.placeCity
        ? `${this.card.country}, ${this.placeCity}`
        : this.card.country;
    },

    headTier() {
      return this.isLine ? EntryTier(this.entry) : CombinedTier(this.locations);
    },
    premiumTitle() {
      if (this.headTier !== "Mixed") return null;
      return `${this.placeCity || this.card.country} also has Premium servers`;
    },
    // a one-line card: its entry is locked; a country card: all its locations are
    isHeadLocked() {
      if (this.isLine) return IsEntryLocked(this.entry, this.isPremiumAccount);
      return this.locations.every((l) =>
        IsEntryLocked(l, this.isPremiumAccount),
      );
    },
    // the lowest latency of the card (a Free account: of the hosts it may use)
    headPing() {
      if (this.isLine)
        return EntryPing(this.entry, this.funcGetPing, this.isPremiumAccount);
      return BestPing(this.locations, this.funcGetPing, this.isPremiumAccount);
    },
    pingHint() {
      if (this.isPremiumAccount || this.isFavHost || this.isHeadLocked)
        return null;
      if (this.locations.some((l) => EntryTier(l) !== "Free"))
        return "Best ping among the Free servers you can use";
      return null;
    },
    hostCount() {
      if (this.isFavHost) return 1;
      return this.locations.reduce(
        (n, l) => n + ((l.hosts && l.hosts.length) || 0),
        0,
      );
    },
    // second line of a one-line card: "N servers", or the favourite host's name
    line2Text() {
      if (this.isFavHost)
        return HostShortName(EntryLocation(this.entry), this.entry.favHost);
      return ServersCountText(this.hostCount);
    },
    headLabel() {
      const t = [this.card.country];
      if (this.isLine) {
        const loc = EntryLocation(this.entry);
        if (this.isFavHost) {
          t.push(loc.city || "");
          t.push(this.line2Text);
        } else if (this.lineCity) t.push(this.lineCity);
        t.push(TierText(this.headTier));
        if (!this.isFavHost) t.push(this.line2Text);
        if (this.isHeadLocked) t.push("locked");
        else if (this.headPing != null) t.push(PingText(this.headPing));
      } else {
        t.push(this.placeCity);
        t.push(TierText(this.headTier));
        if (this.isHeadLocked) t.push("locked");
        else if (this.headPing != null)
          t.push("fastest server " + PingText(this.headPing));
      }
      return t.filter((v) => !!v).join(", ");
    },
    // ISP of a one-line location card (the "show ISP" setting): one ISP only
    ispText() {
      if (!this.isLine || this.isFavHost) return "";
      if (this.settings.showISPInfo !== true) return "";
      const isps = GetSreverISPs(this.entry);
      return isps.length === 1 ? isps[0] : "";
    },

    inaccessibleTexts() {
      return this.locations.map((l) => {
        const loc = EntryLocation(l);
        const host = IsFavHostEntry(l) ? l.favHost : null;
        const r = CheckIsInaccessibleServer(this.isExitServer, loc, host);
        return r ? r.message || "" : null;
      });
    },
    // multi-hop: the entry (all the locations of a country card) cannot be used here
    isHeadInaccessible() {
      return (
        this.inaccessibleTexts.length > 0 &&
        this.inaccessibleTexts.every((t) => t !== null)
      );
    },
    headTooltip() {
      const t = [];
      const place = this.lineCity
        ? `${this.lineCity}, ${this.card.country}`
        : this.card.country;
      const tier = TierText(this.headTier);
      if (this.isNameWrapped) {
        // the name on both lines: the second line's items (and the tier chips
        // when they did not fit) are left out
        if (this.isFavHost) t.push(`${this.line2Text} in ${place} (${tier})`);
        else if (this.isLine) t.push(`${place} (${tier}, ${this.line2Text})`);
        else t.push(`${place} (${tier})`);
      } else if (this.isCityOnLine2) {
        // the city left the first line (it may not fit the second one either);
        // a favourite host's tier chip may give way there too
        t.push(
          this.isFavHost ? `${this.line2Text} in ${place} (${tier})` : place,
        );
      }
      if (this.isHeadInaccessible) t.push(this.inaccessibleTexts[0]);
      if (this.isLine) {
        const loc = EntryLocation(this.entry);
        const s = this.settings;
        if (
          s.enableIPv6InTunnel === true &&
          s.showGatewaysWithoutIPv6 === true &&
          IsServerSupportIPv6(loc) === true
        )
          t.push("IPv6 supported");
        if (s.showISPInfo === true) {
          const isp = this.isFavHost
            ? this.entry.favHost.isp || ""
            : this.ispText;
          if (isp) t.push("ISP: " + isp);
        }
      }
      return t.filter((v) => !!v).join("\n") || null;
    },

    // the card holds the selected / connected location (or is the chosen favourite host)
    isCardSelected() {
      if (!this.markedGateway) return false;
      if (this.isFavHost) {
        const loc = EntryLocation(this.entry);
        return (
          GatewayId(loc.gateway) === this.markedGateway &&
          !!this.chosenHostId &&
          HostId(this.entry.favHost) === this.chosenHostId
        );
      }
      return this.locations.some(
        (l) => GatewayId(l.gateway) === this.markedGateway,
      );
    },

    // favourite: the entry; a country card: its location, or all its locations
    // (shown as a favourite when all of them are)
    isHeadFavorite() {
      if (this.isFavHost)
        return this.settings.hostsFavoriteListDnsNames.includes(
          this.entry.favHost.dns_name,
        );
      const favs = this.settings.serversFavoriteList;
      return (
        this.locations.length > 0 &&
        this.locations.every((l) => favs.includes(GatewayId(l.gateway)))
      );
    },
    headFavoriteLabel() {
      let name = this.card.country;
      if (this.isFavHost) {
        const loc = EntryLocation(this.entry);
        name = loc.city ? `${this.line2Text} in ${loc.city}` : this.line2Text;
      } else if (this.placeCity)
        name = `${this.placeCity}, ${this.card.country}`;
      else if (this.shownCities)
        name = `${this.shownCities} in ${this.card.country}`;
      return this.isHeadFavorite
        ? `Remove ${name} from favorites`
        : `Add ${name} to favorites`;
    },

    headUpgradeKey() {
      return this.isLine
        ? UpgradeKeyForEntry(this.entry)
        : UpgradeKeyForCard(this.card.key);
    },
    isHeadUpgradeOpen() {
      return this.isHeadLocked && this.upgradeKey === this.headUpgradeKey;
    },
    headUpgradeCardId() {
      return UpgradeCardDomId(this.headUpgradeKey);
    },
    headUpgradeName() {
      if (this.isFavHost) {
        const loc = EntryLocation(this.entry);
        return loc.city ? `${this.line2Text} in ${loc.city}` : this.line2Text;
      }
      return this.placeCity || this.card.country;
    },
  },
  watch: {
    lineCity() {
      this.$nextTick(this.watchCityFit);
    },
    "card.country"() {
      this.$nextTick(this.refitLine1);
    },
    // a name on both lines: what follows it changed, measure it again
    nameExtraText() {
      if (this.isNameWrapped) this.$nextTick(this.refitLine1);
    },
    headTier() {
      if (this.isNameWrapped) this.$nextTick(this.refitLine1);
    },
  },
  mounted() {
    this.watchCityFit();
  },
  beforeUnmount() {
    if (this.fitObserver) this.fitObserver.disconnect();
    this.fitObserver = null;
  },
  methods: {
    gatewayId(loc) {
      return GatewayId(loc.gateway);
    },
    // "Hong Kong" in "Hong Kong": the header already names the city
    cityEqualsCountry(loc) {
      const city = String((loc && loc.city) || "")
        .trim()
        .toLowerCase();
      return !!city && city === CountryName(loc).toLowerCase();
    },

    // the best location of a country card: the usable one with the lowest
    // latency (those multi-hop allows first), else the first usable one
    bestLocation() {
      const usable = this.locations.filter(
        (l) => !IsEntryLocked(l, this.isPremiumAccount),
      );
      const accessible = usable.filter(
        (l) => this.inaccessibleTexts[this.locations.indexOf(l)] === null,
      );
      const pool = accessible.length ? accessible : usable;
      let best = null;
      let bestPing = null;
      for (const l of pool) {
        const p = EntryPing(l, this.funcGetPing, this.isPremiumAccount);
        if (p != null && (bestPing == null || p < bestPing)) {
          best = l;
          bestPing = p;
        }
      }
      return best || pool[0] || null;
    },
    onHeadClick() {
      if (this.isLine) {
        if (this.isHeadLocked)
          this.$emit("toggle-upgrade", this.headUpgradeKey);
        else this.$emit("select", this.entry);
        return;
      }
      const best = this.bestLocation();
      if (best) this.$emit("select", best);
      else this.$emit("toggle-upgrade", this.headUpgradeKey);
    },
    onHeadFavorite(evt) {
      if (this.isLine || this.locations.length === 1)
        this.$emit("favorite", evt, this.entry);
      else this.$emit("favorite-many", evt, this.locations);
    },
    // "Not now": the card goes and the focus returns to the row that opened it
    onDismissHeadUpgrade() {
      this.$emit("close-upgrade");
      this.$nextTick(() => {
        if (this.$refs.headMain) this.$refs.headMain.focus();
      });
    },

    // watch whether the first line fits: the country name, then (a card
    // naming its city after the country) the city
    watchCityFit() {
      const box = this.$refs.headTexts;
      if (box && !this.fitObserver && typeof ResizeObserver !== "undefined") {
        // the texts' box, whose size the steps below never change (its height
        // is fixed; a name on both lines makes only the first line taller), so
        // re-fitting inside the callback cannot start a resize loop
        this.fitObserver = new ResizeObserver((entries) => {
          const e = entries[entries.length - 1];
          const w = e ? e.contentRect.width : null;
          if (w === this.textsWidth) return;
          this.textsWidth = w;
          this.refitLine1();
        });
        this.fitObserver.observe(box);
      }
      this.refitLine1();
    },
    // the line's width changed (or its country): measure again from the
    // country's own size (the steps below do not change the line's width)
    refitLine1() {
      this.isNameExtraOut = false;
      this.isNameChipsShrunk = false;
      this.isExtraStep = false;
      if (this.countryStep === 0 && !this.isCountryCut) {
        this.checkCityFit();
        return;
      }
      this.countryStep = 0;
      this.isCountryCut = false;
      this.$nextTick(this.checkCityFit);
    },
    checkCityFit() {
      const l1 = this.$refs.line1;
      const c = this.$refs.country;
      // a country wider than the line (on both lines: needing a third one):
      // one step on, then measure again
      if (l1 && c && !this.isCountryCut) {
        const over = this.isNameWrapped
          ? c.getClientRects().length > 2
          : c.scrollWidth > l1.clientWidth + 0.5;
        if (over) {
          if (this.countryStep < 4) {
            this.countryStep++;
            this.$nextTick(this.checkCityFit);
            return;
          }
          this.isCountryCut = true;
        }
      }
      // the city wrapped to the (hidden) second line of the first line box
      const g = this.$refs.cityGroup;
      let wrapped = false;
      if (g && c)
        wrapped =
          g.getBoundingClientRect().top > c.getBoundingClientRect().top + 1;
      if (wrapped !== this.isCityOnLine2) this.isCityOnLine2 = wrapped;
      this.$nextTick(this.checkLine2City);
    },
    // a country card's city that moved to the second line: whether it has
    // room there (else it wrapped to that line's hidden second row)
    checkLine2City() {
      const e = this.$refs.l2City;
      let hidden = false;
      if (e && e.parentElement)
        hidden =
          e.getBoundingClientRect().top >=
          e.parentElement.getBoundingClientRect().bottom - 0.5;
      if (hidden !== this.isLine2CityHidden) this.isLine2CityHidden = hidden;
      if (this.isNameWrapped) this.checkNameLine2();
    },
    // a name on both lines: an item after it that does not fit its second
    // line wraps to the hidden third one. The host's name (or city) first
    // makes room with the name at 11 px; with none even then it is left out
    // (the name back at 12 px), which may give the chips room; chips that
    // still do not fit show the crown for the Premium word (else they stay
    // left out whole).
    checkNameLine2() {
      const l1 = this.$refs.line1;
      if (!l1 || !this.isNameWrapped || this.isCountryCut) return;
      const end = l1.getBoundingClientRect().bottom - 0.5;
      const isOut = (el) => !!el && el.getBoundingClientRect().top >= end;
      if (isOut(this.$refs.nameExtra)) {
        if (this.countryStep === 3) {
          this.countryStep = 4;
          this.isExtraStep = true;
        } else {
          if (this.isExtraStep) this.countryStep = 3;
          this.isExtraStep = false;
          this.isNameExtraOut = true;
        }
        this.$nextTick(this.checkNameLine2);
        return;
      }
      const chips = this.$refs.nameChips;
      if (!this.isNameChipsShrunk && isOut(chips && chips.$el))
        this.isNameChipsShrunk = true;
    },
  },
};
</script>

<style scoped lang="scss">
// R6B card (292 px in the list's 14 px side padding), 1 px border, radius 12.
// Header / one-line row (40 px): button (9 px | 21 px flag | 8 | texts | 8 |
// latency | 2 px) | 28 px star | 24 px chevron column. The latency column thus
// ends 54 px before the inner right edge in every row of the list.
.srvCard {
  flex: none;
  box-sizing: border-box;
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  background: var(--surface-color);
  display: flex;
  flex-direction: column;
  transition:
    background-color 0.15s,
    border-color 0.15s;
}
.srvCard.selected {
  border-color: var(--accent-ring);
}
.srvCard.tinted {
  background: var(--accent-tint);
}

.head {
  position: relative;
  height: 40px;
  flex: none;
  border-radius: 11px;
  display: flex;
  align-items: center;
  transition: background-color 0.15s;
}
.head.open {
  border-radius: 11px 11px 0 0;
}
// not while the star or the chevron is hovered: their own box shows then
.srvCard:not(.tinted) .head:not(:has(.starBtn:hover, .chevronBtn:hover)):hover {
  background: var(--neutral-tint);
}
// the tree line from the flag down to the city rows
.headStem {
  position: absolute;
  left: 19px;
  top: 29px;
  width: 1px;
  height: 11px;
  display: block;
  background: var(--srv-tree-line, #d4d4d8);
}

button {
  margin: 0;
  font-family: inherit;
}
button:focus {
  outline: none;
}

.headMain {
  flex: 1;
  min-width: 0;
  height: 40px;
  box-sizing: border-box;
  padding: 0 2px 0 9px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 8px;
  text-align: left;
  cursor: pointer;
}
.headMain:focus-visible {
  outline: 2px solid var(--accent-color);
  outline-offset: -2px;
}
.inaccessible {
  opacity: 0.5;
}

// a fixed height (the two lines, 18 + 2 + 16; a name on both lines, 32, sits
// in its middle): the box the fitting code watches never resizes itself
.headTexts {
  flex: 1;
  min-width: 0;
  height: 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
}
// one line: an item that does not fit wraps to the hidden second line
.line1 {
  height: 18px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  column-gap: 5px;
  overflow: hidden;
}
.country {
  flex: 0 1 auto;
  min-width: 0;
  display: block;
  font-size: 13.5px;
  font-weight: 600;
  line-height: 18px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.country.fs12 {
  font-size: 12px;
}
.country.fs11 {
  font-size: 11px;
}
// a name too wide for one line even at 11 px takes both lines (2 x 16 px, the
// second line's items left out); the tier chips follow it when they fit on
// its second line, else they wrap to the hidden third one. More than two
// lines even at 11 px end in an ellipsis (the tooltip has the name).
.headTexts.nameWrap .line1 {
  display: block;
  height: 32px;
  line-height: 16px;
  overflow: hidden;
}
// (top-aligned: at 11 px a baseline-aligned name made each line box 17 px
// tall, so its second line ended a pixel below the clip)
.headTexts.nameWrap .country {
  display: inline;
  vertical-align: top;
  line-height: 16px;
  white-space: normal;
  overflow-wrap: anywhere;
}
.headTexts.nameWrap .country.clamp {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}
.line1 .nameChips {
  display: inline-flex;
  vertical-align: top;
  margin-left: 5px;
}
// a favourite host's name or the city after a name on both lines (as on the
// second line: 11 px, 500, soft)
.line1 .nameExtra {
  display: inline-flex;
  vertical-align: top;
  gap: 4px;
  margin-left: 5px;
  font-size: 11px;
  font-weight: 500;
  line-height: 16px;
  color: var(--text-soft);
  white-space: nowrap;
}
.cityGroup {
  flex: none;
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
}
.cityDot {
  font-size: 13px;
  line-height: 18px;
  color: var(--text-faint);
}
.lineCity {
  font-size: 13.5px;
  font-weight: 500;
  line-height: 18px;
  color: var(--text-soft);
}
.headMain.locked .country,
.headMain.locked .lineCity {
  color: var(--text-muted);
}

.line2 {
  height: 16px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  column-gap: 4px;
  overflow: hidden;
}
.l2Text {
  flex: none;
  display: flex;
  gap: 4px;
  font-size: 11px;
  line-height: 16px;
  color: var(--text-muted);
  white-space: nowrap;
}
// the city (moved from the first line) and a favourite host's name
.l2Text.l2Place,
.l2Text.l2Host {
  font-weight: 500;
  color: var(--text-soft);
}
.l2Dot {
  color: var(--text-faint);
}
.l2Text.l2Isp {
  color: var(--text-faint);
}
// right-to-left placement packed to the left (as the city rows' meta): the
// first item is 0 wide, so even the city is shown whole or not at all
.line2.l2Rev {
  flex-direction: row-reverse;
  justify-content: flex-end;
}
.l2Keep {
  flex: none;
  width: 0;
  height: 16px;
}

.slot {
  width: 24px;
  flex: none;
  display: block;
}
</style>
