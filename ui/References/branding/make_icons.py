"""Generate LepidVPN logo, app icons and tray icons.

Usage: python3 make_icons.py <ui-dir> <preview-dir>
"""
import io
import os
import sys

import cairosvg
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

UI = sys.argv[1]
PREVIEW = sys.argv[2]

NAVY = "#0B1220"
CYAN = "#22D3EE"
BLUE = "#3B82F6"
GREEN = "#34D399"
AMBER = "#F5B942"

# Shield with a knocked-out "L" (100x100 box). Even-odd fill makes the L a hole.
SHIELD = "M50 5 L87 17.5 V45 C87 69.5 71.5 86.5 50 95 C28.5 86.5 13 69.5 13 45 V17.5 Z"
L_MARK = "M37 27 H49 V60 H66 V71 H37 Z"


def mark_svg(fill, size=100, hole=True, extra=""):
    path = SHIELD + (" " + L_MARK if hole else "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 100 100">'
        f'<path fill-rule="evenodd" d="{path}" fill="{fill}"/>{extra}</svg>'
    )


def app_icon_svg(size):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 100 100">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>
<rect x="2" y="2" width="96" height="96" rx="22" fill="{NAVY}"/>
<g transform="translate(15 14) scale(0.7)">
<path d="{SHIELD}" fill="url(#g)"/>
<path d="{L_MARK}" fill="#FFFFFF"/>
</g></svg>'''


def png(svg, size):
    data = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def text_path(text, font_file, height):
    """SVG path of `text` with cap height scaled to `height`; returns (d, width)."""
    font = TTFont(font_file)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    cap = getattr(font["OS/2"], "sCapHeight", 0) or upm * 0.7
    scale = height / cap
    pen = SVGPathPen(glyphs)
    x = 0
    for ch in text:
        name = cmap[ord(ch)]
        tpen = TransformPen(pen, (scale, 0, 0, -scale, x * scale, height))
        glyphs[name].draw(tpen)
        x += glyphs[name].width
    return pen.getCommands(), x * scale


def status_overlay(kind):
    """Status badge drawn in the bottom-right of the 100x100 tray mark."""
    if kind == "connected":
        return f'<circle cx="76" cy="76" r="22" fill="{GREEN}" stroke="#000" stroke-opacity="0.35" stroke-width="4"/>'
    if kind == "connecting":
        return f'<circle cx="76" cy="76" r="17" fill="none" stroke="{GREEN}" stroke-width="9"/>'
    if kind == "paused":
        return (f'<rect x="60" y="56" width="11" height="40" rx="2" fill="{AMBER}"/>'
                f'<rect x="78" y="56" width="11" height="40" rx="2" fill="{AMBER}"/>')
    return ""


def tray_svg(kind, light_taskbar):
    color = "#1A1A1A" if light_taskbar else "#FFFFFF"
    # shrink the shield a little when a badge is shown so both stay readable
    badge = status_overlay(kind)
    group = f'<g transform="translate(0 0) scale({0.86 if badge else 1})">' \
            f'<path fill-rule="evenodd" d="{SHIELD} {L_MARK}" fill="{color}"/></g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">{group}{badge}</svg>'


def save_ico(images, path):
    images[0].save(path, format="ICO", sizes=[im.size for im in images], append_images=images[1:])


def main():
    os.makedirs(PREVIEW, exist_ok=True)

    # --- wordmark logo for the login screen
    d, w = text_path("LepidVPN", "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf", 22)
    total_w = 38 + w
    logo = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="32" viewBox="0 0 {total_w:.1f} 32" fill="none">
<defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>
<g transform="scale(0.32)"><path fill-rule="evenodd" d="{SHIELD} {L_MARK}" fill="url(#lg)"/></g>
<g transform="translate(38 5)"><path d="{d}" fill="#2B9BF4"/></g>
</svg>
'''
    with open(os.path.join(UI, "src/assets/logo.svg"), "w") as f:
        f.write(logo)
    grey = logo.replace('fill="url(#lg)"', 'fill="#8A94A6"').replace('fill="#2B9BF4"/></g>', 'fill="#8A94A6"/></g>')
    with open(os.path.join(UI, "src/assets/logo_grey.svg"), "w") as f:
        f.write(grey)
    png(logo.replace(f'width="{total_w:.0f}" height="32"', f'width="{total_w * 8:.0f}" height="256"'), 256)

    # --- application icons
    sizes = [16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 128, 256]
    imgs = [png(app_icon_svg(s), s) for s in sizes]
    save_ico(imgs[::-1], os.path.join(UI, "buildResources/appicons/icon.ico"))
    save_ico([png(app_icon_svg(s), s) for s in (256, 64, 48, 32, 16)],
             os.path.join(UI, "References/Windows/Installer/icon.ico"))
    for s in (16, 32, 48, 64, 128, 256):
        png(app_icon_svg(s), s).save(os.path.join(UI, f"buildResources/appicons/icons/{s}x{s}.png"))
    png(app_icon_svg(64), 64).save(os.path.join(UI, "public/64x64.png"))
    png(app_icon_svg(512), 512).save(os.path.join(PREVIEW, "app_512.png"))

    # --- tray icons (Windows .ico, Linux .png)
    preview = Image.new("RGBA", (8 * 72 + 8, 2 * 72 + 8), (120, 120, 120, 255))
    for col, kind in enumerate(["connected", "connecting", "disconnected", "paused"]):
        for row, light in enumerate([False, True]):
            name = kind + ("_lt" if light else "")
            svg = tray_svg(kind, light)
            save_ico([png(svg, s) for s in (32, 24, 20, 16)], os.path.join(UI, f"public/tray/windows/{name}.ico"))
            png(svg, 16).save(os.path.join(UI, f"public/tray/linux/{name}.png"))
            png(svg, 32).save(os.path.join(UI, f"public/tray/linux/{name}@2x.png"))
            bg = (240, 240, 240, 255) if light else (32, 32, 32, 255)
            tile = Image.new("RGBA", (64, 64), bg)
            tile.alpha_composite(png(svg, 32).resize((64, 64), Image.NEAREST))
            preview.alpha_composite(tile, (8 + (col * 2 + 0) * 72 if False else 8 + col * 144 + row * 72, 8))
            tile16 = Image.new("RGBA", (64, 64), bg)
            tile16.alpha_composite(png(svg, 16).resize((64, 64), Image.NEAREST))
            preview.alpha_composite(tile16, (8 + col * 144 + row * 72, 80))
    preview.save(os.path.join(PREVIEW, "tray_new.png"))

    # logo preview on dark and light backgrounds
    lp = png(logo.replace(f'width="{total_w:.0f}" height="32"', f'width="{total_w * 4:.0f}" height="128"'), 128)
    lp = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=logo.encode(), scale=4))).convert("RGBA")
    canvas = Image.new("RGBA", (lp.width + 40, lp.height * 2 + 60), (11, 18, 32, 255))
    canvas.paste((245, 247, 250, 255), (0, lp.height + 30, canvas.width, canvas.height))
    canvas.alpha_composite(lp, (20, 15))
    canvas.alpha_composite(lp, (20, lp.height + 45))
    canvas.save(os.path.join(PREVIEW, "logo_preview.png"))


