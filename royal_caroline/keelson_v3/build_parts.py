"""Close all backbone parts from the v2 line work.
 1. closes the 9 tiny gaps with short lines, adds 2 clearly-implied dividers,
 2. polygonizes the network (planar faces) and extracts every face boundary
    as EXACT sub-curves of the original lines (not resampled polylines),
 3. writes one closed curve per part + QA picture + report.
Usage: python3 -I build_parts.py <v2.3dm> <keelson_closed_v3.3dm> <out.3dm> <qa.png> <report.txt>"""
import sys, numpy as np, rhino3dm as R, shapely
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union, polygonize_full, snap, nearest_points

src3, kee3, out3, outpng, outtxt = sys.argv[1:6]
hogc = R.File3dm.Read(sys.argv[6]) if len(sys.argv) > 6 else None
m = R.File3dm.Read(src3); k = R.File3dm.Read(kee3); layers = [l.FullPath for l in m.Layers]
rep = []
def log(*a):
    s = ' '.join(str(x) for x in a); print(s); rep.append(s)

# ---------- 1. collect source curves ----------
S = []   # dict(layer, name, crv)
def add(layer, name, crv): S.append(dict(layer=layer, name=name, crv=crv))
for o in m.Objects:
    a, g = o.Attributes, o.Geometry; L = layers[a.LayerIndex]
    if L[:2] in ('00', '98', '02'): continue
    if hogc and L[:2] == '01' and a.Name.startswith('BODY_OUTER_V2_') and 19 <= int(a.Name.split('_')[-1]) <= 198: continue   # replaced by the smooth contour
    if L.startswith('03') and not a.Name and type(g).__name__ == 'NurbsCurve': continue   # whole purple spline
    if type(g).__name__ == 'PolyCurve':
        for i in range(g.SegmentCount): add(L[:2], a.Name or 'BODY', g.SegmentCurve(i))
    else: add(L[:2], a.Name or 'BODY', g)
for o in k.Objects:
    if o.Attributes.Name == 'KEELSON_V3_CLOSED':
        g = o.Geometry
        for i in range(g.SegmentCount): add('K3', 'KEELSON_V3', g.SegmentCurve(i))

if hogc:
    for o in hogc.Objects:
        if o.Attributes.Name.startswith('HOGC_'): add('01', 'HOG_CONTOUR_V3', o.Geometry)

def dense(c, n=None):
    d = c.Domain; t = type(c).__name__
    if t == 'LineCurve':
        ts = np.linspace(d.T0, d.T1, 2)
        if n: ts = np.linspace(d.T0, d.T1, n)
    else:
        rough = np.linspace(d.T0, d.T1, 60)
        pr = np.array([[c.PointAt(t_).X, c.PointAt(t_).Z] for t_ in rough])
        L = np.hypot(*np.diff(pr, axis=0).T).sum()
        ts = np.linspace(d.T0, d.T1, int(max(24, min(6000, L / 0.2))))
    return ts, np.array([[c.PointAt(t_).X, c.PointAt(t_).Z] for t_ in ts])
for s in S: s['ts'], s['pts'] = dense(s['crv']); s['ls'] = LineString(s['pts'])

TOL = 0.02
def netunion(extra=()):
    net = unary_union([s['ls'] for s in S] + list(extra)); return unary_union(snap(net, net, TOL))

# ---------- 2. closure fixes ----------
FIX = []   # (name, p, q)
ends = [(i, Point(s['pts'][0])) for i, s in enumerate(S)] + [(i, Point(s['pts'][-1])) for i, s in enumerate(S)]
for i, p in ends:
    if not any(j != i and S[j]['ls'].distance(p) < TOL for j in range(len(S))):
        d, j = min((S[j]['ls'].distance(p), j) for j in range(len(S)) if j != i)
        q = nearest_points(p, S[j]['ls'])[1]
        if d < 2.0:
            FIX.append(('GAP_%s' % S[i]['name'], (p.x, p.y), (q.x, q.y), d))
            log('gap %.3f mm  %-34s (%.2f,%.2f) -> %s' % (d, S[i]['name'], p.x, p.y, S[j]['name']))
        else: log('UNRESOLVED dangling end (%.1f mm): %s (%.2f,%.2f)' % (d, S[i]['name'], p.x, p.y))
