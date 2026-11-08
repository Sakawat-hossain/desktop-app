// Geometry of the world map drawn by the map view (components/map/map-world.vue).
//
// The outlines come from the app's own world map (src/assets/world_map_dark.svg;
// world_map_light.svg has the same outlines, only other colours). Each <path> is
// one country. The paths are drawn inline, so a country can be styled (the
// country of the connected server is filled), and the point lookups below find
// the country under a map point.
//
// Map units: the coordinate space of the SVG (MAP_WIDTH x MAP_HEIGHT), the same
// space helpers.getCoordinatesBy() projects longitude/latitude into.

import worldMapSvg from "@/assets/world_map_dark.svg?raw";
import { getCoordinatesBy } from "@/helpers/helpers";

function readSize(attr, fallback) {
  const m = new RegExp(`<svg[^>]*\\s${attr}="([\\d.]+)"`).exec(worldMapSvg);
  const v = m ? parseFloat(m[1]) : NaN;
  return v > 0 ? v : fallback;
}

export const MAP_WIDTH = readSize("width", 11300);
export const MAP_HEIGHT = readSize("height", 8249);

// the "d" attribute of every country path, in file order (176 paths)
export const MAP_PATHS = Object.freeze(
  Array.from(worldMapSvg.matchAll(/<path\b[^>]*?\sd="([^"]+)"/g), (m) => m[1]),
);

// The graticule, drawn faintly under the land (map-world.vue): a meridian every 10
// degrees of longitude across the whole map, and a parallel every 10 degrees of
// latitude from 80 S to 80 N. One path, in map units.
export const GRATICULE_PATH = (() => {
  const f = (v) => Math.round(v * 10) / 10;
  let d = "";
  // the map runs from about 170 W to 170 W again (190 E): every meridian on it
  for (let lon = -180; lon <= 190; lon += 10) {
    const x = getCoordinatesBy(lon, 0, MAP_WIDTH, MAP_HEIGHT).x;
    if (x >= 0 && x <= MAP_WIDTH) d += `M${f(x)} 0V${f(MAP_HEIGHT)}`;
  }
  for (let lat = -80; lat <= 80; lat += 10) {
    const y = getCoordinatesBy(0, lat, MAP_WIDTH, MAP_HEIGHT).y;
    if (y >= 0 && y <= MAP_HEIGHT) d += `M0 ${f(y)}H${f(MAP_WIDTH)}`;
  }
  return d;
})();

// ---------------------------------------------------------------------------
// The user's own location marker (map-marker.vue, kind "user"), in px around its map
// point (the tip of the pin): the map view (Component-Map.vue) places the label card
// and keeps the room the marker takes with these.
export const USER_PIN = Object.freeze({
  // centre of the pin head: the stem and the middle of the card are on this line
  headY: -16.5,
  // top of the pin (22 x 28, its tip on the point)
  top: -27,
  // half the width / height of the widest ripple (the one that breathes while connecting)
  ringRx: 34,
  ringRy: 13,
  // the card starts this far right of the point (or ends this far left of it, flipped);
  // the stem runs from the pin head to it
  cardGap: 24,
  // the card can slide up or down (to stay in view) while the stem stays this far
  // inside its top and bottom edges
  stemInset: 14,
});

// ---------------------------------------------------------------------------
// The line from the user's location 'u' to the server 's' ({ x, y }, any one unit):
// a quadratic curve bent to one side (downwards) by 40 % of its length. The dashed
// line, the map framing and the connection effect all use this curve.
// Returns its control point (the middle when the two points are the same).
export function routeControlPoint(u, s) {
  const dx = s.x - u.x;
  const dy = s.y - u.y;
  const len = Math.sqrt(dx * dx + dy * dy);
  const mx = (u.x + s.x) / 2;
  const my = (u.y + s.y) / 2;
  if (!(len > 0)) return { x: mx, y: my };
  let nx = -dy / len;
  let ny = dx / len;
  if (ny < 0 || (ny === 0 && nx < 0)) {
    nx = -nx;
    ny = -ny;
  }
  const bow = len * 0.4;
  return { x: mx + nx * bow, y: my + ny * bow };
}

