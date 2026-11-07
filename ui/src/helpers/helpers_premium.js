// Free / Premium helpers for the OvpnPlus panel's server data.
//
// The panel sends "is_premium" on every host and on the location (true only
// when every host of the location is Premium), and a display "name" per host
// ("Dhaka District #1"). The account is Premium when its capabilities contain
// "premium". The VPN server itself refuses Premium hosts to Free accounts; the
// app only uses these helpers to show the right marks and to avoid picking a
// host the account cannot use.

export function IsHostPremium(host) {
  return host != null && host.is_premium === true;
}

// true when every host of the location is Premium (or the location says so)
export function IsServerPremium(server) {
  if (!server) return false;
  if (server.is_premium === true) return true;
  const hosts = server.hosts || [];
  return hosts.length > 0 && hosts.every((h) => IsHostPremium(h));
}

// true when the location has both Free and Premium hosts
export function IsServerMixed(server) {
  const hosts = (server && server.hosts) || [];
  const premium = hosts.filter((h) => IsHostPremium(h)).length;
  return premium > 0 && premium < hosts.length;
}

// "Free" | "Premium" | "Mixed"
export function ServerTier(server) {
  if (IsServerMixed(server)) return "Mixed";
  return IsServerPremium(server) ? "Premium" : "Free";
}

// hosts of the location that the account may use
export function UsableHosts(server, isPremiumAccount) {
  const hosts = (server && server.hosts) || [];
  if (isPremiumAccount) return hosts;
  return hosts.filter((h) => !IsHostPremium(h));
}

// a Free account cannot use a Premium host, nor a location whose hosts are all Premium
export function IsHostLocked(host, isPremiumAccount) {
  return !isPremiumAccount && IsHostPremium(host);
}
export function IsServerLocked(server, isPremiumAccount) {
  if (isPremiumAccount || !server) return false;
  return UsableHosts(server, false).length === 0;
}

// the id the app uses for a host: the part of its hostname before the first dot
export function HostId(host) {
  return host && host.hostname ? host.hostname.split(".")[0] : "";
}

// display name of a host; falls back to "<City> #n" (n counted from 1)
export function HostDisplayName(server, host) {
  if (host && host.name) return host.name;
  const hosts = (server && server.hosts) || [];
  const i = hosts.indexOf(host);
  const city = (server && server.city) || "Server";
  return hosts.length > 1 && i >= 0 ? `${city} #${i + 1}` : city;
}
