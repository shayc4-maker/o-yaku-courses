import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep
D=json.load(open('data/frames_outer_all_v1.json'))
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Visible=vis; l.Color=col; LI[n]=f.Layers.Add(l); return LI[n]
def add(g,ln,name):
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.Add(g,a)
lR=layer('OUTER_faces_+Y',(200,0,0,255)); lL=layer('OUTER_faces_-Y',(0,0,200,255)); lP=layer('POINTS_outer',(120,120,0,255),False)
def spline(q,sg,X):
    q=np.array(q,float); keep=[0]+[i for i in range(1,len(q)) if np.hypot(*(q[i]-q[i-1]))>1e-6]; q=q[keep]; tck,u=splprep(q.T,k=3,s=0); t,c,k=tck
    P=[r3.Point3d(X,sg*c[0][i],c[1][i]) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,3,P); tt=t[1:-1]
    for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
    return nc
n=0
for b,fr in D.items():
    for nm,v in fr.items():
        X=v['X']; pts=v['points']; corner=any(p[0]=='corner' for p in pts); q=[[p[1],p[2]] for p in pts]; body=q[:-1] if corner else q
        for sg,ly,tag in ((1,lR,'R'),(-1,lL,'L')):
            add(spline(body,sg,X),ly,'F%02d_%s_%s'%(int(b),nm,tag)); n+=1
            if corner: add(r3.LineCurve(r3.Point3d(X,sg*q[-2][0],q[-2][1]),r3.Point3d(X,sg*q[-1][0],q[-1][1])),ly,'F%02d_%s_%s_top'%(int(b),nm,tag))
        pa=r3.ObjectAttributes(); pa.LayerIndex=lP; pa.Name='F%02d_%s_pt'%(int(b),nm)
        for y,z in q: f.Objects.AddPoint(r3.Point3d(X,y,z),pa)
f.Write('rhino/RoyalCaroline_frames_outer_lines_v1.3dm',7); print('objects',len(f.Objects),'splines',n)
