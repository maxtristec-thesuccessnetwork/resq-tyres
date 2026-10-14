#!/usr/bin/env python3
"""Cut photo derivatives at the shape the page shows them, from the graded masters,
with number plates blurred.

    python3 tools/crop-photos.py

The masters in assets/ are already graded (tools/grade-photos.py writes the graded
master back over the original), so this only blurs plates, crops, resizes and encodes:
never re-grade a master, and never edit a master in place.

A derivative cut at the image's own shape but shown through `object-fit: cover`
in a box of another shape downloads pixels nobody sees. Cutting it at the box's
shape gives the same picture for fewer bytes, which matters most for the first
photo on a page (the largest contentful paint).

  PLATES[master] = boxes (left, top, right, bottom, in master pixels) blurred before
                   any cut, so no derivative shows a readable number plate.
  LETTERING[master] = the service list on the van's side door, lightly blurred (the text is small). It
                   lists "Battery replacement" and "Wheel alignment", which the business
                   doesn't offer, so no derivative may show it readable. The "24 Hour Mobile
                   Tyres" line, the name and the phone number stay sharp.
  CROPS[master]  = list of (aspect w/h of the box it fills, vertical focus 0-1, widths, name)

  * hero-resq: the home and Wakefield hero box is aspect-ratio 4/4.2 with
    object-position center 40%, so the crop keeps the same 40% point.
  * van: the jump-start hero (same 4/4.2 box), the van section and service
    (4:5, the photo's own shape), the square home service card, and the 1200x630 share image.
  * roadside-fit: the Harrogate hero (4/4.2) and the square service cards.
  * wheelchange: the /emergency proof photo, shown full width at up to 280px
    tall (about 4:3 on a phone), the square service cards, and the Wakefield
    hero (4/4.2), so Wakefield no longer reuses the home page's hero photo.

Files under /assets are served immutable for a year, so a new cut always gets a
new file name.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
QUALITY = 68   # about what the live -v2 files use, so the look does not change

PLATES = {
    "hero-resq.jpg":    [(160, 948, 248, 1036), (36, 746, 74, 780), (840, 652, 888, 672)],
    "van.jpg":          [(886, 782, 998, 852)],
    "roadside-fit.jpg": [(710, 470, 916, 564), (80, 217, 148, 247), (874, 209, 939, 240)],
    "wheelchange.jpg":  [(16, 598, 114, 674), (746, 406, 808, 438)],
}

LETTERING = {
    "hero-resq.jpg":    [(436, 556, 552, 644)],
    "van.jpg":          [(290, 532, 382, 648)],
}

CROPS = {
    "hero-resq.jpg":    [(4 / 4.2, 0.40, [600, 760, 900], "hero-resq-{w}-v5.webp")],
    "van.jpg":          [(4 / 4.2, 0.30, [600, 760, 900], "van-hero-{w}-v2.webp"),
                         (4 / 5, 0.50, [420, 760, 1100], "van-{w}-v4.webp"),
                         (1, 0.42, [420, 760], "van-sq-{w}-v2.webp"),
                         (1200 / 630, 0.4625, [1200], "share-{w}x630-v3.jpg")],
    "roadside-fit.jpg": [(4 / 4.2, 0.50, [420, 760], "roadside-fit-hero-{w}.webp"),
                         (1, 0.50, [420, 760], "roadside-fit-{w}-v3.webp")],
    "wheelchange.jpg":  [(4 / 3, 0.50, [420, 760], "wheelchange-4x3-{w}-v2.webp"),
                         (1, 0.50, [420, 760], "wheelchange-{w}-v3.webp"),
                         (4 / 4.2, 0.50, [420, 760], "wheelchange-hero-{w}.webp")],
}


def blur_plates(img, boxes, pad=None, sigma=None):
    for (l, t, r, b) in boxes:
        p = pad or max(6, (b - t) // 2)
        box = (max(0, l - p), max(0, t - p), min(img.width, r + p), min(img.height, b + p))
        region = img.crop(box).filter(ImageFilter.GaussianBlur(sigma or max(6, (b - t) * 0.45)))
        mask = Image.new("L", region.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((p // 2, p // 2, region.width - p // 2, region.height - p // 2),
                                               radius=p, fill=255)
        img.paste(region, box[:2], mask.filter(ImageFilter.GaussianBlur(p / 3)))
    return img


def crop_to(img, aspect, focus_y):
    w, h = img.size
    if w / h > aspect:                      # too wide: trim the sides, centred
        nw = round(h * aspect)
        x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    nh = round(w / aspect)                  # too tall: trim top and bottom around focus_y
    y = round((h - nh) * focus_y)
    return img.crop((0, y, w, y + nh))


def main():
    for master, cuts in CROPS.items():
        src = blur_plates(Image.open(os.path.join(ASSETS, master)).convert("RGB"), PLATES.get(master, []))
        # the door text is small, so a light blur makes it unreadable without fogging the van
        src = blur_plates(src, LETTERING.get(master, []), pad=8, sigma=7)
        for aspect, focus_y, widths, name in cuts:
            img = crop_to(src, aspect, focus_y)
            for w in widths:
                out = os.path.join(ASSETS, name.format(w=w))
                small = img.resize((w, round(w / aspect)), Image.LANCZOS)
                if out.endswith(".jpg"):
                    small.save(out, "JPEG", quality=85, optimize=True, progressive=True)
                else:
                    small.save(out, "WEBP", quality=QUALITY, method=6)
                print(f"{os.path.basename(out)}  {small.width}x{small.height}  {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    main()