// ---------------------------------------------------------------------------
// Path parsing (only what the map file uses: M/L/H/V/Z, absolute or relative)

function parsePath(d) {
  const tokens = d.match(
    /[MmLlHhVvZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g,
  );
  const rings = [];
  let ring = null;
  let cmd = "M";
  let x = 0;
  let y = 0;
  let startX = 0;
  let startY = 0;
  let i = 0;

  const num = () => parseFloat(tokens[i++]);
  const isNum = () => i < tokens.length && !/^[A-Za-z]$/.test(tokens[i]);
  const closeRing = () => {
    if (ring && ring.length >= 6) rings.push(ring);
    ring = null;
  };
  const addPoint = () => {
    if (!ring) ring = [startX, startY];
    ring.push(x, y);
  };

  while (tokens && i < tokens.length) {
    if (!isNum()) cmd = tokens[i++];
    switch (cmd) {
      case "M":
      case "m":
        if (!isNum()) break;
        closeRing();
        x = cmd === "m" ? x + num() : num();
        y = cmd === "m" ? y + num() : num();
        startX = x;
        startY = y;
        ring = [x, y];
        // further coordinate pairs after a moveto are linetos
        cmd = cmd === "m" ? "l" : "L";
        break;
      case "L":
      case "l":
        if (!isNum()) break;
        x = cmd === "l" ? x + num() : num();
        y = cmd === "l" ? y + num() : num();
        addPoint();
        break;
      case "H":
      case "h":
        if (!isNum()) break;
        x = cmd === "h" ? x + num() : num();
        addPoint();
        break;
      case "V":
      case "v":
        if (!isNum()) break;
        y = cmd === "v" ? y + num() : num();
        addPoint();
        break;
      case "Z":
      case "z":
        closeRing();
        x = startX;
        y = startY;
        break;
      default:
        // unknown command: skip its numbers
        while (isNum()) i++;
    }
  }
  closeRing();

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const r of rings) {
    for (let k = 0; k < r.length; k += 2) {
      if (r[k] < minX) minX = r[k];
      if (r[k] > maxX) maxX = r[k];
      if (r[k + 1] < minY) minY = r[k + 1];
      if (r[k + 1] > maxY) maxY = r[k + 1];
    }
  }
  return { rings, minX, minY, maxX, maxY };
}

let shapes = null; // parsed on the first lookup
function getShapes() {
  if (!shapes) shapes = MAP_PATHS.map(parsePath);
  return shapes;
}

// ---------------------------------------------------------------------------
// Point tests

// winding number of a closed ring around (px, py): the "nonzero" fill rule of SVG
function winding(ring, px, py) {
  let wn = 0;
  const n = ring.length;
  for (let i = 0, j = n - 2; i < n; j = i, i += 2) {
    const x1 = ring[j];
    const y1 = ring[j + 1];
    const x2 = ring[i];
    const y2 = ring[i + 1];
    const side = (x2 - x1) * (py - y1) - (px - x1) * (y2 - y1);
    if (y1 <= py) {
      if (y2 > py && side > 0) wn++;
    } else if (y2 <= py && side < 0) wn--;
  }
  return wn;
}

function isInside(shape, px, py) {
  if (px < shape.minX || px > shape.maxX || py < shape.minY || py > shape.maxY)
    return false;
  let wn = 0;
  for (const r of shape.rings) wn += winding(r, px, py);
  return wn !== 0;
}

