# bow HT planks v3: same rule as the previous round (bow_ht.py: stock = region of the hull with half-breadth >= the plank's inner face, head extension above the deck following station 1's flare, capped at X<=546, flat top) but with the NEW hull lines: lower part = the builder's plane splines / rabbet, deck level Z=101, top Z=118.66 (frame 1 front top)
import json,pickle,numpy as np
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B=json.load(open('data/bow_lines_builder_final_v1.json')); A5=json.load(open('data/frames_outer_approved_v5.json')); WL=json.load(open('data/bow_deck_waterline_v3.json'))
def dense(P,step=0.3):
    P=np.array(P); s=np.r_[0,np.cumsum(np.hypot(*np.diff(P[:,[0,2]],axis=0).T))]; q=np.arange(0,s[-1],step); q=np.r_[q,s[-1]]; return np.c_[np.interp(q,s,P[:,0]),np.interp(q,s,P[:,2])]
curves=[('Y2.65',dense(B['RABBET_final_to_M48'])),('Y11.62',dense(B['SPLINE_plane2_Y11.62'])),('Y20.59',dense(B['SPLINE_plane3_Y20.59'])),('Y29.56',dense(B['SPLINE_plane4_Y29.56'])),('Y38.53',dense(B['SPLINE_plane5_Y38.53']))]
Ys=[2.65,11.62,20.59,29.56,38.53,47.5]; XA=528.03; ZD=101.0; XBH=546.0; ZT=118.66
F=A5['1']['front']; C=np.array(F['curve']); C=np.vstack([C,np.array(F['top'])[1:]]); o=np.argsort(C[:,1]); yf=lambda z:float(np.interp(z,C[o,1],C[o,0]))      # half-breadth of frame 1 front (station 1 flare) vs Z
dwl=np.array(WL['curve']); ow=np.argsort(dwl[:,1]); x_of_y=lambda y:float(np.interp(y,dwl[ow,1],dwl[ow,0]))                                          # deck waterline X as a function of Y
profiles={}
for k,((key,Cc),y0) in enumerate(zip(curves,Ys[:-1]),1):
    Cc=Cc[Cc[:,0]>=XA-1e-6]; i=np.where(Cc[:,1]>=ZD)[0]
    if len(i): j=i[0]; Cc=np.vstack([Cc[:j],[np.interp(ZD,[Cc[j-1,1],Cc[j,1]],[Cc[j-1,0],Cc[j,0]]),ZD]])
    if Cc[0,0]>XA+1e-6: Cc=np.vstack([[XA,Cc[0,1]],Cc])
    xtop=Cc[-1,0]; pts=[tuple(p) for p in Cc]
    if xtop>XBH:      # the part forward of the cap ends flat at the deck level
        pts+=[(XBH,ZD),(XBH,ZT)]
    else:             # head extension: front edge follows the flare of station 1 above the deck, capped at XBH
        for z in np.arange(ZD+0.5,ZT,0.5):
            yt=y0-(yf(z)-yf(ZD)); x=min(x_of_y(max(yt,0.0)),XBH); pts.append((max(x,xtop),z))
        pts.append((min(pts[-1][0],XBH),ZT))
    pts.append((XA,ZT)); pg=Polygon(pts).buffer(0)
    profiles[k]=dict(y0=y0,y1=Ys[k],poly=pts,area=pg.area,xtop=xtop); print('plank %d (inner face Y %.2f): area %.0f, deck-level X %.2f, front edge above the deck %s'%(k,y0,pg.area,xtop,'cap 546 (flat at Z=101 beyond)' if xtop>XBH else 'follows station-1 flare'))
pickle.dump(profiles,open('data/bow_ht_profiles_v3.pkl','wb'))
old=pickle.load(open('data/bow_ht_profiles.pkl','rb'))
fig,axs=plt.subplots(1,2,figsize=(20,11))
cols=plt.cm.tab10(np.linspace(0,1,5))
for a,(ttl,src) in zip(axs,(('previous round (v2)',old),('now (new plane splines)',profiles))):
    for k in range(1,6):
        P=np.array(src[k][2]) if src is old else np.array(src[k]['poly']); a.fill(P[:,0],P[:,1],color=cols[k-1],alpha=.45,label='HT%d (Y %.1f..%.1f)'%(6-k,(src[k][0] if src is old else src[k]['y0']),(src[k][1] if src is old else src[k]['y1']))); a.plot(P[:,0],P[:,1],color=cols[k-1],lw=1)
    a.set_xlim(522,566); a.set_ylim(20,124); a.set_aspect('equal'); a.grid(alpha=.3); a.set_title(ttl); a.legend(fontsize=8,loc='lower right')
fig.savefig('qa/bow_ht_v3_vs_v2.png',dpi=55,bbox_inches='tight')
