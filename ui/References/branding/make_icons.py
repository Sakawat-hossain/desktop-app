"""Generate the OvpnPlus app icons, tray icons, login logos and installer
bitmaps from the brand artwork in ./source:

  mark-on-dark.png       ring mark for dark backgrounds (white ring)
  mark-on-light.png      ring mark for light backgrounds (black ring)
  wordmark-on-dark.png   "OVPNPLUS" for dark backgrounds
  wordmark-on-light.png  "OVPNPLUS" for light backgrounds

Usage: python3 make_icons.py <ui-dir> [<preview-dir>]
"""
import os
import sys

from PIL import Image, ImageDraw

UI = sys.argv[1]
PREVIEW = sys.argv[2] if len(sys.argv) > 2 else None
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source")

BG_DARK = (20, 22, 28, 255)  # app icon / installer background
GREEN = (52, 211, 153, 255)
AMBER = (245, 185, 66, 255)


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


def tray_icon(kind, light_taskbar, size):
    """Mark with a status badge; drawn at 4x and scaled down."""
    big = size * 4
    canvas = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    src = MARK_LIGHT if light_taskbar else MARK_DARK
    has_badge = kind in ("connected", "connecting", "paused")
    mark = fit(src, round(big * (0.86 if has_badge else 1.0)), round(big * (0.86 if has_badge else 1.0)))
    canvas.alpha_composite(mark, (0, 0) if has_badge else ((big - mark.width) // 2, (big - mark.height) // 2))
    d = ImageDraw.Draw(canvas)
    r = big * 0.22
    cx = cy = big - r - big * 0.02
    if kind == "connected":
        d.ellipse([cx - r - big * 0.04, cy - r - big * 0.04, cx + r + big * 0.04, cy + r + big * 0.04], fill=(0, 0, 0, 110))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    elif kind == "connecting":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN, width=round(big * 0.09))
    elif kind == "paused":
        w = big * 0.11
        top, bottom = big * 0.56, big * 0.98
        d.rectangle([big * 0.60, top, big * 0.60 + w, bottom], fill=AMBER)
        d.rectangle([big * 0.78, top, big * 0.78 + w, bottom], fill=AMBER)
    return canvas.resize((size, size), Image.LANCZOS)


def save_ico(images, path):
    images = sorted(images, key=lambda im: -im.width)
    images[0].save(path, format="ICO", sizes=[im.size for im in images], append_images=images[1:])


def main():
    out = lambda *p: os.path.join(UI, *p)

    # application icons
    save_ico([app_icon(s) for s in (256, 128, 96, 72, 64, 48, 40, 36, 32, 30, 24, 20, 16)],
             out("buildResources/appicons/icon.ico"))
    save_ico([app_icon(s) for s in (256, 64, 48, 32, 16)], out("References/Windows/Installer/icon.ico"))
    for s in (16, 32, 48, 64, 128, 256):
        app_icon(s).save(out(f"buildResources/appicons/icons/{s}x{s}.png"))
    app_icon(64).save(out("public/64x64.png"))

    # tray icons: Windows .ico, Linux .png (+@2x)
    for kind in ("connected", "connecting", "disconnected", "paused"):
        for light in (False, True):
            name = kind + ("_lt" if light else "")
            save_ico([tray_icon(kind, light, s) for s in (32, 24, 20, 16)], out(f"public/tray/windows/{name}.ico"))
            tray_icon(kind, light, 16).save(out(f"public/tray/linux/{name}.png"))
            tray_icon(kind, light, 32).save(out(f"public/tray/linux/{name}@2x.png"))

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
        sheet = Image.new("RGBA", (900, 620), (128, 128, 128, 255))
        sheet.alpha_composite(app_icon(256), (10, 10))
        sheet.alpha_composite(app_icon(32), (280, 10))
        sheet.alpha_composite(app_icon(16), (320, 10))
        for col, kind in enumerate(("connected", "connecting", "disconnected", "paused")):
            for row, light in enumerate((False, True)):
                bg = (240, 240, 240, 255) if light else (32, 32, 32, 255)
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
