"""Build the closed KEELSON profile: purple spline + frame steps + top chain + end caps.
Usage: python3 -I build_keelson.py <input.3dm> <out.3dm> <qa.png>"""
import sys, re, numpy as np, rhino3dm as R
from shapely.geometry import Polygon, LineString

src, out3dm, outpng = sys.argv[1:4]
m = R.File3dm.Read(src)
layers = [l.FullPath for l in m.Layers]
purple = None; top = {}; stairs = []; aft_top = None; aft_cap = None
for o in m.Objects:
    a, g = o.Attributes, o.Geometry; L = layers[a.LayerIndex]
    if L.startswith('03') and not a.Name: purple = g
    if L.startswith('02'):
        i = int(re.search(r'(\d+)$', a.Name).group(1))
        if 225 <= i <= 234: top[i] = g
        if i == 414: aft_cap = g
        if type(g).__name__ == 'LineCurve' and i != 229:
            s, e = g.PointAtStart, g.PointAtEnd
            if abs(s.Z - e.Z) < 1e-6 and abs(s.X - e.X) > 1:
                stairs.append((min(s.X, e.X), max(s.X, e.X), s.Z))
    if L.startswith('01') and not a.Name and type(g).__name__ == 'NurbsCurve':
        if abs(g.PointAtStart.X - 51.08) < .05 and abs(g.PointAtEnd.X - 41.25) < .05: aft_top = g
stairs.sort()
assert purple and aft_top and aft_cap and len(top) == 10, (purple, aft_top, aft_cap, len(top))

t0, t1 = purple.Domain.T0, purple.Domain.T1
def tx(x):
    lo, hi = t0, t1
    for _ in range(80):
        mid = (lo + hi) / 2
        if purple.PointAt(mid).X < x: lo = mid
        else: hi = mid
    return (lo + hi) / 2
def pz(x): return purple.PointAt(tx(x)).Z

pieces = []   # (name, curve, kind)
def line(a, b, name):
    pieces.append((name, R.LineCurve(R.Point3d(a[0], 0, a[1]), R.Point3d(b[0], 0, b[1])), 'line'))

x_start = purple.PointAtStart.X
cur = x_start
for k, (xa, xf, zt) in enumerate(stairs, 1):
    seg = purple.Trim(tx(cur), tx(xa))
    pieces.append(('PURPLE_CUT_%02d' % k, seg, 'spline'))
    za = pz(xa)
    line((xa, za), (xa, zt), 'STEP_%02d_V_AFT' % k)
    line((xa, zt), (xf, zt), 'STEP_%02d_H' % k)
    last = (k == len(stairs))
    if not last:
        zf = pz(xf)
        line((xf, zt), (xf, zf), 'STEP_%02d_V_FWD' % k)
    cur = xf
# forward cap: from last horizontal end up to top-chain end
tend = top[234].PointAtEnd
line((stairs[-1][1], stairs[-1][2]), (tend.X, tend.Z), 'CAP_FWD')
# top chain fwd -> aft
for i in range(234, 224, -1):
    c = top[i].Duplicate(); c.Reverse(); pieces.append(('TOP_%d' % i, c, 'line' if type(top[i]).__name__ == 'LineCurve' else 'spline'))
c = aft_top.Duplicate(); pieces.append(('AFT_TOP', c, 'spline'))   # (51.08,33.98)->(41.25,38.06)
c.Reverse() if c.PointAtStart.X < c.PointAtEnd.X else None
# after Reverse above the chain is aft_top running 51.08 -> 41.25 only if start was 51.08
cap = aft_cap.Duplicate()
if cap.PointAtStart.Z < cap.PointAtEnd.Z: cap.Reverse()
pieces.append(('CAP_AFT', cap, 'line'))

# continuity report
P = lambda p: np.array([p.X, p.Z])
gaps = []
for (n1, c1, _), (n2, c2, _) in zip(pieces, pieces[1:] + pieces[:1]):
    gaps.append((np.linalg.norm(P(c1.PointAtEnd) - P(c2.PointAtStart)), n1, n2))
mx = max(gaps)
print('pieces', len(pieces), 'max end-gap %.2e between %s -> %s' % mx)
bad = [g for g in gaps if g[0] > 0.2]
print('gaps > 0.2mm:', bad)

# build a polyline for validation
pts = []
for n, c, k in pieces:
    N = 2 if k == 'line' and type(c).__name__ == 'LineCurve' else 200
    d = c.Domain
    for j in range(N):
        t = d.T0 + (d.T1 - d.T0) * j / (N - 1)
        p = c.PointAt(t); pts.append((p.X, p.Z))
ded = [pts[0]]
for p in pts[1:]:
    if np.hypot(p[0]-ded[-1][0], p[1]-ded[-1][1]) > 1e-9: ded.append(p)
poly = Polygon(ded)
print('shapely valid', poly.is_valid, 'area %.1f' % poly.area, 'bounds', [round(v, 1) for v in poly.bounds])
if not poly.is_valid:
    from shapely.validation import explain_validity; print(explain_validity(poly))
# step table
print('steps', len(stairs))
for k, (xa, xf, zt) in enumerate(stairs, 1):
    va, vf = zt - pz(xa), zt - (pz(xf))
    if k in (1, len(stairs)) or min(va, vf) < 0.2: print('  step %02d  x=[%.1f,%.1f] z=%.2f  Vaft=%+.2f Vfwd=%+.2f' % (k, xa, xf, zt, va, vf))

# write 3dm
f = R.File3dm(); f.Settings.ModelUnitSystem = R.UnitSystem.Millimeters
def layer(name, rgb):
    l = R.Layer(); l.Name = name; l.Color = (*rgb, 255); return f.Layers.Add(l)
Lc = layer('10_KEELSON_CLOSED_V3', (0, 0, 0)); Ls = layer('10_KEELSON_PIECES_SPLINE', (0, 105, 225)); Ll = layer('10_KEELSON_PIECES_LINE', (20, 145, 55))
pc = R.PolyCurve()
for n, c, k in pieces:
    pc.Append(c)
    a = R.ObjectAttributes(); a.Name = 'KEELSON_V3_' + n
    a.LayerIndex = Ls if k == 'spline' else Ll
    f.Objects.AddCurve(c, a)
a = R.ObjectAttributes(); a.Name = 'KEELSON_V3_CLOSED'; a.LayerIndex = Lc
f.Objects.AddCurve(pc, a)
print('polycurve closed:', pc.IsClosed, 'valid:', pc.IsValid)
f.Write(out3dm, 7)

# QA picture
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(4, 1, figsize=(14, 15), gridspec_kw={'height_ratios': [1, 1, 1, 1]})
views = [('whole', (30, 550), (0, 45)), ('aft', (36, 130), (10, 40)), ('mid', (280, 340), (4, 14)), ('fwd', (440, 535), (8, 42))]
for ax, (t, xl, yl) in zip(axs, views):
    for n, c, k in pieces:
        d = c.Domain; q = np.array([[c.PointAt(d.T0 + (d.T1 - d.T0) * j / 120).X, c.PointAt(d.T0 + (d.T1 - d.T0) * j / 120).Z] for j in range(121)])
        ax.plot(q[:, 0], q[:, 1], color=('#1969e1' if k == 'spline' else '#149137'), lw=1.2)
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect('equal'); ax.set_title(t); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(outpng, dpi=110)
