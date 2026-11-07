# lift the lower end points of the APPROVED outer lines (builder file) from the foremost face back to station 5 (X 404.4) onto the plan's rabbet (ink rabbet, recalibrated v2, upper line); only the +Y half; the first control point of each face spline is moved up (nothing else touched); lift only (never lowers); capped so that the end stays below control point 1 (no belly). Output: Rhino file with the half ship after the lift + report.
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import CubicSpline
SRC='/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/c8f595d5-RoyalCaroline_frames_outer_lines_v1.3dm'
V2=json.load(open('data/rabbet_points_v2_calibrated.json'))['points']; R2=CubicSpline([p[0] for p in V2],[p[1] for p in V2],bc_type='natural'); X5=404.4
src=r3.File3dm.Read(SRC); L={i:src.Layers[i].Name for i in range(len(src.Layers))}
out=r3.File3dm(); out.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; lay=r3.Layer(); lay.Name='OUTER_faces_+Y_after_lift'; lay.Color=(200,0,0,255); li=out.Layers.Add(lay)
rows=[]; belly=[]
for o in src.Objects:
    if L[o.Attributes.LayerIndex]!='OUTER_faces_+Y': continue
    g=o.Geometry.Duplicate(); nm=o.Attributes.Name
    if g.ObjectType.name=='Curve' and hasattr(g,'Points') and not nm.endswith('_top'):
        P=g.Points; n=len(P); X0=P[0].X; z0=P[0].Z; z1=P[1].Z
        if X0>=X5:
            tgt=float(R2(min(X0,527.99))); want=tgt-z0
            if want>0.005:
                cap=z1-z0-0.05; d=max(0.0,min(want,cap)); 
                if d>0:
                    p0=P[0]; P[0]=r3.Point4d(p0.X,p0.Y,p0.Z+d,1.0) if hasattr(r3,'Point4d') else p0
                rows.append((nm,round(X0,2),round(z0,2),round(tgt,2),round(want,2),round(d,2),'capped' if d<want-1e-6 else ''))
    a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=nm; out.Objects.Add(g,a)
out.Write('rhino/RoyalCaroline_frames_outer_half_lifted_v1.3dm',7)
print('faces lifted:',len(rows)); 
for r in rows: print(r)
