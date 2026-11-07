"""Generate the OvpnPlus app icons, tray icons, login logos and installer
bitmaps.

App icons, login logos and installer bitmaps come from the brand artwork in
./source:

  mark-on-dark.png       ring mark for dark backgrounds (white ring)
  mark-on-light.png      ring mark for light backgrounds (black ring)
  wordmark-on-dark.png   "OVPNPLUS" for dark backgrounds
  wordmark-on-light.png  "OVPNPLUS" for light backgrounds

The tray icons are drawn from geometry on a 16-unit grid. Gold means
protected:

  connected     gold coin with a dark core
  connecting    faint track ring, gold 120 degree arc and a core dot
                (Windows also gets the turning-arc frames connecting_<n>.ico)
  disconnected  outline ring with a core dot
  paused        outline ring with two gold pause bars

Every state comes for a dark taskbar (<name>) and a light taskbar
(<name>_lt). Windows gets .ico files (16, 20, 24, 32, 40 and 48 px for
100% to 300% display scale), Linux gets <name>.png (16 px) and
<name>@2x.png (32 px).

Usage: python3 make_icons.py <ui-dir> [<preview-dir>] [--tray-only]

  --tray-only   write only public/tray/windows/*.ico and public/tray/linux/*.png
"""
import math
import os
import sys

from PIL import Image, ImageDraw

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
if not ARGS:
    sys.exit(__doc__)
TRAY_ONLY = "--tray-only" in sys.argv[1:]
UI = ARGS[0]
PREVIEW = ARGS[1] if len(ARGS) > 1 else None
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source")

BG_DARK = (20, 22, 28, 255)  # app icon / installer background


def load(name):
    return Image.open(os.path.join(SRC, name)).convert("RGBA")


MARK_DARK = load("mark-on-dark.png")
MARK_LIGHT = load("mark-on-light.png")
WORD_DARK = load("wordmark-on-dark.png")
WORD_LIGHT = load("wordmark-on-light.png")


def fit(img, w, h):
    """Scale img to fit inside w x h, keeping its aspect ratio."""
    scale = min(w / img.width, h / img.height)
    return img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)