// squared distance from (px, py) to the nearest edge of a closed ring
function ringDistance2(r, px, py) {
  let best = Infinity;
  const n = r.length;
  for (let i = 0, j = n - 2; i < n; j = i, i += 2) {
    const x1 = r[j];
    const y1 = r[j + 1];
    const dx = r[i] - x1;
    const dy = r[i + 1] - y1;
    const len2 = dx * dx + dy * dy;
    let t = len2 > 0 ? ((px - x1) * dx + (py - y1) * dy) / len2 : 0;
    if (t < 0) t = 0;
    else if (t > 1) t = 1;
    const ex = x1 + t * dx - px;
    const ey = y1 + t * dy - py;
    const d2 = ex * ex + ey * ey;
    if (d2 < best) best = d2;
  }
  return best;
}

function distanceToOutline(shape, px, py) {
  let best = Infinity;
  for (const r of shape.rings) {
    const d2 = ringDistance2(r, px, py);
    if (d2 < best) best = d2;
  }
  return Math.sqrt(best);
}

// A city on the coast can fall just outside its country's simplified outline:
// a point this close (in map units, about 7 px at the default zoom) still counts.
const COAST_TOLERANCE = 16;

const indexCache = new Map();

// Index (in MAP_PATHS) of the country that contains the point (map units), or -1.
export function countryIndexAtPoint(px, py) {
  if (!Number.isFinite(px) || !Number.isFinite(py)) return -1;
  const all = getShapes();
  for (let i = 0; i < all.length; i++) {
    if (isInside(all[i], px, py)) return i;
  }
  let bestIndex = -1;
  let bestDist = COAST_TOLERANCE;
  for (let i = 0; i < all.length; i++) {
    const s = all[i];
    if (
      px < s.minX - COAST_TOLERANCE ||
      px > s.maxX + COAST_TOLERANCE ||
      py < s.minY - COAST_TOLERANCE ||
      py > s.maxY + COAST_TOLERANCE
    )
      continue;
    const d = distanceToOutline(s, px, py);
    if (d <= bestDist) {
      bestDist = d;
      bestIndex = i;
    }
  }
  return bestIndex;
}

// Index of the country of a location ({ longitude, latitude }), or -1.
export function countryIndexOfLocation(location) {
  if (!location) return -1;
  const lon = Number(location.longitude);
  const lat = Number(location.latitude);
  if (!Number.isFinite(lon) || !Number.isFinite(lat)) return -1;
  const key = lon + "," + lat;
  if (indexCache.has(key)) return indexCache.get(key);
  const p = getCoordinatesBy(lon, lat, MAP_WIDTH, MAP_HEIGHT);
  const index = countryIndexAtPoint(p.x, p.y);
  indexCache.set(key, index);
  return index;
}

const boxCache = new Map();

// Box ({ minX, minY, maxX, maxY }, map units) of the land of a location's country
// that holds the location: the outline ring around its point (the main land, not the
// far islands or overseas territories that share the country's path), or the nearest
// ring when a coastal city falls just outside the outline. null: in no country.
export function countryBoxOfLocation(location) {
  const index = countryIndexOfLocation(location);
  if (index < 0) return null;
  const lon = Number(location.longitude);
  const lat = Number(location.latitude);
  const key = lon + "," + lat;
  if (boxCache.has(key)) return boxCache.get(key);

  const p = getCoordinatesBy(lon, lat, MAP_WIDTH, MAP_HEIGHT);
  let ring = null;
  let bestD2 = Infinity;
  for (const r of getShapes()[index].rings) {
    if (winding(r, p.x, p.y) !== 0) {
      ring = r;
      break;
    }
    const d2 = ringDistance2(r, p.x, p.y);
    if (d2 < bestD2) {
      bestD2 = d2;
      ring = r;
    }
  }
  let box = null;
  if (ring) {
    box = { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity };
    for (let k = 0; k < ring.length; k += 2) {
      if (ring[k] < box.minX) box.minX = ring[k];
      if (ring[k] > box.maxX) box.maxX = ring[k];
      if (ring[k + 1] < box.minY) box.minY = ring[k + 1];
      if (ring[k + 1] > box.maxY) box.maxY = ring[k + 1];
    }
    box = Object.freeze(box);
  }
  boxCache.set(key, box);
  return box;
}
