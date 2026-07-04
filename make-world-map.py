# Generates rendered/assets/world-map.svg from Natural Earth data
# (world-atlas countries json). Run once: python3 make-world-map.py
#
# Miller projection — the classic wall-map look (no polar squash), as a flat
# 360-degree strip that tiles seamlessly side-by-side, so the site can pan it
# in an endless horizontal loop.
# - each country is one <path> with data-name for styling/clicks
# - faint 30-degree graticule
# - rings crossing the antimeridian (Russia, Fiji) are unwrapped + mirrored,
#   so each copy of the strip is complete at both edges
import json
import math
import os

SRC_50M = '/tmp/countries-50m.json'
SRC_110M = '/tmp/countries-110m.json'
OUT = 'rendered/assets/world-map.svg'
# Crop: 84N (just above Greenland) down to -64.5S — only the tip of the
# Antarctic Peninsula peeks in at the bottom edge as a teaser; the rest of
# Antarctica (and the empty Southern Ocean band) stays off-map.
LAT_TOP, LAT_BOT = 84.0, -66.0
WIDTH = 1000.0
DEG = math.pi / 180.0

def miller_y(lat):
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * lat * DEG))

Y_TOP = miller_y(LAT_TOP)
Y_BOT = miller_y(LAT_BOT)
SCALE = WIDTH / (2 * math.pi)         # px per projection unit
HEIGHT = (Y_TOP - Y_BOT) * SCALE

def project(lon, lat):
    x = (lon * DEG + math.pi) * SCALE
    y = (Y_TOP - miller_y(lat)) * SCALE
    return x, y
MAX_KB = 520                          # fall back to 110m if 50m comes out huge

def fmt(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s

def simplify(pts, tol):
    # Douglas-Peucker in projected pixel space. Run on the shared topology
    # arcs (not per-country rings) so neighbouring borders stay welded.
    if len(pts) < 3:
        return pts
    proj = [project(lon, lat) for lon, lat in pts]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = proj[a]
        bx, by = proj[b]
        dx, dy = bx - ax, by - ay
        seg2 = dx * dx + dy * dy
        worst, wdist = -1, tol * tol
        for i in range(a + 1, b):
            px, py = proj[i]
            if seg2 == 0:
                ex, ey = px - ax, py - ay
            else:
                t = ((px - ax) * dx + (py - ay) * dy) / seg2
                t = 0 if t < 0 else (1 if t > 1 else t)
                ex, ey = px - (ax + t * dx), py - (ay + t * dy)
            d2 = ex * ex + ey * ey
            if d2 > wdist:
                worst, wdist = i, d2
        if worst >= 0:
            keep[worst] = True
            stack.append((a, worst))
            stack.append((worst, b))
    return [p for p, k in zip(pts, keep) if k]

def build_from(src, tol=0.0):
    topo = json.load(open(src))
    scale = topo['transform']['scale']
    translate = topo['transform']['translate']

    def decode_arc(arc):
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * scale[0] + translate[0], y * scale[1] + translate[1]))
        return pts

    arcs = [decode_arc(a) for a in topo['arcs']]
    if tol > 0:
        arcs = [simplify(a, tol) for a in arcs]

    def ring_points(ring):
        pts = []
        for idx in ring:
            seg = arcs[~idx][::-1] if idx < 0 else arcs[idx]
            if pts:
                seg = seg[1:]
            pts.extend(seg)
        return pts

    def unwrap(pts):
        out = []
        offset = 0.0
        prev = None
        for lon, lat in pts:
            if prev is not None:
                if lon - prev > 180.0:
                    offset -= 360.0
                elif lon - prev < -180.0:
                    offset += 360.0
            prev = lon
            out.append((lon + offset, lat))
        return out

    def ring_path(ring):
        # Each ring is drawn ONCE, unwrapped — rings that cross the
        # antimeridian simply extend past the 0..1000 edge. The page renders
        # the strip with overflow:visible and tiles three copies, so the
        # overflow lands exactly on the neighbouring copy. (Duplicated
        # shifted subpaths caused fill artifacts on Antarctica and huge
        # bounding boxes that broke browser paint culling on Russia.)
        pts = unwrap(ring_points(ring))
        proj = [project(lon, lat) for lon, lat in pts]
        coords = []
        last = None
        for x, y in proj:
            c = (fmt(x), fmt(y))
            if c != last:
                coords.append(f'{c[0]} {c[1]}')
                last = c
        if len(coords) < 3:
            return ''
        return 'M' + ' '.join(coords) + 'Z'

    paths = []
    for geom in topo['objects']['countries']['geometries']:
        name = geom.get('properties', {}).get('name', '?')
        if geom['type'] == 'Polygon':
            polys = [geom['arcs']]
        elif geom['type'] == 'MultiPolygon':
            polys = geom['arcs']
        else:
            continue
        d = ''.join(ring_path(ring) for poly in polys for ring in poly)
        if not d:
            continue
        safe = name.replace('&', '&amp;').replace('"', '&quot;')
        paths.append(f'<path class="country" data-name="{safe}" d="{d}"/>')
    return paths

# faint graticule every 30 degrees (straight lines in cylindrical projections)
grat = []
for lon in range(-150, 151, 30):
    x, y0 = project(lon, LAT_TOP)
    _, y1 = project(lon, LAT_BOT)
    grat.append(f'M{fmt(x)} {fmt(y0)}L{fmt(x)} {fmt(y1)}')
for lat in range(-30, 61, 30):
    x0, y = project(-180, lat)
    x1, _ = project(180, lat)
    grat.append(f'M{fmt(x0)} {fmt(y)}L{fmt(x1)} {fmt(y)}')
grat_d = ''.join(grat)

def render(paths):
    # Clip vertically only: the rect is much wider than the viewBox so
    # dateline-crossing land can still bleed onto the neighbouring tiled
    # copy, but Antarctica's below-crop skirt is cut off.
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH:.0f} {HEIGHT:.0f}" '
        f'preserveAspectRatio="xMidYMid meet">\n'
        f'<defs><clipPath id="vclip"><rect x="-1500" y="0" width="4000" height="{HEIGHT:.0f}"/></clipPath></defs>\n'
        f'<g clip-path="url(#vclip)">\n'
        f'<path class="grat" d="{grat_d}"/>\n'
        + '\n'.join(paths) +
        '\n</g>\n</svg>\n'
    )

# 50m coastlines, simplified to ~1/3px tolerance — crisp at page size but small
paths = build_from(SRC_50M, tol=0.35)
body = render(paths)
if len(body) // 1024 > MAX_KB:
    print(f'50m output {len(body) // 1024}KB > {MAX_KB}KB cap — falling back to 110m')
    paths = build_from(SRC_110M)
    body = render(paths)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w').write(body)
print(f'wrote {OUT}: {len(paths)} countries, {len(body) // 1024}KB, viewBox 0 0 {WIDTH:.0f} {HEIGHT:.0f}')
