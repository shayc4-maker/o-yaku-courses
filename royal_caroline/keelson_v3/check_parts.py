"""Planar-closure check for all backbone parts: polygonize the line work, list faces, dangles, gaps.
Usage: python3 -I check_parts.py <v2.3dm> <keelson_closed_v3.3dm>"""
import sys, re, numpy as np, rhino3dm as R
from shapely.geometry import LineString, Point, MultiPoint
from shapely.ops import unary_union, polygonize_full, snap
m = R.File3dm.Read(sys.argv[1]); k = R.File3dm.Read(sys.argv[2])
layers = [l.FullPath for l in m.Layers]
def pl(c):
    d = c.Domain; t = type(c).__name__
    n = 2 if t == 'LineCurve' else 300
    return [(c.PointAt(d.T0 + (d.T1 - d.T0) * j / (n - 1)).X, c.PointAt(d.T0 + (d.T1 - d.T0) * j / (n - 1)).Z) for j in range(n)]
src = []   # (layer, name, LineString)
for o in m.Objects:
    a, g = o.Attributes, o.Geometry; L = layers[a.LayerIndex]
    if L[:2] in ('00', '98'): continue
    if L.startswith('02'): continue          # keelson: replaced by the new closed profile
    if L.startswith('03') and not a.Name and type(g).__name__ == 'NurbsCurve': continue  # the full purple spline
    if type(g).__name__ == 'PolyCurve':      # explode joined review-like curves
        for i in range(g.SegmentCount): src.append((L[:2], a.Name or '?', LineString(pl(g.SegmentCurve(i)))))
    else: src.append((L[:2], a.Name or '?', LineString(pl(g))))
for o in k.Objects:
    if o.Attributes.Name == 'KEELSON_V3_CLOSED':
        g = o.Geometry
        for i in range(g.SegmentCount): src.append(('K3', 'KEELSON_V3', LineString(pl(g.SegmentCurve(i)))))
print('curves', len(src), 'by layer', {l: sum(1 for s in src if s[0] == l) for l in sorted({s[0] for s in src})})
TOL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.02
# dangling endpoints = endpoints that touch nothing else within TOL
ends = []
for i, (L, n, ls) in enumerate(src):
    for p in (ls.coords[0], ls.coords[-1]): ends.append((i, Point(p)))
dang = []
for i, p in ends:
    touch = any(j != i and src[j][2].distance(p) < TOL for j in range(len(src)))
    if not touch:
        nd = min((src[j][2].distance(p), src[j][1]) for j in range(len(src)) if j != i)
        dang.append((src[i][0], src[i][1], round(p.x, 2), round(p.y, 2), 'nearest %.3f mm: %s' % nd))
print('dangling endpoints (tol %.3f):' % TOL, len(dang))
for d in dang: print('  ', d)
bridges = []
if len(sys.argv) > 4 and sys.argv[4] == 'bridge':
    from shapely.ops import nearest_points
    for i, p in ends:
        if not any(j != i and src[j][2].distance(p) < TOL for j in range(len(src))):
            j = min((src[j][2].distance(p), j) for j in range(len(src)) if j != i)[1]
            q = nearest_points(p, src[j][2])[1]
            bridges.append(LineString([(p.x, p.y), (q.x, q.y)]))
    print('bridges added', len(bridges))
net = unary_union([s[2] for s in src] + bridges)
net = snap(net, net, TOL)
net = unary_union(net)
polys, cuts, dangles, invalid = polygonize_full(net)
P = [p for p in polys.geoms]
print('faces', len(P), 'dangles', len(dangles.geoms), 'cut edges', len(cuts.geoms), 'invalid', len(invalid.geoms))
rows = []
for p in P:
    b = p.bounds
    names = sorted({s[1].rsplit('_', 1)[0] for s in src if s[2].buffer(TOL).intersects(p.exterior) and s[2].intersection(p.exterior.buffer(TOL)).length > 0.3})
    rows.append((b[0], p.area, b, names))
for x, a, b, names in sorted(r for r in rows if r[1] > 3):
    print('face x[%.1f,%.1f] z[%.1f,%.1f] area %.1f  ~%s' % (b[0], b[2], b[1], b[3], a, ', '.join(names)[:150]))
