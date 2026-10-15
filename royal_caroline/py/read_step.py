import sys,re,json
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepCheck import BRepCheck_Analyzer
r=STEPControl_Reader(); r.ReadFile(sys.argv[1]); r.TransferRoots()
sh=r.OneShape(); ex=TopExp_Explorer(sh,TopAbs_SOLID); rows=[]
txt=open(sys.argv[1],errors='ignore').read()
names=re.findall(r"MANIFOLD_SOLID_BREP \( '([^']*)'",txt)
i=0
while ex.More():
    s=ex.Current(); b=Bnd_Box(); BRepBndLib.Add_s(s,b); g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g)
    x0,y0,z0,x1,y1,z1=b.CornerMin().X(),b.CornerMin().Y(),b.CornerMin().Z(),b.CornerMax().X(),b.CornerMax().Y(),b.CornerMax().Z(); c=g.CentreOfMass()
    rows.append(dict(name=names[i] if i<len(names) else '?',vol=g.Mass(),bb=[round(v,2) for v in (x0,y0,z0,x1,y1,z1)],cm=[round(c.X(),1),round(c.Y(),1),round(c.Z(),1)],valid=BRepCheck_Analyzer(s).IsValid()))
    ex.Next(); i+=1
for r_ in rows: print(r_)
json.dump(rows,open(sys.argv[2],'w'))