# dividers (endpoints taken from the existing line ends, so they join exactly)
def endpoint_near(x, z, r=0.3):
    best = None
    for s_ in S:
        for q in (s_['pts'][0], s_['pts'][-1]):
            d = np.hypot(q[0] - x, q[1] - z)
            if d < r and (best is None or d < best[0]): best = (d, tuple(q))
    return best[1]
def up_to_contour(x, z0, zmax=20):
    ray = LineString([(x, z0), (x, zmax)]); hits = []
    for s_ in S:
        if s_['layer'] == '01':
            g = ray.intersection(s_['ls'])
            if not g.is_empty: hits += [p for p in getattr(g, 'geoms', [g]) if p.geom_type == 'Point' and p.y > z0 + 0.05]
    return min(hits, key=lambda p: p.y)
a0 = endpoint_near(59.5, 4.1); p = up_to_contour(a0[0], a0[1])
FIX.append(('DIV_DEADWOOD_RISING_HOG', a0, (a0[0], p.y), 0)); log('divider DEADWOOD_RISING|HOG   x=%.2f  z %.2f..%.2f' % (a0[0], a0[1], p.y))
b0 = endpoint_near(539.79, 37.74); b1 = endpoint_near(539.81, 47.83)
FIX.append(('DIV_STEM_APRONSTRIP', b0, b1, 0)); log('divider STEM|APRON-STRIP      (%.2f,%.2f)->(%.2f,%.2f)' % (*b0, *b1))
for i, (n, a_, b_, d) in enumerate(FIX):
    add('FX', n, R.LineCurve(R.Point3d(a_[0], 0, a_[1]), R.Point3d(b_[0], 0, b_[1])))
    S[-1]['ts'], S[-1]['pts'] = dense(S[-1]['crv']); S[-1]['ls'] = LineString(S[-1]['pts'])

# ---------- 3. faces ----------
net = netunion()
polys, cuts, dang, inv = polygonize_full(net)
F = sorted([p for p in polys.geoms if p.area > 3], key=lambda p: (p.bounds[0], p.bounds[1]))
log('faces (area>3): %d' % len(F))
for i, p in enumerate(F): b = p.bounds; log('  F%02d x[%.1f,%.1f] z[%.1f,%.1f] area %.1f' % (i, b[0], b[2], b[1], b[3], p.area))

# ---------- 4. exact boundary pieces per face ----------
ON_TOL = 0.04
def pieces_for(ring):
    rb = ring.buffer(0.05).bounds
    res = []
    for si, s in enumerate(S):
        bb = s['ls'].bounds
        if bb[2] < rb[0] or bb[0] > rb[2] or bb[3] < rb[1] or bb[1] > rb[3]: continue
        c = s['crv']; d = c.Domain
        if 'fts' not in s: s['fts'], s['fP'] = dense(c, n=int(max(2, s['ls'].length / 0.2)) + 1) if type(c).__name__ == 'LineCurve' else (s['ts'], s['pts'])
        ts, P = s['fts'], s['fP']
        on = shapely.distance(shapely.points(P), ring) < ON_TOL
        i = 0
        while i < len(ts):
            if on[i]:
                j = i
                while j + 1 < len(ts) and on[j + 1]: j += 1
                ta, tb = ts[i], ts[j]
                if i > 0:    # refine entry
                    lo, hi = ts[i - 1], ts[i]
                    for _ in range(40):
                        mid = (lo + hi) / 2; q = c.PointAt(mid)
                        if Point(q.X, q.Z).distance(ring) < ON_TOL: hi = mid
                        else: lo = mid
                    ta = hi
                if j < len(ts) - 1:
                    lo, hi = ts[j], ts[j + 1]
                    for _ in range(40):
                        mid = (lo + hi) / 2; q = c.PointAt(mid)
                        if Point(q.X, q.Z).distance(ring) < ON_TOL: lo = mid
                        else: hi = mid
                    tb = lo
                if tb - ta > 1e-6:
                    A, B = c.PointAt(ta), c.PointAt(tb)
                    if np.hypot(A.X - B.X, A.Z - B.Z) > 0.02 or tb - ta > 0.05 * (d.T1 - d.T0):
                        res.append(dict(si=si, ta=ta, tb=tb, A=(A.X, A.Z), B=(B.X, B.Z), name=s['name'], layer=s['layer']))
                i = j + 1
            else: i += 1
    return res

