# 2D cutting plan of the double frames (S side + mirrored P side), division like the builder's frame 21 sheet.
# Faces of frame i: X-4, X, X+4; outer line of a face = hull-flow interpolation between the neighbouring frames' outer lines (from the plan pieces);
# inner line = parallel at the TRUE in-plane offset t*sqrt(1+(dZ*dY/dX)^2) (normal thickness t=3.2 mm); layer block = union of the two face bands (sanding allowance = wood between block and exact face lines);
# pieces: layer A = floor(1) fut2(2,7) top(3,6); layer F = fut1(8,13) fut3(9,12) top(10,11), joints at the old division (perpendicular cuts).
import json,sys,numpy as np
from shapely.geometry import Polygon,LineString,box,MultiPolygon
from shapely.ops import unary_union,split
from shapely import affinity
from scipy.signal import savgol_filter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
T=3.2
PCS=json.load(open('data/frame_pieces_v10.json'))['pieces']; X=json.load(open('data/frames_X.json'))['X_mm']
def outer_line(fr):
    sel=[p for p in PCS if p['frame']==fr and p['layer']=='A' and p['side'] in('S','C')]
    U=unary_union([(Polygon(p['poly']).buffer(0).intersection(box(0,-10,100,200)) if p['side']=='C' else Polygon(p['poly']).buffer(0)).buffer(0.02) for p in sel]).buffer(-0.02)
    ring=np.array(U.exterior.coords)[:-1]; ib=int(np.argmin(ring[:,1]+0.001*ring[:,0])); it=int(np.argmax(ring[:,1]*1000+ring[:,0]))
    def chain(a,b):
        idx=[a]
        while idx[-1]!=b: idx.append((idx[-1]+1)%len(ring))
        return ring[idx]
    c1,c2=chain(ib,it),chain(it,ib)[::-1]; return c1 if c1[:,0].mean()>c2[:,0].mean() else c2
ZG=np.arange(0,150.01,0.25); OUT={}
def Yfun(fr):
    if fr in OUT: return OUT[fr]
    L=outer_line(fr); z=np.maximum.accumulate(L[:,1]); z=z+np.arange(len(z))*1e-6
    zmin,zmax=z[0],z[-1]; y=np.interp(ZG,z,L[:,0],left=np.nan,right=np.nan); OUT[fr]=(y,zmin,zmax); return OUT[fr]
def face_outer(i,Xf):
    y0,zmin,zmax=Yfun(i); j=i+1 if Xf>X[i-1] else i-1
    if j<1 or j>45: y=y0.copy()
    else:
        y1=Yfun(j)[0]; w=(Xf-X[i-1])/(X[j-1]-X[i-1]); y=np.where(np.isnan(y1),y0,(1-w)*y0+w*y1)
    ok=(ZG>=zmin)&(ZG<=zmax)&~np.isnan(y); return np.c_[y[ok],ZG[ok]]
def yx(i):      # dY/dX at equal Z from the neighbours
    a,b=max(i-1,1),min(i+1,45); ya,yb=Yfun(a)[0],Yfun(b)[0]; g=(yb-ya)/(X[b-1]-X[a-1]); return np.where(np.isnan(g),0,g)
