# builder's corrected F49-F51 (c0fd01d8): trim the top at bulwark S1 and stop at the outer timber (T3: centre path +- half thickness, aft view Y-Z)
import rhino3dm as r,numpy as np,json,glob,math
SRC=glob.glob('/root/.claude/uploads/*/c0fd01d8-*.3dm')[0]; m=r.File3dm.Read(SRC); L={l.Index:l.Name for l in m.Layers}
SB=np.array(json.load(open('data/bulwark_line_v3.json'))['S1'])
# outer timber T3 (Y~40) side-profile outline pieces from the builder's file; frame X-line meets it from below -> the frame stops there
T3=[]
for o in m.Objects:
    if o.Attributes.Name.startswith('T3 side profile') and hasattr(o.Geometry,'Domain'):
        g=o.Geometry; T3.append(np.array([[q.X,q.Z] for q in (g.PointAt(t) for t in np.linspace(g.Domain.T0,g.Domain.T1,300))]))
def cross(X):
    zs=[]
    for P in T3:
        for p,q in zip(P[:-1],P[1:]):
            if (p[0]-X)*(q[0]-X)<=0 and p[0]!=q[0]: zs.append(p[1]+(X-p[0])/(q[0]-p[0])*(q[1]-p[1]))
    return sorted(z for z in zs if z>76)
res={}
for o in m.Objects:
    g=o.Geometry; n=o.Attributes.Name
    if L[o.Attributes.LayerIndex].startswith('PROPOSED_frames') and hasattr(g,'Domain'):
        t=np.linspace(g.Domain.T0,g.Domain.T1,3000); P=np.array([[q.X,q.Y,q.Z] for q in (g.PointAt(x) for x in t)]); X=P[0,0]
        zs1=float(np.interp(X,SB[:,0],SB[:,1])); ct=cross(X); zt=ct[0] if ct else 1e9
        stop='outer timber T3' if zt<zs1 else 'S1'; i=int(np.argmin(abs(P[:,2]-zs1))); j=int(np.argmin(abs(P[:,2]-zt))) if zt<zs1 else 0   # builder: KEEP the upper part (timber crossing .. S1), delete what is below
        res[n]=dict(stop=stop,t=float(t[i]),dom=(float(t[j]),g.Domain.T1)); Z=zs1
        print(n[:3],'X=%.1f'%X,'-> keeps from',stop if zt<zs1 else 'bottom','Z %.1f up to S1 Z %.1f'%(P[j,2],P[i,2]),'(S1 %.1f, timber crossing %s)'%(zs1,[round(z,1) for z in ct]))
f=r.File3dm(); f.Settings.ModelUnitSystem=r.UnitSystem.Millimeters; M={}
for i,l in enumerate(m.Layers): ly=r.Layer(); ly.Name=l.Name; ly.Color=l.Color; M[i]=f.Layers.Add(ly)
for o in m.Objects:
    a=o.Attributes; a.LayerIndex=M[a.LayerIndex]; g=o.Geometry; k=a.Name
    if k in res and hasattr(g,'Trim'): g=g.Duplicate(); g=g.Trim(res[k]['dom'][0],res[k]['t']); a.Name=k+' upper part kept (from '+('outer timber T3' if res[k]['stop']!='S1' else 'foot')+' to S1)'
    f.Objects.Add(g,a)
f.Write('rhino/RoyalCaroline_aft_timbers_lines_v5.3dm',7); print('written')
