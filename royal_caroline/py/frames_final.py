import sys,csv,json,numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d
S,R=sys.argv[1],sys.argv[2]
a=1-np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L')).astype(float)/255
prof=uniform_filter1d(a[1858:1905,4100:5950].mean(0),9); on=prof>0.6
runs=[];s=None
for j,v in enumerate(on):
    if v and s is None: s=j
    if not v and s is not None:
        if j-s>35: runs.append((s+4100,j+4100))
        s=None
mid=[(s+e)/2 for s,e in runs]; print('midship blocks',[(round(c),e-s) for (s,e),c in zip(runs,mid)])
csvx=[float(r['x_px_plan5'])+3.5 for r in csv.DictReader(open(R+'/plan5/plan5_frames_detected.csv'))]
fr=csvx[:19]+[c for c in mid if 4150<c<5800]+csvx[32:]
fr=sorted(fr); print(len(fr),'frames'); p=np.diff(fr); print('pitch px',np.round(p).astype(int).tolist())
K=1000/244.8/48
X=[((4197.6+(x-1280)*1.00146)-4194.98)*K for x in fr]
json.dump({'frames_p5_aligned_px':fr,'X_mm':X,'note':'X model mm fwd of station 18; frame 1 = sternmost; mapping heel/foremost homologous points plan_5->A1/1, ratio 1.00146'},open(S+'/out/frames_X.json','w'),indent=1)
for i,(x,xm) in enumerate(zip(fr,X),1): print(i,round(x,1),round(xm,2))