def app_icon(size):
    """Mark on a dark rounded square (supersampled for clean edges)."""
    big = size * 4
    canvas = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ImageDraw.Draw(canvas).rounded_rectangle([0, 0, big - 1, big - 1], radius=round(big * 0.22), fill=BG_DARK)
    mark = fit(MARK_DARK, round(big * 0.70), round(big * 0.70))
    canvas.alpha_composite(mark, ((big - mark.width) // 2, (big - mark.height) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


# ------------------------------------------------------------------ tray icons

TRAY_KINDS = ("connected", "connecting", "disconnected", "paused")
TRAY_SIZES_WINDOWS = (48, 40, 32, 24, 20, 16)  # 300% .. 100% display scale
CONNECTING_FRAMES = 8  # Windows turning arc: 45 degree steps, frame 0 = connecting.ico
SUPERSAMPLE = 4  # every pixel is drawn as 4 x 4 samples, then averaged down

GOLD = (0xFF, 0xB0, 0x00)
GOLD_ON_LIGHT = (0xA8, 0x6E, 0x00)  # gold strokes on a light taskbar
CORE_ON_GOLD = (0x11, 0x11, 0x11)

# keyed by "light taskbar?"
TASKBAR = {False: (0x1F, 0x1F, 0x1F), True: (0xF3, 0xF3, 0xF3)}
INK = {False: (0xF4, 0xF4, 0xF5), True: (0x1F, 0x1F, 0x1F)}
ACCENT = {False: GOLD, True: GOLD_ON_LIGHT}
# connecting track: >= 3:1 on the dark taskbar; on the light taskbar it stays faint (as in design B)
# so the gold arc stands out from it, since both have similar lightness at 3:1
TRACK = {False: (0x74, 0x74, 0x7C), True: (0xB4, 0xB4, 0xBA)}


def luminance(rgb):
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# Shapes are signed distance functions in 16-grid units (negative = inside).

def disc(r, cx=8.0, cy=8.0):
    return lambda x, y: math.hypot(x - cx, y - cy) - r


def ring(r, width, cx=8.0, cy=8.0):
    return lambda x, y: abs(math.hypot(x - cx, y - cy) - r) - width / 2


def arc(r, width, start, sweep, cx=8.0, cy=8.0):
    """Arc stroke with round caps. Angles in degrees, clockwise from 12 o'clock."""

    def point(angle):
        a = math.radians(angle)
        return cx + r * math.sin(a), cy - r * math.cos(a)

    ends = (point(start), point(start + sweep))

    def sdf(x, y):
        angle = math.degrees(math.atan2(x - cx, cy - y)) % 360
        if (angle - start) % 360 <= sweep:
            return abs(math.hypot(x - cx, y - cy) - r) - width / 2
        return min(math.hypot(x - ex, y - ey) for ex, ey in ends) - width / 2

    return sdf


def box(x0, y0, x1, y1, radius=0.0):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hh = (x1 - x0) / 2 - radius, (y1 - y0) / 2 - radius

    def sdf(x, y):
        qx, qy = abs(x - cx) - hw, abs(y - cy) - hh
        return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - radius

    return sdf


def pause_bar_pixels(size):
    """The two pause bars as whole-pixel rects (x0, y0, x1, y1) for this size.

    On the 16 px grid they are x 5-7 and 9-11, y 5-11 (doubled exactly at
    32 px); other sizes keep the bars centred, with whole-pixel edges.
    """
    k = size / 16
    width = int(2 * k + 0.5)
    gap = 2 * max(1, math.ceil(k - 0.5))  # even, so the bars stay centred
    height = 2 * width + gap
    c = size // 2
    top, bottom = c - height // 2, c + height // 2
    return [
        (c - gap // 2 - width, top, c - gap // 2, bottom),
        (c + gap // 2, top, c + gap // 2 + width, bottom),
    ]


def tray_layers(kind, light, size, frame=0):
    """(shape, colour) layers, painted in order."""
    ink, accent, track = INK[light], ACCENT[light], TRACK[light]
    if kind == "connected":
        if light:
            # gold alone is too faint on a light taskbar: keep a dark rim
            return [(disc(6.5), GOLD), (ring(6.5, 1), ink), (disc(2.5), ink)]
        return [(disc(7), GOLD), (disc(2.5), CORE_ON_GOLD)]
    if kind == "connecting":
        start = frame * 360 / CONNECTING_FRAMES
        return [(ring(6, 2), track), (arc(6, 2.25, start, 120), accent), (disc(1.75), ink)]
    if kind == "disconnected":
        return [(ring(6, 2), ink), (disc(2), ink)]
    if kind == "paused":
        unit = 16 / size
        # corner radius 0.6 units, dropped where it is under a pixel so the
        # snapped bar edges stay crisp at 16-24 px
        radius = 0.6 if 0.6 / unit >= 1 else 0.0
        bars = [box(x0 * unit, y0 * unit, x1 * unit, y1 * unit, radius=radius)
                for x0, y0, x1, y1 in pause_bar_pixels(size)]
        return [(ring(6, 2), ink)] + [(bar, accent) for bar in bars]
    raise ValueError(kind)


def render(layers, size):
    """Rasterise the layers into a size x size RGBA image (anti-aliased)."""
    unit = 16 / size  # grid units per pixel
    step = unit / SUPERSAMPLE  # grid units per sample
    samples = SUPERSAMPLE * SUPERSAMPLE
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = img.load()
    for py in range(size):
        for px in range(size):
            acc_r = acc_g = acc_b = acc_a = 0.0
            for sy in range(SUPERSAMPLE):
                y = (py + (sy + 0.5) / SUPERSAMPLE) * unit
                for sx in range(SUPERSAMPLE):
                    x = (px + (sx + 0.5) / SUPERSAMPLE) * unit
                    r = g = b = a = 0.0  # premultiplied
                    for shape, rgb in layers:
                        cover = min(1.0, max(0.0, 0.5 - shape(x, y) / step))
                        if cover > 0:
                            keep = 1 - cover
                            r = rgb[0] * cover + r * keep
                            g = rgb[1] * cover + g * keep
                            b = rgb[2] * cover + b * keep
                            a = cover + a * keep
                    acc_r += r
                    acc_g += g
                    acc_b += b
                    acc_a += a
            alpha = round(acc_a / samples * 255)
            if alpha > 0:
                pixels[px, py] = (
                    round(acc_r / acc_a),
                    round(acc_g / acc_a),
                    round(acc_b / acc_a),
                    alpha,
                )
    return img


_tray_cache = {}


def tray_icon(kind, light_taskbar, size, frame=0):
    key = (kind, light_taskbar, size, frame)
    if key not in _tray_cache:
        _tray_cache[key] = render(tray_layers(kind, light_taskbar, size, frame), size)
    return _tray_cache[key]


def check_tray_contrast():
    """The gold strokes and the ink must stay >= 3:1 (the light-taskbar track is decorative)."""
    for light in (False, True):
        for name, rgb in (("track", TRACK[light]), ("accent", ACCENT[light]), ("ink", INK[light])):
            ratio = contrast(rgb, TASKBAR[light])
            label = "light" if light else "dark"
            print(f"  {label} taskbar {name:6s} {ratio:4.2f}:1")
            if name == "track" and light:
                arc = contrast(rgb, ACCENT[light])
                print(f"  light taskbar arc vs track {arc:4.2f}:1")
                continue
            if ratio < 3:
                sys.exit(f"{label} taskbar {name} contrast {ratio:.2f}:1 is below 3:1")


def tray_name(kind, light, frame=0):
    return kind + ("_lt" if light else "") + (f"_{frame}" if frame else "")


def make_tray_icons(out):
    check_tray_contrast()
    for kind in TRAY_KINDS:
        frames = range(CONNECTING_FRAMES) if kind == "connecting" else (0,)
        for light in (False, True):
            for frame in frames:
                name = tray_name(kind, light, frame)
                save_ico([tray_icon(kind, light, s, frame) for s in TRAY_SIZES_WINDOWS],
                         out(f"public/tray/windows/{name}.ico"))
            name = tray_name(kind, light)
            tray_icon(kind, light, 16).save(out(f"public/tray/linux/{name}.png"))
            tray_icon(kind, light, 32).save(out(f"public/tray/linux/{name}@2x.png"))


def tray_preview():
    """Both taskbars: each state at 4x zoom (16 px), then 32, 24, 20 and 16 px."""
    col_w, row_h = 230, 92
    sheet = Image.new("RGBA", (10 + col_w * len(TRAY_KINDS), 10 + row_h * 2), (128, 128, 128, 255))
    for row, light in enumerate((False, True)):
        y0 = 10 + row * row_h
        band = Image.new("RGBA", (col_w * len(TRAY_KINDS) - 10, row_h - 10), TASKBAR[light] + (255,))
        sheet.alpha_composite(band, (10, y0))
        for col, kind in enumerate(TRAY_KINDS):
            x = 10 + col * col_w + 8
            sheet.alpha_composite(tray_icon(kind, light, 16).resize((64, 64), Image.NEAREST), (x, y0 + 9))
            x += 72
            for s in (32, 24, 20, 16):
                sheet.alpha_composite(tray_icon(kind, light, s), (x, y0 + 9 + 64 - s))
                x += s + 6
    return sheet


def save_ico(images, path):
    images = sorted(images, key=lambda im: -im.width)
    images[0].save(path, format="ICO", sizes=[im.size for im in images], append_images=images[1:])


def main():
    out = lambda *p: os.path.join(UI, *p)

    # tray icons: Windows .ico, Linux .png (+@2x)
    make_tray_icons(out)

    if not TRAY_ONLY:
        # application icons
        save_ico([app_icon(s) for s in (256, 128, 96, 72, 64, 48, 40, 36, 32, 30, 24, 20, 16)],
                 out("buildResources/appicons/icon.ico"))
        save_ico([app_icon(s) for s in (256, 64, 48, 32, 16)], out("References/Windows/Installer/icon.ico"))
        for s in (16, 32, 48, 64, 128, 256):
            app_icon(s).save(out(f"buildResources/appicons/icons/{s}x{s}.png"))
        app_icon(64).save(out("public/64x64.png"))

        # login screen logos (the login view picks one by color theme)
        fit(WORD_LIGHT, 480, 56).save(out("src/assets/logo.png"))
        fit(WORD_DARK, 480, 56).save(out("src/assets/logo_dark.png"))

        # installer: page header (white) and welcome/finish side bitmap (dark)
        head = Image.new("RGBA", (150, 57), (255, 255, 255, 255))
        word = fit(WORD_LIGHT, 136, 30)
        head.alpha_composite(word, ((150 - word.width) // 2, (57 - word.height) // 2))
        head.convert("RGB").save(out("References/Windows/Installer/header.bmp"))
        side = Image.new("RGBA", (164, 314), BG_DARK)
        mark = fit(MARK_DARK, 104, 104)
        side.alpha_composite(mark, ((164 - mark.width) // 2, 92))
        word = fit(WORD_DARK, 140, 20)
        side.alpha_composite(word, ((164 - word.width) // 2, 92 + mark.height + 18))
        side.convert("RGB").save(out("References/Windows/Installer/startfinish.bmp"))

    if PREVIEW:
        os.makedirs(PREVIEW, exist_ok=True)
        tray_preview().save(os.path.join(PREVIEW, "tray_preview.png"))
        if not TRAY_ONLY:
            sheet = Image.new("RGBA", (900, 620), (128, 128, 128, 255))
            sheet.alpha_composite(app_icon(256), (10, 10))
            sheet.alpha_composite(app_icon(32), (280, 10))
            sheet.alpha_composite(app_icon(16), (320, 10))
            for col, kind in enumerate(TRAY_KINDS):
                for row, light in enumerate((False, True)):
                    bg = TASKBAR[light] + (255,)
                    for i, s in enumerate((16, 32)):
                        tile = Image.new("RGBA", (64, 64), bg)
                        tile.alpha_composite(tray_icon(kind, light, s).resize((64, 64), Image.NEAREST))
                        sheet.alpha_composite(tile, (280 + col * 150 + row * 70, 60 + i * 70))
            dark = Image.new("RGBA", (500, 70), BG_DARK)
            dark.alpha_composite(fit(WORD_DARK, 480, 56), (10, 7))
            light = Image.new("RGBA", (500, 70), (245, 247, 250, 255))
            light.alpha_composite(fit(WORD_LIGHT, 480, 56), (10, 7))
            sheet.alpha_composite(dark, (280, 210))
            sheet.alpha_composite(light, (280, 290))
            sheet.alpha_composite(Image.open(out("References/Windows/Installer/startfinish.bmp")).convert("RGBA"), (10, 290))
            sheet.alpha_composite(Image.open(out("References/Windows/Installer/header.bmp")).convert("RGBA"), (280, 380))
            sheet.save(os.path.join(PREVIEW, "brand_preview.png"))


main()
