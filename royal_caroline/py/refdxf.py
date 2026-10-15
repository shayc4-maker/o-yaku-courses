import sys,ezdxf
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
def segs(e):
    t=e.dxftype()
    if t=='LINE': return [[(e.dxf.start.x,e.dxf.start.z),(e.dxf.end.x,e.dxf.end.z)]]
    if t=='POLYLINE': return [[(v.dxf.location.x,v.dxf.location.z) for v in e.vertices]]
    if t=='SPLINE':
        try: return [[(p.x,p.z) for p in e.flattening(0.05)]]
        except Exception: return [[(p[0],p[2]) for p in e.control_points]]
    return []
def load(path):
    d=ezdxf.readfile(path); out={}
    for e in d.modelspace():
        for s in segs(e): out.setdefault(e.dxf.layer,[]).append(s)
    return out
if __name__=='__main__':
    L=load(sys.argv[1]); cols={'01_BODY_OUTER':'0.55','02_KEELSON':'tab:red','03_STERN_KNEE':'tab:blue','04_AFT_DIVISIONS':'tab:green','05_KEEL_HOG_FALSEKEEL':'tab:brown','06_STEM_APRON':'tab:cyan','07_HEAD_GRIPE':'tab:purple','98_JOINED_REVIEW_CURVES':'tab:orange'}
    skip=set(sys.argv[3].split(',')) if len(sys.argv)>3 else set()
    for name,(x0,x1,z0,z1) in {'aft':(-20,125,-12,90),'mid':(170,260,-12,45),'bow':(430,615,-12,125)}.items():
        fig,ax=plt.subplots(figsize=(20,20*(z1-z0)/(x1-x0)))
        for l,ss in L.items():
            if l in skip: continue
            for s in ss:
                a=np.array(s); ax.plot(a[:,0],a[:,1],color=cols.get(l,'k'),lw=.8 if l!='98_JOINED_REVIEW_CURVES' else .5)
        ax.set_xlim(x0,x1);ax.set_ylim(z0,z1);ax.set_aspect('equal');ax.grid(alpha=.2)
        plt.tight_layout();plt.savefig(f'{sys.argv[2]}_{name}.png',dpi=60);plt.close()