main()


def installer_bitmaps():
    shield = f'''<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>'''
    # welcome/finish page: 164x314, navy with the shield mark
    side = f'''<svg xmlns="http://www.w3.org/2000/svg" width="164" height="314" viewBox="0 0 164 314">{shield}
<rect width="164" height="314" fill="{NAVY}"/>
<g transform="translate(42 100) scale(0.8)"><path d="{SHIELD}" fill="url(#g)"/><path d="{L_MARK}" fill="#FFFFFF"/></g></svg>'''
    Image.open(io.BytesIO(cairosvg.svg2png(bytestring=side.encode()))).convert("RGB").save(
        os.path.join(UI, "References/Windows/Installer/startfinish.bmp"))
    # page header: 150x57, white with the wordmark
    with open(os.path.join(UI, "src/assets/logo.svg")) as f:
        logo = f.read()
    lw = float(logo.split('viewBox="0 0 ')[1].split(" ")[0])
    scale = min(130 / lw, 1.2)
    lg = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=logo.encode(), scale=scale))).convert("RGBA")
    head = Image.new("RGBA", (150, 57), (255, 255, 255, 255))
    head.alpha_composite(lg, ((150 - lg.width) // 2, (57 - lg.height) // 2))
    head.convert("RGB").save(os.path.join(UI, "References/Windows/Installer/header.bmp"))
    head.convert("RGB").save(os.path.join(PREVIEW, "header_new.png"))
    Image.open(os.path.join(UI, "References/Windows/Installer/startfinish.bmp")).save(os.path.join(PREVIEW, "side_new.png"))


installer_bitmaps()
