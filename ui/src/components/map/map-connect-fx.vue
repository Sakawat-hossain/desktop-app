<template>
  <svg
    class="connectFx"
    :width="box.width"
    :height="box.height"
    :viewBox="`0 0 ${box.width} ${box.height}`"
    :style="{ left: box.left + 'px', top: box.top + 'px' }"
    aria-hidden="true"
  >
    <!--
      The connection effect on the map, placed in the locations layer (px), from the
      user's location ('from') to the server ('to'), on the curve of the dashed line:
        mode "travel": the gold line draws itself from the user to the server and a comet
                       (a dot with a short fading tail) runs along it, again and again;
        mode "land":   the comet ends its run at the server ("landed"), a ripple bursts at
                       the pin and the line fades out ("done");
        mode "leave":  everything fades out ("done"): the connection was cancelled or failed.
      The dashes are in 'pathLength' units (100 = the whole line), so the animations go on
      unchanged when the zoom changes the length of the line.
      (No comment above the root element: the component must keep one root node.)
    -->
    <template v-if="line">
      <g class="fxLine">
        <path
          class="fxLineGlow"
          :d="line.d"
          pathLength="100"
          :stroke-dasharray="line.lineDash"
          stroke-dashoffset="0"
        />
        <path
          class="fxLineStroke"
          :d="line.d"
          pathLength="100"
          :stroke-dasharray="line.lineDash"
          stroke-dashoffset="0"
        />
      </g>
      <g class="fxComet">
        <path
          v-for="(t, i) in line.tails"
          :key="i"
          class="fxTail"
          :d="line.d"
          pathLength="100"
          :stroke-dasharray="t.dash"
          :stroke-width="t.width"
          :stroke-opacity="t.opacity"
          stroke-dashoffset="0"
        />
        <path
          class="fxHalo"
          :d="line.d"
          pathLength="100"
          :stroke-dasharray="line.headDash"
          stroke-dashoffset="0"
        />
        <path
          class="fxHead"
          :d="line.d"
          pathLength="100"
          :stroke-dasharray="line.headDash"
          stroke-dashoffset="0"
        />
        <path
          class="fxCore"
          :d="line.d"
          pathLength="100"
          :stroke-dasharray="line.headDash"
          stroke-dashoffset="0"
        />
      </g>
    </template>

    <!-- the burst at the pin when the comet lands: two rings (as the pin's ripple) and a flash -->
    <g class="fxBurst" :transform="`translate(${box.toX} ${box.toY})`">
      <ellipse class="fxRing fxRingOuter" :rx="BURST_RX" :ry="BURST_RY" />
      <ellipse
        class="fxRing fxRingInner"
        :rx="BURST_RX * 0.62"
        :ry="BURST_RY * 0.62"
      />
      <circle class="fxFlash" r="6" />
    </g>
  </svg>
</template>

<script>
import { routeControlPoint } from "./map-geometry";

// closer than this (px) the markers overlap: no line (as the dashed line)
const MIN_LINE_PX = 24;
// one run of the comet (ms): it travels for TRAVEL_PART of it, then fades at the server
const CYCLE_MS = 1600;
const TRAVEL_PART = 0.8;
const TRAVEL_EASING = "cubic-bezier(0.45, 0, 0.3, 1)";
// the comet tail (px), between these parts of the line (pathLength units)
const TAIL_PX = 44;
const TAIL_MIN = 6;
const TAIL_MAX = 40;
// period of the dash patterns (pathLength units): longer than the line and a tail
// together, so a dash never shows twice
const PERIOD = 400;
// landing: the comet ends its run in LAND_MIN_MS .. LAND_MIN_MS + LAND_RUN_MS
// (the further it still has to go, the longer)
const LAND_MIN_MS = 140;
const LAND_RUN_MS = 420;
const LAND_EASING = "cubic-bezier(0.25, 0.6, 0.35, 1)";
// the burst at the pin (ms); the line fades out in its second part
const BURST_MS = 500;
const LINE_FADE_DELAY_MS = 200;
const BURST_EASING = "cubic-bezier(0.2, 0.6, 0.35, 1)";
// cancelled / failed: the effect fades out (ms)
const LEAVE_MS = 300;
// the outer burst ring (px): the size of the connected pin's widest ripple ring
const BURST_RX = 34;
const BURST_RY = 12.4;

// A pattern of one dash 't' long (pathLength units) that ends at the dash offset:
// with the offset at -p the dash covers the line from p - t to p.
function trailingDash(t) {
  const r = (v) => Math.round(v * 100) / 100;
  return `0 ${r(PERIOD - t)} ${r(t)} 0`;
}

// length (px) of the quadratic curve u -> s with the control point c
function curveLength(u, c, s) {
  const n = 24;
  let len = 0;
  let px = u.x;
  let py = u.y;
  for (let i = 1; i <= n; i++) {
    const t = i / n;
    const a = (1 - t) * (1 - t);
    const b = 2 * (1 - t) * t;
    const e = t * t;
    const x = a * u.x + b * c.x + e * s.x;
    const y = a * u.y + b * c.y + e * s.y;
    len += Math.sqrt((x - px) * (x - px) + (y - py) * (y - py));
    px = x;
    py = y;
  }
  return len;
}

export default {
  props: {
    // the user's location and the server: { x, y } (px in the locations layer)
    from: { type: Object, required: true },
    to: { type: Object, required: true },
    // "travel" | "land" | "leave"
    mode: { type: String, default: "travel" },
    // returned with the events, so the parent knows which effect they come from
    fxId: { type: Number, default: 0 },
  },
  emits: ["landed", "done"],
  setup() {
    return { BURST_RX, BURST_RY };
  },

  computed: {
    curve() {
      return routeControlPoint(this.from, this.to);
    },
    // the SVG box (px in the locations layer): the curve and the burst at the server
    box() {
      const u = this.from;
      const s = this.to;
      const c = this.curve;
      const pad = 10;
      const bx = BURST_RX + 6;
      const by = BURST_RY + 6;
      const left = Math.floor(Math.min(u.x - pad, c.x - pad, s.x - bx));
      const top = Math.floor(Math.min(u.y - pad, c.y - pad, s.y - by));
      const right = Math.ceil(Math.max(u.x + pad, c.x + pad, s.x + bx));
      const bottom = Math.ceil(Math.max(u.y + pad, c.y + pad, s.y + by));
      const f = (v) => Math.round(v * 10) / 10;
      return {
        left,
        top,
        width: right - left,
        height: bottom - top,
        toX: f(s.x - left),
        toY: f(s.y - top),
      };
    },
    // the curve and its dash patterns, or null when the points are too close
    line() {
      const u = this.from;
      const s = this.to;
      const dx = s.x - u.x;
      const dy = s.y - u.y;
      if (!(Math.sqrt(dx * dx + dy * dy) >= MIN_LINE_PX)) return null;
      const c = this.curve;
      const b = this.box;
      const f = (v) => Math.round(v * 10) / 10;
      const d =
        `M${f(u.x - b.left)} ${f(u.y - b.top)}` +
        `Q${f(c.x - b.left)} ${f(c.y - b.top)} ${f(s.x - b.left)} ${f(s.y - b.top)}`;
      const len = curveLength(u, c, s);
      const tail = Math.min(
        TAIL_MAX,
        Math.max(TAIL_MIN, (100 * TAIL_PX) / len),
      );
      return {
        d,
        lengthPx: len,
        // the line: from the start to the comet (drawn with its first run)
        lineDash: trailingDash(100),
        // the comet: a dot, and three tails that fade towards their ends
        headDash: trailingDash(0.2),
        tails: [
          { t: tail, width: 2.2, opacity: 0.22 },
          { t: tail * 0.6, width: 2.8, opacity: 0.38 },
          { t: tail * 0.3, width: 3.4, opacity: 0.6 },
        ].map((v) => ({ ...v, dash: trailingDash(v.t) })),
      };
    },
    hasLine() {
      return this.line != null;
    },
  },

  watch: {
    mode(m) {
      if (m === "land") this.land();
      else if (m === "leave") this.leave();
    },
    // the zoom made the line appear (or vanish): its new paths get their animations
    hasLine() {
      if (this.stage !== "travel") return;
      this.cancelAll();
      this.$nextTick(() => {
        if (this.stage === "travel") this.travel();
      });
    },
  },

  created() {
    // not reactive: the running animations, the stage, and a token that is changed to
    // drop the continuations of animations that were cancelled
    this.anims = new Set();
    this.stage = "travel";
    this.token = 0;
  },
  mounted() {
    document.addEventListener("visibilitychange", this.onVisibility);
    this.travel();
    if (this.mode === "land") this.land();
    else if (this.mode === "leave") this.leave();
  },
  beforeUnmount() {
    document.removeEventListener("visibilitychange", this.onVisibility);
    this.token++;
    this.stage = "done";
    this.cancelAll();
  },

  methods: {
    el(sel) {
      return this.$el ? this.$el.querySelector(sel) : null;
    },
    els(sel) {
      return this.$el ? Array.from(this.$el.querySelectorAll(sel)) : [];
    },
    // starts a Web Animation and keeps it until it ends (to pause, resume or cancel it)
    run(el, frames, options) {
      if (!el || typeof el.animate !== "function") return null;
      const a = el.animate(frames, options);
      this.anims.add(a);
      const drop = () => this.anims.delete(a);
      a.finished.then(drop, drop);
      return a;
    },
    cancelAll() {
      const list = Array.from(this.anims);
      this.anims.clear();
      for (const a of list) a.cancel();
    },
    // 'func' once all 'anims' have ended (not when they are cancelled)
    after(anims, func) {
      const token = this.token;
      Promise.all(anims.filter((a) => a != null).map((a) => a.finished)).then(
        () => {
          if (token === this.token) func();
        },
        () => {},
      );
    },

    // the line draws itself with the first run of the comet; the comet runs again and again
    travel() {
      this.stage = "travel";
      if (!this.line) return;
      const move = [
        { offset: 0, strokeDashoffset: "0px", easing: TRAVEL_EASING },
        { offset: TRAVEL_PART, strokeDashoffset: "-100px" },
        { offset: 1, strokeDashoffset: "-100px" },
      ];
      for (const el of this.els(".fxLine path"))
        this.run(el, move, { duration: CYCLE_MS, fill: "forwards" });
      for (const el of this.els(".fxComet path"))
        this.run(el, move, { duration: CYCLE_MS, iterations: Infinity });
      this.run(
        this.el(".fxComet"),
        [
          { offset: 0, opacity: 0 },
          { offset: 0.06, opacity: 1 },
          { offset: TRAVEL_PART, opacity: 1 },
          { offset: 0.92, opacity: 0 },
          { offset: 1, opacity: 0 },
        ],
        { duration: CYCLE_MS, iterations: Infinity },
      );
      if (document.hidden) this.pauseAll();
    },

    // connected: the comet ends its run at the server (from where it is now)
    land() {
      if (this.stage !== "travel") return;
      this.stage = "land";
      const head = this.el(".fxHead");
      const comet = this.el(".fxComet");
      if (!head || !comet || document.hidden) {
        this.cancelAll();
        this.landed();
        return;
      }
      let p = -parseFloat(getComputedStyle(head).strokeDashoffset) || 0;
      const shown = parseFloat(getComputedStyle(comet).opacity) || 0;
      // it has just reached the server and is fading out there: one more, quick run
      if (p >= 99 && shown < 0.6) p = 0;
      p = Math.min(100, Math.max(0, p));
      const lineEls = this.els(".fxLine path");
      const lineAt = lineEls.map((el) => getComputedStyle(el).strokeDashoffset);
      this.cancelAll();

      const duration = Math.round(LAND_MIN_MS + LAND_RUN_MS * (1 - p / 100));
      const opts = { duration, easing: LAND_EASING, fill: "forwards" };
      const runs = [];
      for (const el of this.els(".fxComet path"))
        runs.push(
          this.run(
            el,
            [{ strokeDashoffset: -p + "px" }, { strokeDashoffset: "-100px" }],
            opts,
          ),
        );
      // the line ends where the comet is (still drawing: it follows the comet)
      lineEls.forEach((el, i) =>
        runs.push(
          this.run(
            el,
            [{ strokeDashoffset: lineAt[i] }, { strokeDashoffset: "-100px" }],
            opts,
          ),
        ),
      );
      this.run(
        comet,
        [
          { offset: 0, opacity: shown },
          { offset: Math.min(1, 100 / duration), opacity: 1 },
          { offset: 1, opacity: 1 },
        ],
        { duration, fill: "forwards" },
      );
      this.after(runs, () => this.landed());
    },

    // the comet is at the server: the ripple bursts there and the line fades out
    landed() {
      if (this.stage !== "land") return;
      this.stage = "burst";
      this.$emit("landed", this.fxId);
      if (document.hidden) {
        this.done();
        return;
      }
      const ring = (sel, from, opacity, delay) =>
        this.run(
          this.el(sel),
          [
            { transform: `scale(${from})`, opacity },
            { transform: "scale(1)", opacity: 0 },
          ],
          {
            duration: BURST_MS - delay,
            delay,
            easing: BURST_EASING,
            fill: "forwards",
          },
        );
      const runs = [
        ring(".fxRingOuter", 0.15, 0.95, 0),
        ring(".fxRingInner", 0.2, 0.85, 90),
        this.run(
          this.el(".fxFlash"),
          [
            { transform: "scale(0.4)", opacity: 1 },
            { transform: "scale(1.5)", opacity: 0 },
          ],
          { duration: 320, easing: "ease-out", fill: "forwards" },
        ),
        this.run(this.el(".fxComet"), [{ opacity: 1 }, { opacity: 0 }], {
          duration: 180,
          easing: "ease-out",
          fill: "forwards",
        }),
        this.run(this.el(".fxLine"), [{ opacity: 1 }, { opacity: 0 }], {
          duration: BURST_MS - LINE_FADE_DELAY_MS,
          delay: LINE_FADE_DELAY_MS,
          easing: "ease-in-out",
          fill: "forwards",
        }),
      ];
      this.after(runs, () => this.done());
    },

    // cancelled / failed / disconnected: everything fades out (the comet keeps running)
    leave() {
      if (this.stage === "leave" || this.stage === "done") return;
      this.stage = "leave";
      this.token++;
      if (document.hidden || !this.$el) {
        this.cancelAll();
        this.done();
        return;
      }
      const shown = parseFloat(getComputedStyle(this.$el).opacity);
      const a = this.run(
        this.$el,
        [{ opacity: shown >= 0 ? shown : 1 }, { opacity: 0 }],
        { duration: LEAVE_MS, easing: "ease-out", fill: "forwards" },
      );
      this.after([a], () => this.done());
    },

    done() {
      if (this.stage === "done") return;
      this.stage = "done";
      this.$emit("done", this.fxId);
    },

    pauseAll() {
      for (const a of this.anims) a.pause();
    },
    playAll() {
      for (const a of this.anims) a.play();
    },
    // Hidden window: the running comet stops; an effect that is ending ends at once
    // (no one sees it), so the map can take its final view.
    onVisibility() {
      if (!document.hidden) {
        if (this.stage === "travel") this.playAll();
        return;
      }
      if (this.stage === "travel") {
        this.pauseAll();
        return;
      }
      this.token++;
      this.cancelAll();
      if (this.stage === "land") this.landed();
      else this.done();
    },
  },
};
</script>

<style scoped lang="scss">
// Effect colours (light theme; dark values below): the gold of the map route and pins,
// darker in the light theme to keep its contrast on the pale map.
.connectFx {
  --fx-line: #c47f00;
  --fx-glow: rgba(209, 143, 0, 0.2);
  --fx-tail: #d18f00;
  --fx-head: #d58c00;
  --fx-halo: rgba(224, 150, 0, 0.3);
  --fx-core: #fff4d6;
  --fx-ring: #d18f00;
  --fx-flash: #ffc94d;

  position: absolute;
  display: block;
  overflow: visible;
  pointer-events: none;
}
@media (prefers-color-scheme: dark) {
  .connectFx {
    --fx-line: #ffb000;
    --fx-glow: rgba(255, 176, 0, 0.22);
    --fx-tail: #ffb000;
    --fx-head: #ffc233;
    --fx-halo: rgba(255, 184, 32, 0.36);
    --fx-core: #fffaeb;
    --fx-ring: #ffb000;
    --fx-flash: #ffe08a;
  }
}

.connectFx path {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.fxLineGlow {
  stroke: var(--fx-glow);
  stroke-width: 6;
}
.fxLineStroke {
  stroke: var(--fx-line);
  stroke-width: 1.75;
}
// the comet shows only while it runs (its animation fades it in and out)
.fxComet {
  opacity: 0;
}
.fxTail {
  stroke: var(--fx-tail);
}
.fxHalo {
  stroke: var(--fx-halo);
  stroke-width: 13;
}
.fxHead {
  stroke: var(--fx-head);
  stroke-width: 6.5;
}
.fxCore {
  stroke: var(--fx-core);
  stroke-width: 2.6;
}

.fxRing,
.fxFlash {
  opacity: 0;
  transform-box: fill-box;
  transform-origin: center;
}
.fxRing {
  fill: none;
  stroke: var(--fx-ring);
  stroke-width: 1.6;
}
.fxFlash {
  fill: var(--fx-flash);
}
</style>
