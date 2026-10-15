# Closed backbone parts (profile, XZ) from backbone_split_v5 + post top raised to dots 244/245 (Z 90.5)
import json
import rhino3dm as r3, ezdxf
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sp=json.load(open('data/backbone_split_v5.json'))
dots={d['id']:d for d in json.load(open('scan/dots_merged.json'))}
a,b=dots[245],dots[244]
P=[tuple(p) for p in sp['STERNPOST'][:-1]]
i=P.index(next(p for p in P if abs(p[0]+16.01)<.02 and abs(p[1]-83.8)<.02))
assert abs(P[i+1][0]+8.24)<.02 and abs(P[i+1][1]-83.8)<.02
P[i:i+2]=[(a['X'],a['Z']),(b['X'],b['Z'])]
sp['STERNPOST']=P+[P[0]]
parts={}
for k,v in sp.items():
    pg=Polygon(v); assert pg.is_valid,k
    parts[k]=[(round(x,3),round(z,3)) for x,z in v]
json.dump(parts,open('data/backbone_parts_v1.json','w'))
# 3dm: one layer per part, closed polyline in the XZ plane (Y=0)
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
cols=plt.cm.tab20.colors
for n,(k,v) in enumerate(parts.items()):
    li=r3.Layer(); li.Name=k; c=cols[n%20]; li.Color=tuple(int(255*t) for t in c)+(255,)
    idx=f.Layers.Add(li)
    pl=r3.Polyline(len(v))
    for x,z in v: pl.Add(x,0.0,z)
    at=r3.ObjectAttributes(); at.LayerIndex=idx; at.Name=k
    f.Objects.AddPolyline(pl,at)
f.Write('rhino/RoyalCaroline_backbone_parts_v1.3dm',7)
doc=ezdxf.new('R2010'); doc.units=4; m=doc.modelspace()
for k,v in parts.items():
    doc.layers.add(k); m.add_lwpolyline(v,close=True,dxfattribs={'layer':k})
doc.saveas('rhino/RoyalCaroline_backbone_parts_v1.dxf')
fig,axs=plt.subplots(3,1,figsize=(22,13))
for ax,(x0,x1) in zip(axs,[(-20,200),(180,380),(360,620)]):
    for n,(k,v) in enumerate(parts.items()):
        x=[p[0] for p in v];z=[p[1] for p in v]
        ax.fill(x,z,color=cols[n%20],alpha=.45);ax.plot(x,z,'k',lw=.5)
        pg=Polygon(v).representative_point()
        if x0<=pg.x<=x1: ax.text(pg.x,pg.y,k,fontsize=6,ha='center')
    ax.set_xlim(x0,x1);ax.set_ylim(-12,120 if x1>500 else 95 if x0<0 else 40);ax.set_aspect('equal')
plt.tight_layout();plt.savefig('qa/parts_v1.png',dpi=75)
print(len(parts),'parts');print({k:round(Polygon(v).area,1) for k,v in parts.items()}['STERNPOST'])
