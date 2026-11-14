"""food-picture-01 entry (Python 3.13, standard library only).

Draws one picture — a steaming bowl of ramen on a warm wooden table — and
writes it to /output/entry.png (1024x1024 PNG, < 1 MiB).

The idea, against the judge's criteria (an AI judge compares pictures two at
a time and picks the better-looking food picture): one dish, close up, warm
and glossy — golden broth, noodle swirls, two soft eggs, chashu, green
onions, nori and chopsticks, with steam rising and a soft window light, so
the picture reads as appetising even at ~300 px. No faces, no text, no
gimmick: the food is the whole picture.

How it is drawn: pure stdlib. The scene is computed pixel by pixel
(wood table, bowl, broth with noodle swirls, toppings, steam, chopsticks),
then encoded as PNG by hand (zlib + struct + CRC32). No PIL, no network, no
randomness — the same bytes on every run.
"""
import math
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# Palette (r, g, b).
WOOD_TOP = (126, 76, 44)
WOOD_BOT = (82, 46, 26)
LIGHT_COL = (255, 200, 130)
SHADOW_COL = (52, 28, 14)
BOWL_BODY = (178, 62, 38)      # terracotta
BOWL_DARK = (122, 40, 26)
BOWL_FOOT = (104, 34, 22)
RIM_COL = (246, 231, 205)      # cream rim
RIM_SHADE = (214, 190, 158)
BROTH = (216, 140, 54)
BROTH_LITE = (236, 168, 74)
NOODLE = (242, 206, 132)
EGG_WHITE = (250, 244, 228)
YOLK = (232, 140, 40)
YOLK_HI = (255, 202, 112)
CHASHU = (196, 110, 78)
CHASHU_RIM = (224, 152, 112)
NORI = (22, 38, 24)
ONION = (74, 160, 74)
ONION_DARK = (46, 120, 52)
SEED = (250, 236, 200)
STICK = (150, 100, 52)
STICK_HI = (192, 142, 82)
STEAM_COL = (255, 250, 240)

# Geometry.
BOWL = (512, 700, 370, 250)    # body ellipse cx, cy, rx, ry
RIM = (512, 560, 370, 130)     # rim ellipse
BROTH_E = (512, 560, 325, 108)  # broth ellipse
FOOT = (512, 905, 140, 22)
EGGS = [(398, 548, 54, 34), (636, 584, 54, 34)]  # cx, cy, rx, ry
CHASHU_D = [(516, 606, 48), (606, 540, 42)]      # cx, cy, r
NORI_POLY = [(296, 398), (338, 392), (344, 560), (300, 566)]  # raised top: the sheet now visibly sticks up above the rim behind the egg (was 424/430, barely peeking out)
ONIONS = [(300, 520, 7), (360, 620, 6), (430, 500, 7), (470, 640, 6),
          (560, 500, 7), (700, 520, 6), (730, 600, 7), (680, 640, 6),
          (340, 580, 6), (580, 650, 6), (760, 560, 6), (250, 560, 6)]
SEEDS = [(330, 540), (380, 600), (450, 520), (500, 580), (560, 630),
         (620, 500), (690, 580), (740, 530), (420, 650), (660, 630),
         (300, 600), (540, 540), (710, 610), (470, 560)]
STICKS = [((700, 330), (982, 248)), ((688, 362), (968, 282))]
STEAM = [(380, 0.0), (512, 2.1), (644, 4.2)]  # base x, phase


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def clamp(v, lo=0.0, hi=255.0):
    return lo if v < lo else hi if v > hi else v


def _ellipse(x, y, cx, cy, rx, ry):
    dx = (x - cx) / rx
    dy = (y - cy) / ry
    return dx * dx + dy * dy


def _in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xin = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xin:
                inside = not inside
        j = i
    return inside


