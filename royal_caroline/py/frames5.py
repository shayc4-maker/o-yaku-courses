import sys,csv,numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d
S,R=sys.argv[1],sys.argv[2]
a=1-np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L')).astype(float)/255
pts=[(1731,1809),(1861,1842),(1991,1861),(2129,1878),(2260,1889),(2384,1896),(2518,1913),(2650,1909),(2785,1909),(2913,1909),(3041,1913),(3172,1913),(3301,1913),(3430,1913),(3558,1914),(3691,1914),(3823,1916),(3949,1915),(4085,1915),(5734,1910),(5859,1911),(5998,1909),(6132,1909),(6250,1908),(6372,1907),(6507,1902),(6648,1891),(6770,1875),(6910,1853),(7165,1772),(7299,1713),(7425,1622)]
px,py=map(np.array,zip(*pts))
fr=[(int(r['frame']),float(r['x_px_plan5'])) for r in csv.DictReader(open(R+'/plan5/plan5_frames_detected.csv'))]
out=[]
for i,x in fr:
    yb=np.interp(x,px,py)+14+(x-1032)*0.0011
    if 4100<x<5700: yb=1915+14+(x-1032)*0.0011
    x0=int(x)-90; prof=a[int(yb)-75:int(yb)-25,x0:x0+180].mean(0); prof=uniform_filter1d(prof,7)
    on=prof>0.5; runs=[];s=None
    for j,v in enumerate(on):
        if v and s is None: s=j
        if not v and s is not None: runs.append((s,j)); s=None
    if s is not None: runs.append((s,len(on)))
    runs=[(s+x0,e+x0) for s,e in runs if e-s>30]
    if runs:
        s,e=min(runs,key=lambda r:abs((r[0]+r[1])/2-x-2.5)); c=(s+e)/2; w=e-s
    else: c,w=np.nan,0
    out.append((i,x,c,w))
d=np.array([c-x for i,x,c,w in out if not np.isnan(c) and abs(c-x)<20])
print('offset aligned-orig: median %.1f  std %.1f  n %d'%(np.median(d),d.std(),len(d)))
for i,x,c,w in out: print(i,x,round(c,1),w, '' if abs(c-x-np.median(d))<6 else '  <-- check')
np.save(S+'/out/frames_p5_aligned.npy',np.array([(i,x+np.median(d)) for i,x,c,w in out]))
