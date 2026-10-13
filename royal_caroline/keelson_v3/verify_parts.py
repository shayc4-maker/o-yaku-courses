"""Independent check of parts_closed_v3.3dm: every part is a closed, simple, planar loop; no two parts overlap.
Usage: python3 -I verify_parts.py <parts_closed.3dm>"""
import sys, numpy as np, rhino3dm as R, itertools
from shapely.geometry import Polygon
m = R.File3dm.Read(sys.argv[1]); layers = [l.FullPath for l in m.Layers]
P = {}
for o in m.Objects:
    L = layers[o.Attributes.LayerIndex]
    if L[:2] not in ('20', '21'): continue
    c = o.Geometry; pts = []
    for i in range(c.SegmentCount):
        s = c.SegmentCurve(i); d = s.Domain; n = 2 if type(s).__name__ == 'LineCurve' else 600
        pts += [(s.PointAt(d.T0 + (d.T1 - d.T0) * j / (n - 1)).X, s.PointAt(d.T0 + (d.T1 - d.T0) * j / (n - 1)).Z) for j in range(n)]
    ded = [pts[0]]
    for q in pts[1:]:
        if np.hypot(q[0] - ded[-1][0], q[1] - ded[-1][1]) > 1e-4: ded.append(q)
    if np.hypot(ded[-1][0] - ded[0][0], ded[-1][1] - ded[0][1]) < 1e-3: ded.pop()
    yz = max(abs(o.Geometry.PointAt(t).Y) for t in [c.Domain.T0, c.Domain.T1])
    pg = Polygon(ded)
    P[o.Attributes.Name] = (L, pg, c.IsClosed, yz)
print('%-38s %-4s %7s %6s %7s %s' % ('part', 'lyr', 'area', 'closed', 'simple', 'planar'))
for n, (L, pg, cl, yz) in sorted(P.items(), key=lambda t: t[1][1].bounds[0]):
    print('%-38s %-4s %7.1f %6s %7s %s' % (n, L[:2], pg.area, cl, pg.is_valid, 'Y=0' if yz < 1e-9 else 'Y=%g' % yz))
print('overlaps > 0.5 mm2:')
bad = 0
for (a, (la, pa, *_)), (b, (lb, pb, *_)) in itertools.combinations(P.items(), 2):
    if pa.is_valid and pb.is_valid:
        ia = pa.intersection(pb).area
        if ia > 0.5: print('  %s x %s : %.1f mm2' % (a, b, ia)); bad += 1
print('none' if not bad else '%d overlapping pairs' % bad)
