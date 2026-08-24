#!/usr/bin/env python3
"""Check assets/header.svg before it ships to a profile page nobody proofreads.

Run: python3 tools/check_header.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(ROOT, "assets", "header.svg")
README = os.path.join(ROOT, "README.md")

src = open(SVG, encoding="utf-8").read()
tree = ET.fromstring(src)  # raises on malformed XML, which is the main risk

# GitHub proxies the SVG through camo, so anything active or externally
# fetched either fails to render or renders for some viewers only. The one
# permitted URL is the SVG namespace itself.
assert src.count("http") == src.count('xmlns="http://www.w3.org/2000/svg"'), \
    "header.svg must stay self-contained: found an external URL"
for banned in ("<script", "<foreignObject", "xlink:href", "<image", "@import"):
    assert banned not in src, f"header.svg must stay self-contained: found {banned!r}"

# Animation only survives when the SVG is referenced as an image. Inline <svg>
# in markdown gets its <style> stripped and the whole thing sits still.
readme = open(README, encoding="utf-8").read()
assert "assets/header.svg" in readme, "README does not reference the header"
assert "<svg" not in readme, "inline <svg> in README will not animate; use <img>"
assert "header.gif" not in readme, "README still points at the retired gif"

assert "prefers-reduced-motion" in src, "no reduced-motion fallback"
assert "prefers-color-scheme" in src, "no light-theme fallback"
assert tree.get("role") == "img" and tree.get("aria-label"), "missing image role/label"

# Content must never depend on an animation having run to be visible. Reveal
# animations therefore use fill-mode backwards over a visible base style; a
# base opacity:0 plus `forwards` renders a blank card wherever motion is off.
for cls in (".rise", ".draw"):
    block = re.search(re.escape(cls) + r"\s*\{([^}]*)\}", src)
    assert block, f"{cls} rule not found"
    body = block.group(1)
    assert "backwards" in body, f"{cls} must use animation-fill-mode backwards"
    assert "opacity: 0" not in body, f"{cls} is invisible until its animation runs"

# Every packet must ride a path that a drawn wire actually has, or a dot will
# float across empty space. This is the failure a quick glance hides.
# The grid <path> carries extra attributes, so this only matches the wires.
wires = set(re.findall(r'<path d="([^"]+)"/>', src))
rails = set(re.findall(r"offset-path:path\('([^']+)'\)", src))
assert rails, "no packets found"
assert rails <= wires, f"packet path with no wire: {sorted(rails - wires)}"
assert len(rails) == len(wires) == 4, f"wires={len(wires)} rails={len(rails)}"

kb = len(src.encode()) / 1024
assert kb < 40, f"header.svg is {kb:.0f} KB; it replaced a 984 KB gif for a reason"

print(f"ok  {len(rails)} wires, {kb:.1f} KB, reduced-motion + light theme present")
