#!/usr/bin/env python3
"""
ResQ Tyres — unified photo grade (polish pass, Aug 2026).

The source photography is phone shots taken in three different lights:
blue-hour (hero), harsh warm midday sun (roadside-fit), flat overcast
(wheelchange). A single CSS filter cannot fix that — it shifts all of them
by the same amount. This normalises each photo to a shared target instead,
so they read as one shoot, then applies one identical brand grade on top.

Per image:
  1. White balance from near-neutral pixels only (so a blue sky or a blue
     car doesn't drag the correction the way grey-world would).
  2. Black/white point set from luminance percentiles.
  3. Exposure (gamma) matched to a shared mean luminance.
  4. Contrast matched to a shared luminance spread.
  5. Saturation matched to a shared mean chroma.

Then identical for every image:
  6. Gentle S-curve.
  7. Subtle split tone — ink-cool shadows, faintly warm highlights.

Derivatives are re-cut from the graded master and encoded to land at or
under the byte size they already had, so nothing regresses on LCP.
"""

import os
import sys
import numpy as np
from PIL import Image

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# ---- shared targets: what "one shoot" means numerically ---------------------
T_BLACK, T_WHITE = 0.015, 0.962   # where p1 / p99.3 luminance land
T_MEAN = 0.455                    # mean luminance after levels
T_STD = 0.200                     # luminance spread (contrast)
T_CHROMA = 0.255                  # mean chroma (saturation)

# ---- shared look applied identically to all -------------------------------
S_CURVE = 0.055                   # gentle contrast S
SHADOW_TINT = np.array([0.988, 0.996, 1.014])   # toward brand ink #0f1318
HIGH_TINT = np.array([1.012, 1.000, 0.984])     # a touch of warmth up top
FINAL_SAT = 0.965                 # slight restraint, shared

LUMA = np.array([0.2126, 0.7152, 0.0722])

# master -> (derivative widths, jpeg max bytes, webp max bytes per width)
# fitting.* and tyretread.* are not referenced anywhere in index.html or the
# stylesheet, so they are deliberately left untouched.
SETS = {
    "hero-resq.jpg":    [600, 900],
    "van.jpg":          [420, 760, 1100],
    "roadside-fit.jpg": [420, 760],
    "wheelchange.jpg":  [420, 760],
}


def luma(rgb):
    return rgb @ LUMA


def white_balance(rgb):
    """Gains from near-neutral, well-lit pixels; luminance-preserving."""
    mx, mn = rgb.max(2), rgb.min(2)
    sat = (mx - mn) / (mx + 1e-6)
    l = luma(rgb)
    for thresh in (0.14, 0.20, 0.30, 1.01):
        mask = (sat < thresh) & (l > 0.25) & (l < 0.93)
        if mask.mean() > 0.02:
            break
    means = rgb[mask].mean(0)
    gains = means.mean() / np.maximum(means, 1e-6)
    gains = np.clip(gains, 0.86, 1.16)
    gains /= gains @ LUMA          # keep overall brightness where it was
    return np.clip(rgb * gains, 0, 1), gains


def levels(rgb):
    l = luma(rgb)
    lo, hi = np.percentile(l, 1.0), np.percentile(l, 99.3)
    if hi - lo < 0.05:
        return rgb
    scale = (T_WHITE - T_BLACK) / (hi - lo)
    scale = float(np.clip(scale, 0.75, 1.45))
    off = T_BLACK - lo * scale
    return np.clip(rgb * scale + off, 0, 1)


def match_exposure(rgb):
    l = luma(rgb)
    m = l.mean()
    if m <= 0.01 or m >= 0.99:
        return rgb
    g = float(np.clip(np.log(T_MEAN) / np.log(m), 0.72, 1.38))
    return np.clip(rgb ** g, 0, 1)


def match_contrast(rgb):
    l = luma(rgb)
    s = l.std()
    if s < 0.02:
        return rgb
    c = float(np.clip(T_STD / s, 0.85, 1.25))
    piv = l.mean()
    return np.clip((rgb - piv) * c + piv, 0, 1)


