# Assembly for review in Rhino: builder backbone + all 45 frames (v10, not yet refitted to the new seats) + bow HT1-10 + stern v4 (6 counter timbers with knee, arc wing transom, notched post, transoms, rudder)
import rhino3dm as r3
srcs={'frames':r3.File3dm.Read('rhino/RoyalCaroline_frames45_on_new_keel_REF.3dm'),
      'bow':r3.File3dm.Read('rhino/RoyalCaroline_bow_HT_v2.3dm'),
      'stern':r3.File3dm.Read('rhino/RoyalCaroline_stern_v4.3dm')}
out=r3.File3dm(); out.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
L={}
def lay(name,col):
    if name not in L:
        l=r3.Layer(); l.Name=name; l.Color=col; L[name]=out.Layers.Add(l)
    return L[name]
cnt={}
def add(src,keep,prefix=''):
    f=srcs[src]
    for o in f.Objects:
        lyr=f.Layers[o.Attributes.LayerIndex]; n=lyr.Name
        if not keep(n): continue
        at=r3.ObjectAttributes(); at.LayerIndex=lay(prefix+n,lyr.Color); at.Name=o.Attributes.Name
        g=o.Geometry
        if isinstance(g,r3.Brep) or isinstance(g,r3.Extrusion): out.Objects.AddBrep(g if isinstance(g,r3.Brep) else g.ToBrep(True),at)
        elif isinstance(g,r3.Curve): out.Objects.AddCurve(g,at)
        elif isinstance(g,r3.Point): out.Objects.AddPoint(g.Location,at)
        else:
            try: out.Objects.AddTextDot(g.Text,g.Point,at)
            except Exception: continue
        cnt[prefix+n]=cnt.get(prefix+n,0)+1
add('frames',lambda n:n.startswith('FRAME_'),'')                       # 45 frames
add('stern',lambda n:True,'')                                          # backbone (builder, 5.3 mm), stern parts, rudder
add('bow',lambda n:n.startswith('HT') or n.startswith('HAWSE'),'')     # HT1..10 + hawse hole markers (no duplicate backbone/frames)
out.Write('rhino/RoyalCaroline_assembly_v1.3dm',7)
print(len(out.Objects),'objects,',len(out.Layers),'layers')
fr=[k for k in cnt if k.startswith('FRAME_')]; print(len(fr),'frame layers, objects',sum(cnt[k] for k in fr))
print({k:v for k,v in cnt.items() if not k.startswith('FRAME_')})
