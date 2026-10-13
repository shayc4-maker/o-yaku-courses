"""Rebuild the hog/backbone upper contour (layer 01, BODY_OUTER_V2_19..198) the way the keelson was done:
one smooth base spline + frame steps inserted into it (verticals/horizontals kept exact).
The seat height of every step is the user's; the base spline passes through the user's own corner points
(the lower end of each step), so nothing is invented.
Usage: python3 -I smooth_contour.py <v2.3dm> <out.3dm> <qa.png>"""
import sys, numpy as np, rhino3dm as R
from scipy.interpolate import PchipInterpolator
src, out3dm, outpng = sys.argv[1:4]
m = R.File3dm.Read(src); layers = [l.FullPath for l in m.Layers]
C = {}
for o in m.Objects:
    a = o.Attributes
    if layers[a.LayerIndex].startswith('01') and a.Name.startswith('BODY_OUTER_V2_'):
        C[int(a.Name.split('_')[-1])] = o.Geometry
lo_id, hi_id = 19, 198
def ends(g): return (g.PointAtStart.X, g.PointAtStart.Z), (g.PointAtEnd.X, g.PointAtEnd.Z)
# ---- notches: every horizontal line with a vertical before and after ----
notches = []
for k in sorted(C):
    if not (lo_id <= k <= hi_id): continue
    g = C[k]
    if type(g).__name__ != 'LineCurve': continue
    (xs, zs), (xe, ze) = ends(g)
    if abs(zs - ze) < 1e-9 and abs(xs - xe) > 1 and (k - 1) in C and (k + 1) in C:
        va, vf = C[k - 1], C[k + 1]
        (ax0, az0), (ax1, az1) = ends(va); (fx0, fz0), (fx1, fz1) = ends(vf)
        xa, xf = min(xs, xe), max(xs, xe)
        za_top = az0 if abs(ax1 - xa) < 1e-6 and abs(az1 - zs) < 1e-6 else az1
        zf_top = fz1 if abs(fx0 - xf) < 1e-6 and abs(fz0 - zs) < 1e-6 else fz0
        notches.append(dict(k=k, xa=xa, xf=xf, zs=zs, za_top=za_top, zf_top=zf_top))
notches.sort(key=lambda n: n['xa'])
print('notches', len(notches), 'x', notches[0]['xa'], '..', notches[-1]['xf'])
# ---- base-spline points: the LOWER end of each step (vertical = exactly the user's 1 mm there) ----
X_FLIP = 135.0     # the contour falls aft of here and rises forward of here
pts = []
n18 = C[18]; d = n18.Domain
for t in np.linspace(d.T0, d.T1, 8)[:-1]:
    p = n18.PointAt(t); pts.append((p.X, p.Z))                     # tail of the smooth deadwood edge keeps the tangent
for n in notches:
    if (n['xa'] + n['xf']) / 2 < X_FLIP: pts.append((n['xf'], n['zf_top']))
    else: pts.append((n['xa'], n['za_top']))
x_end = notches[-1]['xf']; z_end = C[hi_id].PointAtEnd.Z
pts.append((x_end, z_end))
(x0, z0), _ = ends(C[19]); pts.append((x0, z0)); pts.sort()
P = np.array(pts); keep = np.r_[True, np.diff(P[:, 0]) > 0.05]; P = P[keep]
S = PchipInterpolator(P[:, 0], P[:, 1])
# ---- dense control-point curve of S ----
xs = np.r_[np.arange(x0, 500, 1.0), np.arange(500, x_end, 0.5), x_end]
base = R.Curve.CreateControlPointCurve([R.Point3d(x, 0, float(S(x))) for x in xs], 3)
t0, t1 = base.Domain.T0, base.Domain.T1
def tx(x):
    lo, hi = t0, t1
    for _ in range(70):
        mid = (lo + hi) / 2
        if base.PointAt(mid).X < x: lo = mid
        else: hi = mid
    return (lo + hi) / 2