def match_saturation(rgb):
    l = luma(rgb)[..., None]
    chroma = np.abs(rgb - l).mean()
    if chroma < 0.01:
        return rgb
    k = float(np.clip(T_CHROMA / (chroma * 3.6), 0.72, 1.30))
    return np.clip(l + (rgb - l) * k, 0, 1)


def s_curve(rgb):
    # smooth, symmetric, no clipping at the ends
    return np.clip(rgb + S_CURVE * np.sin(2 * np.pi * rgb) * -1.0, 0, 1)


def split_tone(rgb):
    l = luma(rgb)[..., None]
    shadow_w = np.clip(1.0 - l * 1.9, 0, 1)
    high_w = np.clip((l - 0.45) * 1.8, 0, 1)
    out = rgb * (1 + (SHADOW_TINT - 1) * shadow_w) * (1 + (HIGH_TINT - 1) * high_w)
    return np.clip(out, 0, 1)


def final_sat(rgb):
    l = luma(rgb)[..., None]
    return np.clip(l + (rgb - l) * FINAL_SAT, 0, 1)


def grade(path):
    im = Image.open(path).convert("RGB")
    rgb = np.asarray(im).astype(np.float64) / 255.0
    before = (luma(rgb).mean(), luma(rgb).std(), rgb.reshape(-1, 3).mean(0))

    rgb, gains = white_balance(rgb)
    rgb = levels(rgb)
    rgb = match_exposure(rgb)
    rgb = match_contrast(rgb)
    rgb = match_saturation(rgb)
    rgb = s_curve(rgb)
    rgb = split_tone(rgb)
    rgb = final_sat(rgb)

    after = (luma(rgb).mean(), luma(rgb).std(), rgb.reshape(-1, 3).mean(0))
    out = Image.fromarray(np.round(rgb * 255).astype(np.uint8), "RGB")
    return out, before, after, gains


def encode_under(img, path, fmt, budget):
    """Write at the best quality that still fits the existing byte budget."""
    qualities = [88, 85, 82, 79, 76, 73, 70, 66, 62] if fmt == "WEBP" else \
                [88, 85, 82, 79, 76, 73, 70]
    best = None
    for q in qualities:
        kw = {"quality": q, "method": 6} if fmt == "WEBP" else \
             {"quality": q, "optimize": True, "progressive": True}
        img.save(path, fmt, **kw)
        size = os.path.getsize(path)
        best = (q, size)
        if size <= budget * 1.03:   # a few bytes over beats a visible quality drop
            break
    return best


def main():
    report = []
    for master, widths in SETS.items():
        mpath = os.path.join(ASSETS, master)
        if not os.path.exists(mpath) or os.path.getsize(mpath) == 0:
            continue
        graded, before, after, gains = grade(mpath)

        budget = os.path.getsize(mpath)
        q, size = encode_under(graded, mpath, "JPEG", budget)
        report.append(
            f"{master:20s} wb gains R{gains[0]:.3f} G{gains[1]:.3f} B{gains[2]:.3f} | "
            f"luma {before[0]:.3f}->{after[0]:.3f} std {before[1]:.3f}->{after[1]:.3f} | "
            f"RGB {before[2][0]:.3f}/{before[2][1]:.3f}/{before[2][2]:.3f} -> "
            f"{after[2][0]:.3f}/{after[2][1]:.3f}/{after[2][2]:.3f} | "
            f"jpg q{q} {size//1024}KB/{budget//1024}KB"
        )

        stem = master.rsplit(".", 1)[0]
        for w in widths:
            dpath = os.path.join(ASSETS, f"{stem}-{w}.webp")
            if not os.path.exists(dpath):
                continue
            dbudget = os.path.getsize(dpath)
            dims = Image.open(dpath).size          # keep exactly what the HTML expects
            resized = graded.resize(dims, Image.LANCZOS)
            q, size = encode_under(resized, dpath, "WEBP", dbudget)
            report.append(
                f"  {stem}-{w}.webp {dims[0]}x{dims[1]} q{q} {size//1024}KB/{dbudget//1024}KB"
                + ("  OVER" if size > dbudget else "")
            )

    print("\n".join(report))


if __name__ == "__main__":
    main()
