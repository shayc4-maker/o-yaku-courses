# 2D proposal: counter timbers stood behind F48 on the wing transom; face width 6 (builder), side + plan view. Nothing built.
import json,numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Pg
pr=json.load(open('data/stern_timber_profile_closed_v1.json')); tr=json.load(open('data/stern_transom_outline_v2.json'))['transoms_normalized']
sp=json.load(open('data/stern_side_points_v3.json')); S=np.array(json.load(open('data/bulwark_line_v3.json'))['S1']); cu=json.load(open('data/stern_cubes_plan4a.json'))['cubes']
fr=json.load(open('data/aft_frames_builder_v1.json'))['curves']
fig,(a,b)=plt.subplots(1,2,figsize=(20,11),gridspec_kw={'width_ratios':[1.5,1]})
D=np.array(pr['closed_dense']); a.add_patch(Pg(D,closed=False,fill=False,ec='gray',lw=1)); 
# centre line of the straight strip and 6 mm face band
r0,r1=np.array(sp['strip_right_edge']); l0,l1=np.array(sp['strip_left_edge'])
c0=(r0+l0)/2; c1=(r1+l1)/2; d=(c1-c0)/np.linalg.norm(c1-c0); n=np.array([-d[1],d[0]])
band=np.array([c0+3*n,c1+3*n,c1-3*n,c0-3*n]); a.add_patch(Pg(band,closed=True,fill=True,fc='orange',alpha=.35,ec='r',lw=1.2))
a.text(c0[0]-9,c0[1]+2,'face 6 mm (centred on the old strip 2.5 mm)',color='r')
for k,v in tr.items(): a.add_patch(Pg(np.array(v['poly']),closed=True,fc='lightblue',ec='b')); a.text(v['poly'][0][0]-3,v['poly'][0][1]+1,k,color='b')
for X0 in (24,13,2):
    zb=[c['cv'][0][2] for k,c in fr.items() if abs(c['cv'][0][0]-X0)<1e-6 or abs(c['cv'][0][0]-(X0+4))<1e-6 or abs(c['cv'][0][0]-(X0+8))<1e-6]
    a.add_patch(Pg([[X0,min(zb)],[X0+8,min(zb)],[X0+8,np.interp(X0+8,S[:,0],S[:,1])],[X0,np.interp(X0,S[:,0],S[:,1])]],closed=True,fc='wheat',ec='brown',alpha=.7))
    a.text(X0+1,min(zb)-4,'F%d'%{24:46,13:47,2:48}[X0],fontsize=9)
m=S[:,0]<40; a.plot(S[m,0],S[m,1],'g-',label='bulwark S1'); a.set_aspect('equal'); a.grid(alpha=.3); a.legend(); a.set_xlim(-55,40); a.set_ylim(40,160); a.set_title('Side view X-Z: timber strip (gray = previous round approved, orange = face 6 mm), transoms T1-3, F46-48')
# plan view at deck: cubes
for c in cu: b.plot(c['y_mm'],-c['aft_face_dx_mm'],'ks'); b.text(c['y_mm']+.5,-c['aft_face_dx_mm'],c['id']+' Y%.1f'%c['y_mm'],fontsize=8)
b.set_title('Plan cubes (plan_4a): timber Y positions at poop deck, aft face dx'); b.grid(alpha=.3); b.set_xlabel('Y'); b.set_ylabel('dx aft face')
fig.savefig('qa/aft_timbers_2d_v1.png',dpi=65,bbox_inches='tight')
