// Tunnel speed helpers. Pure functions: the store and the UI both use them.

const TRAFFIC_HISTORY_LEN = 60;

export function newTrafficState() {
  return { rxBps: 0, txBps: 0, sessionRx: 0, sessionTx: 0, history: [], last: null };
}

// nextTrafficState turns two byte-counter samples ({rx, tx, time}) into a speed.
// The counters are totals since the OpenVPN process started; when they go
// down a new tunnel has started, so the sample becomes the new baseline.
export function nextTrafficState(prev, sample) {
  if (!sample || !Number.isFinite(sample.rx) || !Number.isFinite(sample.tx))
    return prev;
  const last = prev.last;
  if (!last || sample.rx < last.rx || sample.tx < last.tx) {
    return { ...newTrafficState(), sessionRx: sample.rx, sessionTx: sample.tx, last: sample };
  }
  const seconds = (sample.time - last.time) / 1000;
  if (seconds <= 0) return prev;
  const rxBps = (sample.rx - last.rx) / seconds;
  const txBps = (sample.tx - last.tx) / seconds;
  const history = prev.history
    .concat([{ rx: rxBps, tx: txBps }])
    .slice(-TRAFFIC_HISTORY_LEN);
  return { rxBps, txBps, sessionRx: sample.rx, sessionTx: sample.tx, history, last: sample };
}

// formatSpeed: bytes per second -> { value: "12.4", unit: "Mb/s" } (bits, like speed tests)
export function formatSpeed(bytesPerSec) {
  let bits = Math.max(0, Number(bytesPerSec) || 0) * 8;
  const units = ["b/s", "Kb/s", "Mb/s", "Gb/s"];
  let i = 0;
  while (bits >= 1000 && i < units.length - 1) {
    bits /= 1000;
    i++;
  }
  const value = bits >= 100 || i === 0 ? Math.round(bits).toString() : bits.toFixed(1);
  return { value, unit: units[i] };
}

// formatBytes: 1234567890 -> "1.2 GB"
export function formatBytes(bytes) {
  let v = Math.max(0, Number(bytes) || 0);
  const units = ["B", "KB", "MB", "GB", "TB"];
  let i = 0;
  while (v >= 1000 && i < units.length - 1) {
    v /= 1000;
    i++;
  }
  return (v >= 100 || i === 0 ? Math.round(v) : v.toFixed(1)) + " " + units[i];
}

// sparklinePoints: history -> SVG polyline points for a w x h box (newest on the right)
export function sparklinePoints(history, key, w, h, maxValue) {
  if (!history || history.length < 2) return "";
  const max = maxValue > 0 ? maxValue : 1;
  const step = w / (TRAFFIC_HISTORY_LEN - 1);
  const start = w - step * (history.length - 1);
  return history
    .map((s, i) => {
      const x = start + i * step;
      const y = h - 2 - (Math.min(s[key], max) / max) * (h - 6);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}
