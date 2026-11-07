// Small helpers shared by the server list components (components/servers/*).
//
// A list "entry" is either a location (a server object with "hosts") or, in the
// Favorites list, a favourite host: a copy of its location with the host's
// fields on top plus "favHost" (the host) and "favHostParentServerObj" (the
// location). See the "settings/favoriteServersAndHosts" getter.

import {
  IsHostPremium,
  IsHostLocked,
  IsServerLocked,
  ServerTier,
  UsableHosts,
  HostId,
} from "@/helpers/helpers_premium";

// true when the account may use Premium servers. Until the account status is
// known nothing is locked (the store's "vpnState/isFreeAccount" rule); without
// that getter the "account/isPremiumAccount" getter decides.
export function IsPremiumAccountFor(getters) {
  if (!getters) return true;
  const free = getters["vpnState/isFreeAccount"];
  if (free === true) return false;
  if (free === false) return true;
  return getters["account/isPremiumAccount"] === true;
}

// "server-12.example.net" => "server-12" (favourites and exclusions use this id)
export function GatewayId(gateway) {
  if (!gateway) return "";
  return String(gateway).split(".")[0];
}

export function IsFavHostEntry(entry) {
  return !!(entry && entry.favHost);
}

// the location an entry belongs to
export function EntryLocation(entry) {
  if (IsFavHostEntry(entry)) return entry.favHostParentServerObj || entry;
  return entry;
}

// "Free" | "Premium" | "Mixed"
export function EntryTier(entry) {
  if (IsFavHostEntry(entry))
    return IsHostPremium(entry.favHost) ? "Premium" : "Free";
  return ServerTier(entry);
}

export function HostTier(host) {
  return IsHostPremium(host) ? "Premium" : "Free";
}

export function IsEntryLocked(entry, isPremiumAccount) {
  if (IsFavHostEntry(entry))
    return IsHostLocked(entry.favHost, isPremiumAccount);
  return IsServerLocked(entry, isPremiumAccount);
}

function positive(v) {
  return typeof v === "number" && v > 0 ? v : null;
}

// Latency (ms) of a host, or null when unknown or the host is locked.
export function HostPing(host, funcGetPing, isPremiumAccount) {
  if (!host || !funcGetPing) return null;
  if (IsHostLocked(host, isPremiumAccount)) return null;
  return positive(funcGetPing(host));
}

// Latency (ms) shown for a list entry, or null.
// A location shows its best host; for a Free account only the hosts it may use
// count (a Mixed location shows its best Free host, a locked one shows none).
export function EntryPing(entry, funcGetPing, isPremiumAccount) {
  if (!entry || !funcGetPing) return null;
  if (IsFavHostEntry(entry))
    return HostPing(entry.favHost, funcGetPing, isPremiumAccount);
  if (IsServerLocked(entry, isPremiumAccount)) return null;
  if (isPremiumAccount) return positive(funcGetPing(entry));

  let best = null;
  for (const h of UsableHosts(entry, false)) {
    const p = HostPing(h, funcGetPing, false);
    if (p != null && (best == null || p < best)) best = p;
  }
  return best;
}

// same thresholds as controls/control-server-ping.vue
export function PingQualityName(ms) {
  if (ms == null) return null;
  if (ms < 100) return "good";
  if (ms < 300) return "moderate";
  return "bad";
}

export function PingText(ms) {
  if (ms == null) return "";
  return Math.max(1, Math.round(ms)) + " ms";
}

// key of the inline upgrade card (one at a time)
export function UpgradeKeyForEntry(entry) {
  if (IsFavHostEntry(entry))
    return "H:" + GatewayId(EntryLocation(entry).gateway) + ":" + HostId(entry.favHost);
  return "L:" + (entry ? entry.gateway : "");
}
export function UpgradeKeyForHost(server, host) {
  return "H:" + GatewayId(server ? server.gateway : "") + ":" + HostId(host);
}

// DOM id of the upgrade card opened by the row with this key
export function UpgradeCardDomId(key) {
  return "srvUp-" + String(key).replace(/[^A-Za-z0-9_-]/g, "_");
}