def _seg_dist(x, y, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else ((x - x0) * dx + (y - y0) * dy) / L2
    t = max(0.0, min(1.0, t))
    px, py = x0 + t * dx, y0 + t * dy
    return math.hypot(x - px, y - py)


def pixel(x, y):
    # --- wooden table: vertical gradient + grain + warm window light ---
    t = y / H
    c = mix(WOOD_TOP, WOOD_BOT, t)
    grain = math.sin(y * 0.045 + math.sin(x * 0.008) * 3.0) * 0.5 + 0.5
    c = mix(c, WOOD_BOT, grain * 0.18)
    if abs(y - 300) < 2 or abs(y - 640) < 2:
        c = mix(c, SHADOW_COL, 0.35)
    dx, dy = x - 300, y - 200
    d = math.sqrt(dx * dx + dy * dy)
    if d < 700:
        c = mix(c, LIGHT_COL, (1.0 - d / 700.0) ** 2 * 0.30)

    # --- soft shadow under the bowl ---
    if _ellipse(x, y, 512, 930, 385, 42) < 1.0:
        c = mix(c, SHADOW_COL, 0.35)

    # --- bowl body ---
    if _ellipse(x, y, *BOWL) < 1.0:
        bt = (y - 450) / 500.0
        c = mix(BOWL_BODY, BOWL_DARK, max(0.0, min(1.0, bt)))
        if x < 330:  # lit left edge
            c = mix(c, LIGHT_COL, 0.18 * (1.0 - (x - 142) / 190.0))
        if _ellipse(x, y, *FOOT) < 1.0:
            c = BOWL_FOOT

    # --- rim ring ---
    if _ellipse(x, y, *RIM) < 1.0:
        c = RIM_COL
        if y < 560 and _ellipse(x, y, RIM[0], RIM[1], 350, 112) > 1.0:
            c = mix(c, (255, 255, 255), 0.25)

    # --- broth ---
    if _ellipse(x, y, *BROTH_E) < 1.0:
        e = _ellipse(x, y, *BROTH_E)
        c = mix(BROTH_LITE, BROTH, e)
        # noodle swirls: wavy strands across the broth
        sw = math.sin((x * 0.9 + y * 1.7) * 0.12) + math.sin(
            math.hypot(x - 512, (y - 560) * 3.0) * 0.22)
        if sw > 1.25:
            c = mix(c, NOODLE, 0.85)
        # glossy highlight on the broth
        if _ellipse(x, y, 400, 520, 150, 42) < 1.0:
            c = mix(c, (255, 220, 150), 0.22)

    # --- chashu slices ---
    for cx, cy, r in CHASHU_D:
        dd = math.hypot(x - cx, y - cy)
        if dd < r:
            c = CHASHU_RIM if dd > r * 0.72 else CHASHU
            if dd < r * 0.30:
                c = mix(c, (150, 78, 56), 0.5)

    # --- egg halves: white + yolk + highlight ---
    for cx, cy, rx, ry in EGGS:
        if _ellipse(x, y, cx, cy, rx, ry) < 1.0:
            c = EGG_WHITE
            if _ellipse(x, y, cx, cy, 22, 15) < 1.0:
                c = YOLK
                if _ellipse(x, y, cx - 6, cy - 5, 7, 5) < 1.0:
                    c = YOLK_HI

    # --- nori sheet sticking up behind the egg ---
    if _in_poly(x, y, NORI_POLY):
        c = NORI

    # --- green onion rings + sesame seeds on the broth ---
    if _ellipse(x, y, *BROTH_E) < 1.0:
        for ox, oy, r in ONIONS:
            dd = math.hypot(x - ox, y - oy)
            if r - 2 < dd < r:
                c = ONION
            elif dd <= r - 2:
                c = ONION_DARK
        for sx, sy in SEEDS:
            if math.hypot(x - sx, y - sy) < 2.5:
                c = SEED

    # --- steam: three wavy translucent columns above the bowl ---
    if 120 < y < 480:
        for bx, ph in STEAM:
            cx = bx + 28 * math.sin(y * 0.018 + ph)
            w = 26
            if abs(x - cx) < w:
                a = (1.0 - abs(x - cx) / w) * (1.0 - (y - 120) / 360.0) * 0.30
                c = mix(c, STEAM_COL, a)

    # --- chopsticks resting on the rim, upper right ---
    for (x0, y0), (x1, y1) in STICKS:
        d = _seg_dist(x, y, x0, y0, x1, y1)
        if d < 5.0:
            c = STICK_HI if d < 1.8 else STICK

    # --- vignette: darken the corners ---
    dc = math.hypot(x - 512, y - 512) / 720.0
    if dc > 0.78:
        c = mix(c, (40, 20, 10), min(0.45, (dc - 0.78) * 1.4))
    return c


def render():
    buf = [[(0, 0, 0)] * W for _ in range(H)]
    for y in range(H):
        row = buf[y]
        for x in range(W):
            r, g, b = pixel(x, y)
            row[x] = (int(clamp(r)), int(clamp(g)), int(clamp(b)))
    return buf


def png_bytes(buf):
    raw = bytearray()
    for row in buf:
        raw.append(0)
        for r, g, b in row:
            raw.extend((r, g, b))
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    data = png_bytes(render())
    (out_dir / "entry.png").write_bytes(data)


if __name__ == "__main__":
    main()