dev = max(abs(base.PointAt(tx(x)).Z - float(S(x))) for x in np.arange(x0, x_end, 0.7))
print('base spline vs PCHIP max deviation %.4f mm' % dev)
# ---- assemble ----
pieces = []
def line(a, b, name): pieces.append((name, R.LineCurve(R.Point3d(a[0], 0, a[1]), R.Point3d(b[0], 0, b[1])), 'line'))
cur = x0; neg = []
for i, n in enumerate(notches, 1):
    if n['xa'] - cur > 1e-6: pieces.append(('GAP_%02d' % i, base.Trim(tx(cur), tx(n['xa'])), 'spline'))
    za, zf = float(base.PointAt(tx(n['xa'])).Z), float(base.PointAt(tx(n['xf'])).Z)
    va, vf = za - n['zs'], zf - n['zs']
    if min(va, vf) < 0.05: neg.append((i, round(n['xa'], 1), round(va, 2), round(vf, 2)))
    line((n['xa'], za), (n['xa'], n['zs']), 'STEP_%02d_V_AFT' % i)
    line((n['xa'], n['zs']), (n['xf'], n['zs']), 'STEP_%02d_H' % i)
    line((n['xf'], n['zs']), (n['xf'], zf), 'STEP_%02d_V_FWD' % i)
    cur = n['xf']
print('steps with a vertical < 0.05 mm (or reversed):', neg)
vs = [(float(base.PointAt(tx(n['xa'])).Z) - n['zs'], float(base.PointAt(tx(n['xf'])).Z) - n['zs']) for n in notches]
print('vertical lengths: min %.2f max %.2f' % (min(min(v) for v in vs), max(max(v) for v in vs)))
gaps = [np.hypot(a[1].PointAtEnd.X - b[1].PointAtStart.X, a[1].PointAtEnd.Z - b[1].PointAtStart.Z) for a, b in zip(pieces, pieces[1:])]
print('pieces', len(pieces), 'max end gap %.2e' % max(gaps))
# ---- write ----
f = R.File3dm(); f.Settings.ModelUnitSystem = R.UnitSystem.Millimeters
def layer(nm, rgb): l = R.Layer(); l.Name = nm; l.Color = (*rgb, 255); return f.Layers.Add(l)
Lc, Lb, Lp = layer('30_HOG_CONTOUR_V3', (0, 0, 0)), layer('31_HOG_BASE_SPLINE_EDITABLE', (190, 50, 150)), layer('32_HOG_CONTOUR_PIECES', (120, 120, 120))
pc = R.PolyCurve()
for nm, c, k in pieces:
    pc.Append(c); a = R.ObjectAttributes(); a.Name = 'HOGC_' + nm; a.LayerIndex = Lp; f.Objects.AddCurve(c, a)
a = R.ObjectAttributes(); a.Name = 'HOG_CONTOUR_V3'; a.LayerIndex = Lc; f.Objects.AddCurve(pc, a)
a = R.ObjectAttributes(); a.Name = 'HOG_BASE_SPLINE'; a.LayerIndex = Lb; f.Objects.AddCurve(base, a)
f.Write(out3dm, 7)
# ---- QA: old (red) vs new (black) ----
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def pl(c, n=300):
    d = c.Domain; n = 2 if type(c).__name__ == 'LineCurve' else n; q = [c.PointAt(d.T0 + (d.T1 - d.T0) * j / (n - 1)) for j in range(n)]
    return np.array([[p.X, p.Z] for p in q])
fig, axs = plt.subplots(4, 1, figsize=(15, 20))
for ax, (t, xl, yl) in zip(axs, [('aft 36-140', (34, 140), (0, 14)), ('mid 280-340', (280, 340), (1, 5)), ('fwd 420-530', (420, 530), (0, 36)), ('whole', (30, 535), (0, 40))]):
    for k in sorted(C):
        if lo_id <= k <= hi_id: q = pl(C[k]); ax.plot(q[:, 0], q[:, 1], color='#d33', lw=1.0)
    for nm, c, kind in pieces: q = pl(c); ax.plot(q[:, 0], q[:, 1], color='k', lw=1.2)
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect('equal'); ax.set_title(t + '   red = old, black = new'); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(outpng, dpi=75)
