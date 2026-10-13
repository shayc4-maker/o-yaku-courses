"""Frame on station line 18 (X=0): outline taken from the aft body plan (plan_1a, A1/2), curve '18',
rising all the way to the upper edge (top cut of the body-plan stations).
Inputs : station18_trace_px.npy  (pixel trace of curve 18 in plan_1a_aligned.png, produced by follow18)
Scale  : the body plan is 1.4 % smaller per pixel than the profile (calibrated on the 6 waterline rows):
         Z = -0.08393*py + 176.967 ,  Y = (2383 - px) * 0.08393   (centreline x = 2383 px)
Usage  : python3 -I build_frame18.py <trace.npy> <out.3dm> <qa.png> [x_aft_face=0] [thickness_x=4]"""
import sys, numpy as np, rhino3dm as R
from scipy.ndimage import gaussian_filter1d
from shapely.geometry import Polygon
trace, out3dm, outpng = sys.argv[1:4]
XA = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
TX = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0
K, XC = 0.08393, 2383.0
P = np.load(trace)
# arclength resample + light smoothing
d = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
s = np.arange(0, d[-1], 0.5); px = np.interp(s, d, P[:, 0]); py = np.interp(s, d, P[:, 1])
px, py = gaussian_filter1d(px, 8, mode='nearest'), gaussian_filter1d(py, 8, mode='nearest')
Y = (XC - px) * K; Z = -K * py + 176.967
O = np.c_[Y, Z]                                   # top -> post, 'left' half of the body plan = port
Y_POST = (XC - 2356.0) * K                        # sternpost half-siding at the bodyplan bar edge
print('outer: top (%.2f, %.2f)  end (%.2f, %.2f)  post half-width %.2f' % (*O[0], *O[-1], Y_POST))
# extend past the post so the band can be cut cleanly
t_end = (O[-1] - O[-6]); t_end /= np.hypot(*t_end)
O = np.vstack([O, O[-1] + t_end * np.arange(1, 25)[:, None] * 0.5])
O = np.vstack([O[0] + np.array([0.0, 1.0]) * np.arange(10, 0, -1)[:, None] * 0.5, O])   # vertical stub so the top cut is horizontal
Z_TOP = float(O[10, 1]); Y_TOP = float(O[10, 0])
O = np.c_[gaussian_filter1d(O[:, 0], 6, mode='nearest'), gaussian_filter1d(O[:, 1], 6, mode='nearest')]   # blend the stub into the curve (continuous tangent)
# moulded thickness (from the v10 frames: floor ~6.8, futtocks 5.6-4.5, tops 3.8-3.5)
def thick(z): return np.interp(z, [50, 80, 104, 136], [6.0, 5.0, 4.5, 3.5])
Os = np.c_[gaussian_filter1d(O[:, 0], 22, mode='nearest'), gaussian_filter1d(O[:, 1], 22, mode='nearest')]   # smoothed copy: normals only, so the offset cannot loop
T = np.gradient(Os, axis=0); T /= np.hypot(T[:, 0], T[:, 1])[:, None]
N = np.c_[-T[:, 1], T[:, 0]]
interior = np.array([0.0, 100.0])
if np.dot(N[len(N) // 2], interior - O[len(N) // 2]) < 0: N = -N       # normal toward the hull interior
I = O + N * thick(O[:, 1])[:, None]
from shapely.geometry import LineString, box
def cut_top(C):
    for i in range(1, len(C)):
        if C[i - 1, 1] > Z_TOP >= C[i, 1]:
            t = (C[i - 1, 1] - Z_TOP) / (C[i - 1, 1] - C[i, 1]); return np.vstack([C[i - 1] + t * (C[i] - C[i - 1]), C[i:]])
    raise SystemExit('curve never crosses Z_TOP')
def cut_at_post(C):
    out = [C[0]]
    for a_, b_ in zip(C[:-1], C[1:]):
        if b_[0] < Y_POST <= a_[0]:
            t = (a_[0] - Y_POST) / (a_[0] - b_[0]); out.append(a_ + t * (b_ - a_)); break
        out.append(b_)
    return np.array(out)
O2, I2 = cut_at_post(cut_top(O)), cut_at_post(cut_top(I))
poly = Polygon(np.vstack([O2, I2[::-1]]))
print('band valid', poly.is_valid, 'area %.1f mm2' % poly.area, ' outer top', np.round(O2[0], 2), ' inner top', np.round(I2[0], 2),
      ' post cut z', round(O2[-1, 1], 2), '->', round(I2[-1, 1], 2))
# ---------- rhino curves ----------
def crv(C, x, flip):
    pts = [R.Point3d(x, (-1 if flip else 1) * y, z) for y, z in C[::2]]
    if not np.allclose(C[::2][-1], C[-1]): pts.append(R.Point3d(x, (-1 if flip else 1) * C[-1][0], C[-1][1]))
    return R.Curve.CreateControlPointCurve(pts, 3)
f = R.File3dm(); f.Settings.ModelUnitSystem = R.UnitSystem.Millimeters
def layer(nm, rgb): l = R.Layer(); l.Name = nm; l.Color = (*rgb, 255); return f.Layers.Add(l)
L_ = {}
for xname, x in (('AFT_FACE_X%g' % XA, XA), ('FORE_FACE_X%g' % (XA + TX), XA + TX)):
    L_[xname] = layer('40_FRAME_18_' + xname, (0, 0, 0) if 'AFT' in xname else (120, 120, 120))
    for side, flip in (('PORT', True), ('STBD', False)):
        o, i = crv(O2, x, flip), crv(I2, x, flip)
        sg = -1 if flip else 1
        parts = [o, R.LineCurve(R.Point3d(x, sg * O2[0, 0], O2[0, 1]), R.Point3d(x, sg * I2[0, 0], I2[0, 1])), i,
                 R.LineCurve(R.Point3d(x, sg * I2[-1, 0], I2[-1, 1]), R.Point3d(x, sg * O2[-1, 0], O2[-1, 1]))]
        # orientation: outer top->post, cap, inner (reversed so it runs post->top), cap
        i.Reverse(); parts = [o, R.LineCurve(R.Point3d(x, sg * O2[-1, 0], O2[-1, 1]), R.Point3d(x, sg * I2[-1, 0], I2[-1, 1])), i,
                              R.LineCurve(R.Point3d(x, sg * I2[0, 0], I2[0, 1]), R.Point3d(x, sg * O2[0, 0], O2[0, 1]))]
        pc = R.PolyCurve()
        for c in parts: pc.Append(c)
        a = R.ObjectAttributes(); a.Name = 'FRAME18_%s_%s_CLOSED' % (side, xname); a.LayerIndex = L_[xname]; f.Objects.AddCurve(pc, a)
        print(side, xname, 'closed polycurve:', pc.IsClosed)
        for k, c in enumerate(parts):
            a = R.ObjectAttributes(); a.Name = 'FRAME18_%s_%s_%d' % (side, xname, k); a.LayerIndex = L_[xname]; f.Objects.AddCurve(c, a)
f.Write(out3dm, 7)
# ---------- QA ----------
import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 2, figsize=(16, 9), gridspec_kw={'width_ratios': [1, 1]})
ax = axs[0]
for sg in (1, -1):
    ax.fill(sg * np.r_[O2[:, 0], I2[::-1, 0]], np.r_[O2[:, 1], I2[::-1, 1]], color='#c33', alpha=.5)
    ax.plot(sg * O2[:, 0], O2[:, 1], 'k', lw=.8); ax.plot(sg * I2[:, 0], I2[:, 1], 'k', lw=.8)
try:
    fp = json.load(open('/tmp/claude-0/-home-user-o-yaku-courses/156e7236-f04f-5437-b27d-17e93e416883/scratchpad/st/frame_pieces_v10.json'))['pieces']
    for p in fp:
        if p['frame'] == 1: q = np.array(p['poly']); ax.plot(q[:, 0], q[:, 1], color='#888', lw=.6)
except Exception as e: print('v10 overlay skipped', e)
ax.axvspan(-Y_POST, Y_POST, color='#46f', alpha=.3); ax.set_aspect('equal'); ax.set_title('view from astern: frame 18 (red) vs old frame 1 (grey), sternpost (blue)'); ax.grid(alpha=.3)
ax.set_xlim(-70, 70); ax.set_ylim(40, 150)
ax = axs[1]
sys.path.insert(0, '/tmp/claude-0/-home-user-o-yaku-courses/156e7236-f04f-5437-b27d-17e93e416883/scratchpad/st')
from p5map import model_to_p5
from PIL import Image; Image.MAX_IMAGE_PIXELS = None
im = np.array(Image.open('/tmp/claude-0/-home-user-o-yaku-courses/156e7236-f04f-5437-b27d-17e93e416883/scratchpad/st/plan_5_aligned.png'))
x0, x1, z0, z1 = -35, 60, 30, 150
a_, b_ = model_to_p5(x0, z0); c_, d_ = model_to_p5(x1, z1)
ax.imshow(im[int(d_):int(b_), int(a_):int(c_)], cmap='gray', extent=(x0, x1, z0, z1), origin='upper', aspect='equal')
ax.add_patch(plt.Rectangle((XA, O2[-1, 1]), TX, Z_TOP - O2[-1, 1], fc='red', ec='red', alpha=.55))
ax.axvline(0, color='red', lw=.8); ax.set_xlim(x0, x1); ax.set_ylim(z0, z1); ax.set_title('side view on plan_5: frame at line 18 (red), X %g..%g, Z %.1f..%.1f' % (XA, XA + TX, O2[-1, 1], Z_TOP))
plt.tight_layout(); plt.savefig(outpng, dpi=75)
