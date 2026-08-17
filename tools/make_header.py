#!/usr/bin/env python3
"""Render header.gif — a looping sunset-silhouette scene for the profile README.

Frames are emitted as plain SVG (no SMIL), rasterised with cairosvg and packed
into a GIF by ffmpeg. GIF is deliberate: raw.githubusercontent.com serves files
with a `sandbox` CSP that freezes SVG animation, so an animated vector header
renders as a dead still frame on the profile. Raster animation is decoded by the
image pipeline and is unaffected.

Usage: python3 make_header.py [out.gif]
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile

W, H = 800, 280
FRAMES, FPS = 100, 20

SUN = (270, 192, 46)          # cx, cy, r
RIDGE_FAR, RIDGE_MID, RIDGE = 198, 214, 226

INK = "#150e1f"               # foreground silhouette
MID_HILL = "#432c50"
FAR_HILL = "#6d4668"


def tau(t, phase=0.0):
    """Loop-safe oscillator in [-1, 1]."""
    return math.sin(2 * math.pi * (t + phase))


def sky():
    stops = [
        (0.00, "#191a38"), (0.20, "#3a2a54"), (0.42, "#78405e"),
        (0.62, "#bd5e4f"), (0.80, "#e6874a"), (1.00, "#f8c169"),
    ]
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return (
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{s}</linearGradient>'
        '<radialGradient id="glow">'
        '<stop offset="0" stop-color="#ffd98a" stop-opacity="0.85"/>'
        '<stop offset="0.55" stop-color="#f6a25c" stop-opacity="0.28"/>'
        '<stop offset="1" stop-color="#f6a25c" stop-opacity="0"/>'
        '</radialGradient>'
        '<radialGradient id="disc">'
        '<stop offset="0" stop-color="#fff3cd"/>'
        '<stop offset="0.72" stop-color="#ffe1a0"/>'
        '<stop offset="1" stop-color="#ffcf85"/>'
        '</radialGradient>'
    )


def clouds(t):
    """Slow drifting bands. Wrap over the loop so the seam is invisible."""
    out = []
    span = W + 260
    for i, (y, w, h, op, speed) in enumerate(
        [(96, 190, 11, 0.20, 1.0), (128, 250, 13, 0.16, 0.65), (66, 150, 8, 0.13, 1.35)]
    ):
        x = (i * 290 + speed * span * t) % span - 200
        out.append(
            f'<ellipse cx="{x:.1f}" cy="{y}" rx="{w}" ry="{h}" fill="#ffd9a8" opacity="{op}"/>'
            f'<ellipse cx="{x + w * 0.55:.1f}" cy="{y + 5}" rx="{w * 0.62:.0f}" ry="{h * 0.7:.0f}"'
            f' fill="#ffc98f" opacity="{op * 0.75:.2f}"/>'
        )
    return "".join(out)


def bird(x, y, scale, flap):
    """Gull silhouette. flap in [-1,1] drives the wing beat."""
    up = 5.2 * flap
    mid = 3.4 + 2.6 * flap
    d = f"M -10,{-up:.1f} Q -5,{-mid - 3:.1f} 0,0 Q 5,{-mid - 3:.1f} 10,{-up:.1f}"
    return (
        f'<path d="{d}" transform="translate({x:.1f},{y:.1f}) scale({scale})" fill="none"'
        f' stroke="{INK}" stroke-width="{2.0 / scale:.2f}" stroke-linecap="round"/>'
    )


def flock(t):
    out = []
    span = W + 200
    birds = [
        (0, 92, 1.00, 0.00), (34, 78, 0.86, 0.18), (36, 106, 0.88, 0.10),
        (68, 66, 0.72, 0.32), (70, 118, 0.74, 0.26), (104, 96, 0.62, 0.44),
    ]
    for dx, y, sc, ph in birds:
        x = (-160 + dx + span * t) % span - 120
        bob = 3.5 * tau(t, ph * 0.5)
        out.append(bird(x, y + bob, sc, tau(t * 6, ph)))
    return "".join(out)


def deer(x, ground, scale, t):
    """Stag silhouette facing the sun (left). Local origin = hooves on the ridge."""
    ear = 6 * tau(t, 0.0)
    tail = 7 * tau(t, 0.35)
    legs = "".join(
        f'<path d="M {a},-30 L {b},-1" stroke="{INK}" stroke-width="4.6"'
        f' stroke-linecap="round" fill="none"/>'
        for a, b in [(-22, -25), (-13, -11), (18, 16), (27, 30)]
    )
    body = (
        '<path d="M -30,-36 C -32,-47 -22,-54 -4,-55 C 14,-56 28,-51 33,-44'
        ' C 37,-39 35,-31 27,-28 C 8,-24 -16,-24 -27,-28 C -31,-30 -31,-33 -30,-36 Z"/>'
    )
    # tapered band, not a round stroke — a tube of even width reads as a llama
    neck = (
        '<path d="M -30,-42 C -36,-53 -44,-64 -52,-71 L -44,-79'
        ' C -37,-70 -26,-57 -17,-51 Z"/>'
    )
    head = (
        '<path d="M -52,-73 C -58,-80 -67,-83 -71,-79 C -74,-75.5 -68,-70.5 -61,-70'
        ' C -55,-69.6 -52,-71 -52,-73 Z"/>'
    )
    antler = (
        f'<g fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round">'
        '<path d="M -56,-83 C -60,-92 -65,-97 -72,-102"/>'
        '<path d="M -51,-84 C -48,-93 -43,-98 -36,-102"/>'
        '<path d="M -61,-92 L -69,-94"/><path d="M -47,-93 L -39,-92"/>'
        '<path d="M -67,-98 L -75,-99"/><path d="M -42,-98 L -35,-97"/>'
        '</g>'
    )
    earp = (
        f'<path d="M -54,-81 C -57,-88 -53,-92 -49,-89 C -47,-87 -50,-82 -52,-80 Z"'
        f' transform="rotate({ear:.1f} -53 -81)"/>'
    )
    tailp = (
        f'<path d="M 32,-47 C 37,-45 38,-38 35,-35 C 32,-38 31,-43 32,-47 Z"'
        f' transform="rotate({tail:.1f} 32 -47)"/>'
    )
    return (
        f'<g transform="translate({x},{ground}) scale({scale})" fill="{INK}">'
        f'{legs}{neck}{body}{head}{earp}{antler}{tailp}</g>'
    )


def cat(x, ground, scale, t):
    """Sitting cat, tail swaying. Keeps the cat motif from the old header."""
    sway = 13 * tau(t, 0.12)
    ear = 4 * tau(t, 0.55)
    body = (
        '<path d="M -13,-1 C -17,-13 -13,-26 -3,-30 C 7,-33 15,-25 16,-12'
        ' C 16.6,-6 16,-1 15,-1 Z"/>'
    )
    head = '<circle cx="-5" cy="-36" r="10.5"/>'
    ears = (
        f'<g transform="rotate({ear:.1f} -5 -40)">'
        '<path d="M -13,-41 L -15,-51 L -6,-44 Z"/>'
        '<path d="M -1,-44 L 3,-52 L 5,-42 Z"/></g>'
    )
    tail = (
        f'<path d="M 14,-6 C 26,-4 32,-14 30,-26" fill="none" stroke="{INK}"'
        f' stroke-width="5" stroke-linecap="round"'
        f' transform="rotate({sway:.1f} 14 -6)"/>'
    )
    return (
        f'<g transform="translate({x},{ground}) scale({scale})" fill="{INK}">'
        f'{tail}{body}{head}{ears}</g>'
    )


def grass(t):
    """Swaying blades along the ridge. Short, dense and jittered — even tall
    strokes read as a wire fence rather than grass."""
    out = []
    for i in range(170):
        x = -6 + i * 4.8 + (i * 37 % 11) * 0.45
        base = RIDGE + 3 + (i * 17 % 5)
        hgt = 5 + (i * 13 % 9)
        bend = 3.0 * tau(t, i * 0.018)
        out.append(
            f'<path d="M {x:.1f},{base} Q {x + bend * 0.45:.1f},{base - hgt * 0.6:.1f}'
            f' {x + bend:.1f},{base - hgt}" fill="none" stroke="{INK}"'
            f' stroke-width="1.4" stroke-linecap="round"/>'
        )
    return "".join(out)


def motes(t):
    out = []
    for i in range(16):
        px = (i * 71 % W)
        drift = 26 * tau(t, i * 0.06)
        rise = (t + i / 16.0) % 1.0
        y = RIDGE - 4 - rise * 92
        op = 0.55 * math.sin(math.pi * rise)
        out.append(
            f'<circle cx="{px + drift:.1f}" cy="{y:.1f}" r="{1.5 + (i % 3) * 0.4:.1f}"'
            f' fill="#ffd89a" opacity="{op:.2f}"/>'
        )
    return "".join(out)


def frame(t):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{sky()}</defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<circle cx="{SUN[0]}" cy="{SUN[1]}" r="{SUN[2] * 2.7:.0f}" fill="url(#glow)"/>
{clouds(t)}
<circle cx="{SUN[0]}" cy="{SUN[1]}" r="{SUN[2]}" fill="url(#disc)"/>
{flock(t)}
<path d="M0,{H} L0,{RIDGE_FAR + 6} C 120,{RIDGE_FAR - 16} 210,{RIDGE_FAR + 4} 320,{RIDGE_FAR - 4}
 C 440,{RIDGE_FAR - 12} 540,{RIDGE_FAR + 6} 660,{RIDGE_FAR - 2} C 740,{RIDGE_FAR - 8} 780,{RIDGE_FAR + 2} {W},{RIDGE_FAR - 2}
 L{W},{H} Z" fill="{FAR_HILL}" opacity="0.55"/>
<path d="M0,{H} L0,{RIDGE_MID + 8} C 100,{RIDGE_MID - 8} 190,{RIDGE_MID + 6} 300,{RIDGE_MID}
 C 420,{RIDGE_MID - 8} 520,{RIDGE_MID + 8} 640,{RIDGE_MID + 1} C 730,{RIDGE_MID - 5} 770,{RIDGE_MID + 4} {W},{RIDGE_MID}
 L{W},{H} Z" fill="{MID_HILL}" opacity="0.9"/>
{motes(t)}
<path d="M0,{H} L0,{RIDGE + 10} C 90,{RIDGE + 2} 170,{RIDGE - 4} 260,{RIDGE - 2}
 C 360,{RIDGE} 430,{RIDGE - 6} 520,{RIDGE - 3} C 620,{RIDGE} 700,{RIDGE - 5} {W},{RIDGE - 1}
 L{W},{H} Z" fill="{INK}"/>
{deer(300, RIDGE - 1, 0.78, t)}
{cat(624, RIDGE + 2, 0.86, t)}
{grass(t)}
</svg>"""


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "header.gif")
    import cairosvg

    tmp = tempfile.mkdtemp(prefix="header-")
    try:
        for i in range(FRAMES):
            cairosvg.svg2png(
                bytestring=frame(i / FRAMES).encode(),
                write_to=os.path.join(tmp, f"f{i:04d}.png"),
                output_width=W, output_height=H,
            )
        pal = os.path.join(tmp, "pal.png")

        def run(args):
            subprocess.run(args, check=True, capture_output=True)

        run(["ffmpeg", "-y", "-i", os.path.join(tmp, "f%04d.png"),
             "-vf", "palettegen=max_colors=224:stats_mode=full", pal])
        run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%04d.png"),
             "-i", pal, "-lavfi", "paletteuse=dither=sierra2_4a:diff_mode=rectangle",
             "-loop", "0", out])
        print(f"{out}  {os.path.getsize(out) / 1024:.0f} KB  {FRAMES} frames @ {FPS}fps")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