PRI = {'FX': 0, 'K3': 0, '04': 1, '05': 1, '06': 1, '07': 1, '03': 1, '01': 2}
STEP = 0.01
def ring_idx(ring, P, N):
    return (shapely.line_locate_point(ring, shapely.points(P)) / STEP).round().astype(int) % N
def build_loop(ring):
    L = ring.length; N = int(np.ceil(L / STEP)); cov = np.zeros(N, bool)
    cand = pieces_for(ring)
    cand.sort(key=lambda r: (PRI.get(r['layer'], 3), -abs(r['tb'] - r['ta'])))
    out = []
    def fill(i0_, i1_):
        d = (i1_ - i0_) % N
        if d > N / 2: i0_, i1_ = i1_, i0_; d = (i1_ - i0_) % N
        for k in range(d + 1): cov[(i0_ + k) % N] = True
    for r in cand:
        c = S[r['si']]['crv']
        ts = np.linspace(r['ta'], r['tb'], 1500)
        P = np.array([[c.PointAt(t).X, c.PointAt(t).Z] for t in ts])
        idx = ring_idx(ring, P, N)
        new = ~cov[idx]
        j = 0
        while j < len(ts):
            if new[j]:
                e = j
                while e + 1 < len(ts) and new[e + 1]: e += 1
                ta, tb = ts[j], ts[e]
                def isnew(t):
                    q = c.PointAt(t); return not cov[ring_idx(ring, np.array([[q.X, q.Z]]), N)[0]]
                if j > 0:
                    lo, hi = ts[j - 1], ts[j]
                    for _ in range(40):
                        mid = (lo + hi) / 2
                        if isnew(mid): hi = mid
                        else: lo = mid
                    ta = hi
                if e < len(ts) - 1:
                    lo, hi = ts[e], ts[e + 1]
                    for _ in range(40):
                        mid = (lo + hi) / 2
                        if isnew(mid): lo = mid
                        else: hi = mid
                    tb = lo
                A, B = c.PointAt(ta), c.PointAt(tb)
                seglen = LineString(P[j:e + 1]).length if e > j else 0
                if seglen > 0.06:
                    out.append(dict(si=r['si'], ta=ta, tb=tb, name=r['name'], layer=r['layer']))
                    for k in range(j, e): fill(idx[k], idx[k + 1])
                j = e + 1
            else: j += 1
    return out, cov.mean(), cov, N

def make_curves(out):
    segs = []
    for r in out:
        c = S[r['si']]['crv']
        sub = c.Trim(r['ta'], r['tb']) if (r['ta'] > c.Domain.T0 + 1e-9 or r['tb'] < c.Domain.T1 - 1e-9) else c.Duplicate()
        segs.append(dict(crv=sub, name=r['name'], layer=r['layer']))
    return segs

