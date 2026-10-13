import sys,json,numpy as np, rhino3dm as r3
from PIL import Image
from scipy.ndimage import maximum_filter
PK=sys.argv[1]
fr={f['file']:f for f in json.load(open(PK+'/images/frames.json'))}
m=r3.File3dm.Read(PK+'/RoyalCaroline_lines_1to48_v1.3dm')
names={i:l.Name for i,l in enumerate(m.Layers)}
def pts(c,n=300):
    d=c.Domain; return np.array([[p.X,p.Y,p.Z] for p in (c.PointAt(d.T0+(d.T1-d.T0)*i/(n-1)) for i in range(n))])
def check(file,P,proj):
    f=fr[file]; im=np.array(Image.open(PK+'/images/'+file))<128; im=maximum_filter(im,3)
    H,W=im.shape; o=np.array(f['origin']); xa=np.array(f['xaxis']); ya=np.array(f['yaxis'])
    u=((P-o)@xa)/f['w']*W; v=H-((P-o)@ya)/f['h']*H
    ok=(u>=0)&(u<W)&(v>=0)&(v<H); ui=u[ok].astype(int); vi=v[ok].astype(int)
    return im[vi,ui].mean() if ok.any() else np.nan
res={}
for o in m.Objects:
    ln=names[o.Attributes.LayerIndex]; nm=o.Attributes.Name or ''
    if not isinstance(o.Geometry,r3.NurbsCurve): continue
    P=pts(o.Geometry)
    if ln=='BODYPLAN_2D_as_drawn':
        file='bodyplan_aft_A1-2.png' if nm.endswith('1a') else 'bodyplan_fwd_A1-3.png'
        res[nm]=check(file,P,None)
    if ln=='WATERLINES_from_A1-4_plan':
        res[nm]=check('halfbreadth_A1-4.png',P,None)
    if ln=='STATIONS_3D_bodyplan':
        # station lines should fall on profile station verticals: test X position on profile image
        Q=np.array([[P[0,0],0,z] for z in np.linspace(20,60,30)])
        res[nm+'_profileX']=check('profile_A1-1.png',Q,None)
for k,v in sorted(res.items()): print('%-34s on-ink %.2f'%(k,v))
