# all relevant bow lines in space (Rhino 3dm) for checking: approved frame outer lines (copied from the builder's file), stations 1-8 and waterlines I-VII (centre-aligned), rabbet v3, STEP backbone/stem solids, deck-plan points (lower deck 4b: frame line F approved + outer H; upper deck 4a: H/F not approved + arc Q1-Q5/C; positions ROUGH: plan px -> mm at 11.75 px/mm, Y from the mast centre line, X registered by C = stem aft face at the deck height (540.8 at Z 47; 555.0 at Z 86-88), Z from a provisional deck height function). Layers say what is approved and what is reference.
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,CubicSpline
S=11.75
yc_mid4b=lambda x:1079.3-0.00272*x      # symmetric mid-line of the 4b outline (matches the approved frames better than the mast line)
yc_mid4a=lambda x:1061.7-0.00136*x      # same for plan_4a
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Visible=vis; l.Color=col; LI[n]=f.Layers.Add(l); return LI[n]
def add(g,ln,name):
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.Add(g,a)
def pt(x,y,z,ln,name): a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.AddPoint(r3.Point3d(x,y,z),a)
def spline(q3):
    q=np.array(q3,float); keep=[0]+[i for i in range(1,len(q)) if np.linalg.norm(q[i]-q[i-1])>1e-6]; q=q[keep]; tck,u=splprep(q.T,k=3,s=0); t,c,k=tck
    P=[r3.Point3d(c[0][i],c[1][i],c[2][i]) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,3,P); tt=t[1:-1]
    for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
    return nc
# 1. approved frame outer lines, copied
src=r3.File3dm.Read('/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/c8f595d5-RoyalCaroline_frames_outer_lines_v1.3dm'); SL={i:src.Layers[i].Name for i in range(len(src.Layers))}
lA=layer('APPROVED_frames_outer_lines_+Y',(200,0,0,255)); lAm=layer('APPROVED_frames_outer_lines_-Y',(0,0,200,255))
for o in src.Objects:
    n=SL[o.Attributes.LayerIndex]
    if n=='OUTER_faces_+Y': add(o.Geometry.Duplicate(),lA,o.Attributes.Name)
    elif n=='OUTER_faces_-Y': add(o.Geometry.Duplicate(),lAm,o.Attributes.Name)
# 2. stations 1-8 and waterlines (centre-aligned data)
C=json.load(open('data/bodyplan_centered_v1.json')); W=json.load(open('data/wl_top_centered_v1.json')); ENDS=json.load(open('data/bodyplan_ends_centered_v1.json'))
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4}
lS=layer('REF_stations_1-8_centred',(120,0,120,255)); lW=layer('REF_waterlines_I-VII_centred',(230,120,0,255))
for n,X in XST.items():
    P=np.array(C[str(n)]['points']); e=ENDS[str(n)]['end']; q=np.vstack([[e[0],e[1]],P])
    for sg in (1,-1): add(spline([(X,sg*y,z) for y,z in q]),lS,'ST%d_%s'%(n,'R' if sg>0 else 'L'))
for k,v in W.items():
    Pw=np.array(v['points_XY']); Pw=Pw[np.argsort(Pw[:,0])]; m=Pw[:,0]>300
    for sg in (1,-1): add(spline([(x,sg*y,v['z']) for x,y in Pw[m]]),lW,'WL_%s_%s'%(k,'R' if sg>0 else 'L'))
# 3. rabbet v3 (Y=0), STEP solids
RB=json.load(open('data/rabbet_points_v3_ends.json'))['points']; lR=layer('REF_rabbet_v3_Y0',(0,0,0,255)); add(spline([(x,0.0,z) for x,z in RB]),lR,'RABBET_v3')
bf=r3.File3dm.Read('rhino/RoyalCaroline_backbone_solids_v1.3dm'); BL={i:bf.Layers[i].Name for i in range(len(bf.Layers))}; lB=layer('REF_backbone_STEP_solids',(150,150,150,255))
for o in bf.Objects:
    if o.Geometry.ObjectType.name=='Brep': add(o.Geometry.Duplicate(),lB,BL[o.Attributes.LayerIndex])
# 4. deck points (ROUGH)
def zlow(X): return float(np.interp(X,[480,490],[35.0,47.0]))
def zup(X): return float(np.interp(X,[460,480,500,520,540,550,556],[83.3,83.8,84.3,85.4,87.5,89.7,90.5]))
V4b=json.load(open('data/lowerdeck_bow_points_v2.json'))['points']; XC4b,xC4b=540.8,7425.0
lF=layer('DECK_lower_4b_F_frame_line_APPROVED_rough_pos',(0,160,0,255)); lH=layer('DECK_lower_4b_H_outer_ref',(160,220,160,255)); lC=layer('DECK_C_T_stem_corner_ref',(0,0,0,255))
for r in V4b:
    if 'frame_id' in r:
        X=XC4b+(r['frame_x_px']-xC4b)/S; Y=(yc_mid4b(r['frame_x_px'])-r['frame_y_px'])/S; Z=zlow(X)
        for sg in (1,-1): pt(X,sg*Y,Z,lF,'%s_%s'%(r['frame_id'],'R' if sg>0 else 'L'))
        X=XC4b+(r['x_px']-xC4b)/S
        for sg in (1,-1): pt(X,sg*(yc_mid4b(r['x_px'])-r['y_px'])/S,zlow(X),lH,'%s_%s'%(r['id'],'R' if sg>0 else 'L'))
    elif r['id'] in ('C','T'):
        X=XC4b+(r['x_px']-xC4b)/S
        for sg in (1,-1): pt(X,sg*2.65,47.0,lC,'4b_%s_%s'%(r['id'],'R' if sg>0 else 'L'))
V4a=json.load(open('data/upperdeck_4a_bow_points_v4.json'))['points']; Q=json.load(open('data/upperdeck_4a_bow_arc_ref_v1.json'))['points']; XCu,xCu=555.0,7424.0
lU=layer('DECK_upper_4a_H_F_NOT_approved_ref',(220,140,0,255)); lQ=layer('DECK_upper_4a_arc_ref_Q_C',(0,120,220,255))
for r in V4a:
    for key,ln in (('H',lU),('F',lU)):
        X=XCu+(r['%s_x_px'%key]-xCu)/S
        for sg in (1,-1): pt(X,sg*(yc_mid4a(r['%s_x_px'%key])-r['%s_y_px'%key])/S,zup(X),ln,'%s%d_%s'%(key,r['id'],'R' if sg>0 else 'L'))
for r in Q:
    X=XCu+(r['x_px']-xCu)/S
    for sg in (1,-1): pt(X,sg*(yc_mid4a(r['x_px'])-r['y_px'])/S,zup(X),lQ,'%s_%s'%(r['id'],'R' if sg>0 else 'L'))
# 5. deck level reference lines in the side view (Y=0)
lL=layer('REF_deck_levels_side_provisional',(120,120,120,255),True)
add(r3.PolylineCurve([r3.Point3d(x,0,zlow(x)) for x in np.linspace(440,545,12)]),lL,'lower_deck_level_provisional'); add(r3.PolylineCurve([r3.Point3d(x,0,zup(x)) for x in np.linspace(440,556,12)]),lL,'upper_deck_level_provisional')
f.Write('rhino/RoyalCaroline_bow_lines_in_space_v1.3dm',7); print('objects',len(f.Objects),'layers',len(f.Layers))
# registration check numbers