def join(segs, ring):
    if not segs: return None, None, 0
    def mid(c):
        d = c.Domain; q = c.PointAt((d.T0 + d.T1) / 2); return ring.project(Point(q.X, q.Z))
    ordered = sorted(segs, key=lambda s_: mid(s_['crv']))
    def dist(a, b): return np.hypot(a.X - b.X, a.Z - b.Z)
    if len(ordered) > 1:     # first piece: end must be the end nearer to piece 2
        c0, c1 = ordered[0]['crv'], ordered[1]['crv']
        e0 = min(dist(c0.PointAtEnd, c1.PointAtStart), dist(c0.PointAtEnd, c1.PointAtEnd))
        s0 = min(dist(c0.PointAtStart, c1.PointAtStart), dist(c0.PointAtStart, c1.PointAtEnd))
        if s0 < e0: c0.Reverse()
    for i in range(1, len(ordered)):
        prev, c = ordered[i - 1]['crv'], ordered[i]['crv']
        if dist(prev.PointAtEnd, c.PointAtEnd) < dist(prev.PointAtEnd, c.PointAtStart): c.Reverse()
    def axis(c):
        if type(c).__name__ != 'LineCurve': return None
        p, q = c.PointAtStart, c.PointAtEnd
        if abs(p.X - q.X) < 1e-9 and abs(p.Z - q.Z) > 1e-6: return 'V'
        if abs(p.Z - q.Z) < 1e-9 and abs(p.X - q.X) > 1e-6: return 'H'
        return None
    mx = 0
    for i, s_ in enumerate(ordered):
        A, B = s_['crv'], ordered[(i + 1) % len(ordered)]['crv']
        a_, b_ = A.PointAtEnd, B.PointAtStart
        g = dist(a_, b_); mx = max(mx, g)
        if g > 0:
            ax, bx = axis(A), axis(B)
            if ax == 'V' and bx == 'H': T = (a_.X, b_.Z)
            elif ax == 'H' and bx == 'V': T = (b_.X, a_.Z)
            elif ax == 'V': T = (a_.X, b_.Z)
            elif ax == 'H': T = (b_.X, a_.Z)
            elif bx == 'V': T = (b_.X, a_.Z)
            elif bx == 'H': T = (a_.X, b_.Z)
            else: T = ((a_.X + b_.X) / 2, (a_.Z + b_.Z) / 2)
            A.SetEndPoint(R.Point3d(T[0], 0, T[1])); B.SetStartPoint(R.Point3d(T[0], 0, T[1]))
    pc = R.PolyCurve()
    for s_ in ordered: pc.Append(s_['crv'])
    return ordered, pc, mx

# ---------- 5. naming (by face centroid / bbox, using the v5 part names where they exist) ----------
def name_face(p):
    b = p.bounds; cx, cz = p.representative_point().x, p.representative_point().y
    A = p.area
    if abs(A - 2315.1) < 5: return 'KEELSON'
    return None
# (min x, area) -> (name, confident).  Names marked '?' are my reading of the plan; 'v5' = same place as the v5 split.
NAMES = {
 (-30, 1163): ('REAR_OUTLINE_C?', False), (-26, 111): ('REAR_OUTLINE_A?', False), (-24, 459): ('REAR_OUTLINE_B?', False),
 (-16, 849): ('STERNPOST', True), (-5, 279): ('STERN_KNEE', True), (-1, 508): ('DEADWOOD_RISING', True),
 (-1, 1239): ('KEEL_1', True), (1, 1002): ('FALSE_KEEL_ALL_AND_OUTER_STEM_STRIP?', False), (5, 99): ('INNER_POST_HEEL', True),
 (10, 333): ('DEADWOOD_AFT_LOWER', True), (41, 2367): ('KEELSON', True), (59, 1832): ('HOG_AND_FORE_STRIP_MERGED?', False),
 (168, 1177): ('KEEL_2', True), (334, 1336): ('KEEL_3', True), (480, 378): ('APRON_MAIN?', False), (501, 526): ('GRIPE_FOREFOOT?', False),
 (531, 350): ('APRON_INNER?', False), (540, 357): ('STEM_AFT?', False), (540, 399): ('STEM_FORE?', False), (552, 544): ('HEAD_BODY?', False),
 (560, 132): ('HEAD_TRIANGLE?', False), (564, 115): ('KNEE_OF_HEAD_UPPER?', False), (569, 290): ('KNEE_OF_HEAD_LOWER?', False), (573, 10): ('HEAD_SLIVER?', False),
}
def _lookup(p):
    for (x0, ar), v in NAMES.items():
        if abs(p.bounds[0] - x0) < 1.0 and abs(p.area - ar) <= max(1.0, 0.05 * ar): return v
    return None