def band(i,Xf):
    P=face_outer(i,Xf); sm=np.c_[savgol_filter(P[:,0],21,3),savgol_filter(P[:,1],21,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]
    g=np.interp(P[:,1],ZG,yx(i)); delta=T*np.sqrt(1+(d[:,1]*g)**2); m=np.c_[-d[:,1],d[:,0]]
    Q=P+m*delta[:,None]; poly=Polygon(np.vstack([[[0.0,P[0,1]]],P,Q[::-1]])).buffer(0); poly=poly.intersection(box(0,-10,200,300))   # base closes at the centre line (floor crosses over the keel)
    
    return poly,P,Q,m
def pieces_of_frame(i):
    xc=X[i-1]; bandA=unary_union([band(i,xc-4)[0],band(i,xc)[0]]).buffer(0); bandF=unary_union([band(i,xc)[0],band(i,xc+4)[0]]).buffer(0)
    P0,m0=band(i,xc)[1],band(i,xc)[3]
    def joints(layer,names):
        zs=[]
        for nm in names:
            pl=[Polygon(p['poly']) for p in PCS if p['frame']==i and p['layer']==layer and p['piece']==nm and p['side'] in('S','C')]
            zs.append(max(g.bounds[3] for g in pl))
        return zs
    def cutter(z):
        k=int(np.argmin(np.abs(P0[:,1]-z))); p=P0[k]; m=m0[k]; return LineString([tuple(p-3*m),tuple(p+60*m)])
    def divide(blk,zs):
        parts=[blk]
        for z in zs:
            nxt=[]
            for g in parts:
                r=split(g,cutter(z)); nxt+=list(r.geoms)
            parts=nxt
        parts=[g for g in parts if g.area>1.0]; parts.sort(key=lambda g:g.centroid.y); return parts
    zA=joints('A',['floor','fut2']); zF=joints('F',['fut1','fut3'])
    return divide(bandA,zA),divide(bandF,zF),bandA,bandF
def mirror(g): return affinity.scale(g,xfact=-1,yfact=1,origin=(0,0))
def label_set(b):   # builder frame number b -> labels by piece role (layer A: floor 1, fut2 2/7, top 3/6; layer F: fut1 8/13, fut3 9/12, top 10/11)
    return {'A':[(f'{b}-1',None),(f'{b}-2',f'{b}-7'),(f'{b}-3',f'{b}-6')],'F':[(f'{b}-8',f'{b}-13'),(f'{b}-9',f'{b}-12'),(f'{b}-10',f'{b}-11')]}
def build(i):
    b=46-i; A,F,bA,bF=pieces_of_frame(i); L=label_set(b); out=[]
    if len(A)>=3:
        fl=unary_union([A[0].buffer(0.01),mirror(A[0]).buffer(0.01)]).buffer(-0.01)
        out+=[(L['A'][0][0],'A',fl),(L['A'][1][0],'A',A[1]),(L['A'][1][1],'A',mirror(A[1])),(L['A'][2][0],'A',A[2]),(L['A'][2][1],'A',mirror(A[2]))]
    for k,(s,p) in enumerate(L['F']):
        if k<len(F): out+=[(s,'F',F[k]),(p,'F',mirror(F[k]))]
    return b,out,(bA,bF)
if __name__=='__main__':
    frames=[45,44,43,42,41]; fig,axs=plt.subplots(len(frames),2,figsize=(26,9*len(frames)),gridspec_kw={'width_ratios':[1,1.6]}); R={}
    import ezdxf
    doc=ezdxf.new('R2010'); msp=doc.modelspace(); yoff=0
    for r,i in enumerate(frames):
        b,out,(bA,bF)=build(i); R[b]=out; a0,a1=axs[r]
        for nm,lay,g in out:
            col='tab:blue' if lay=='A' else 'tab:red'
            for gg in (g.geoms if hasattr(g,'geoms') else [g]):
                a0.fill(*gg.exterior.xy,color=col,alpha=.18,lw=0); a0.plot(*gg.exterior.xy,color=col,lw=.9)
                c=gg.representative_point(); a0.text(c.x,c.y,nm,fontsize=7,ha='center')
        a0.set_aspect('equal'); a0.set_title(f'frame {b} (our {i}), X={X[i-1]:.1f}: assembled, layer A blue / layer F red'); a0.grid(alpha=.2)
        # nested layout: pieces placed in rows, translated to the origin of their bounding boxes
        x=0; y=0; rowh=0
        for nm,lay,g in sorted(out,key=lambda t:(t[1],t[0])):
            g0=affinity.translate(g,-g.bounds[0],-g.bounds[1]); w=g0.bounds[2]; h=g0.bounds[3]
            if x+w>330: x=0; y+=rowh+6; rowh=0
            gp=affinity.translate(g0,x,-y-h); col='tab:blue' if lay=='A' else 'tab:red'
            for gg in (gp.geoms if hasattr(gp,'geoms') else [gp]):
                a1.fill(*gg.exterior.xy,color=col,alpha=.15,lw=0); a1.plot(*gg.exterior.xy,color=col,lw=.9)
                c=gg.representative_point(); a1.text(c.x,c.y,nm,fontsize=8,ha='center')
                msp.add_lwpolyline([(px,py-yoff) for px,py in gg.exterior.coords],close=True,dxfattribs={'layer':f'F{b}_{lay}'})
                msp.add_text(nm,dxfattribs={'layer':f'F{b}_{lay}','height':2.0,'insert':(c.x,c.y-yoff)})
            x+=w+6; rowh=max(rowh,h)
        yoff+=y+rowh+30
        a1.set_aspect('equal'); a1.set_title(f'frame {b}: cutting layout (mm)'); a1.grid(alpha=.2)
        print(f'frame {b}:',[(nm,lay,round(g.area),round(max(g.bounds[2]-g.bounds[0],g.bounds[3]-g.bounds[1]),1)) for nm,lay,g in out])
    plt.savefig('qa/cutting_plan_frames_b1-5.png',dpi=45,bbox_inches='tight'); doc.saveas('rhino/cutting_plan_frames_b1-5.dxf')