def nm(p):
    v = _lookup(p); return v[0] if v else None
def confident(p):
    v = _lookup(p); return bool(v and v[1])

f = R.File3dm(); f.Settings.ModelUnitSystem = R.UnitSystem.Millimeters; f.Settings.ModelAbsoluteTolerance = 0.01
def mk(n, rgb): l = R.Layer(); l.Name = n; l.Color = (*rgb, 255); return f.Layers.Add(l)
L_closed = mk('20_PARTS_CLOSED', (0, 0, 0)); L_unnamed = mk('21_PARTS_NEED_NAME_OR_SPLIT', (200, 0, 0)); L_fix = mk('22_CLOSURE_FIXES_ADDED', (255, 0, 255)); L_pc = mk('23_PART_PIECES', (120, 120, 120))
for n, a_, b_, d in FIX:
    at = R.ObjectAttributes(); at.Name = n; at.LayerIndex = L_fix
    f.Objects.AddCurve(R.LineCurve(R.Point3d(a_[0], 0, a_[1]), R.Point3d(b_[0], 0, b_[1])), at)

summary = []
for fi, p in enumerate(F):
    for ring_i, ring in enumerate([p.exterior] + [r for r in p.interiors if Polygon(r).area > 0.05]):
        out, covfrac, cov, N = build_loop(ring)
        ordered, pc, gap = join(make_curves(out), ring)
        n = nm(p) or ('FACE_%02d' % fi)
        if ring_i: n += '_HOLE%d' % ring_i
        ok = pc is not None and gap < 0.15 and covfrac > 0.998 and pc.IsClosed
        summary.append((n, p.area, covfrac, gap, ok, len(out)))
        if not ok and covfrac < 0.998:
            miss = np.where(~cov)[0]; log('   DEBUG %s uncovered at %s' % (n, [tuple(np.round(ring.interpolate(i * STEP).coords[0], 1)) for i in miss[::max(1, len(miss) // 6)]]))
        at = R.ObjectAttributes(); at.Name = n; at.LayerIndex = L_closed if (confident(p) and ok) else L_unnamed
        if pc is not None: f.Objects.AddCurve(pc, at)
        for s_ in (ordered or []):
            a2 = R.ObjectAttributes(); a2.Name = n + '|' + s_['name']; a2.LayerIndex = L_pc; f.Objects.AddCurve(s_['crv'], a2)
log('')
log('%-34s %9s %8s %9s %6s %6s' % ('part', 'area', 'covered', 'max gap', 'closed', 'pieces'))
for n, a, c, g, ok, ns in summary: log('%-34s %9.1f %7.1f%% %9.4f %6s %6d' % (n, a, c * 100, g, 'YES' if ok else 'NO', ns))
f.Write(out3, 7)
open(outtxt, 'w').write('\n'.join(rep))

import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(3, 1, figsize=(16, 20)); cm = plt.get_cmap('tab20')
for ax, (t, xl, yl) in zip(axs, [('aft', (-35, 80), (-12, 95)), ('mid', (40, 340), (-12, 45)), ('fwd', (300, 620), (-12, 120))]):
    for i, p in enumerate(F):
        x, y = p.exterior.xy; ax.fill(x, y, color=cm(i % 20), alpha=.4); ax.plot(x, y, 'k', lw=.5)
        c = p.representative_point()
        if xl[0] < c.x < xl[1] and yl[0] < c.y < yl[1]: ax.text(c.x, c.y, (nm(p) or 'F%02d' % i)[:14], fontsize=7, ha='center')
    for n, a_, b_, d in FIX: ax.plot([a_[0], b_[0]], [a_[1], b_[1]], color='magenta', lw=1.5)
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect('equal'); ax.set_title(t)
plt.tight_layout(); plt.savefig(outpng, dpi=75)
