import sys,json,csv,numpy as np
S=sys.argv[1]; O=S+'/out'
meta=json.load(open(O+'/meta.json')); WLZ=meta['WLZ_mm']; STX={int(k):v for k,v in meta['STX'].items()}
st=np.load(O+'/stations.npy',allow_pickle=True).item()
cmp_=json.load(open(O+'/cmp_rows.json'))
def ycross(P,z):
    out=[]
    for i in range(len(P)-1):
        z0,z1=P[i,1],P[i+1,1]
        if (z0-z)*(z1-z)<=0 and z0!=z1:
            t=(z-z0)/(z1-z0); out.append(P[i,0]+t*(P[i+1,0]-P[i,0]))
    return max(out) if out else None
WLN=['I','II','III','IV','V','VI','VII']
rows=[]
for s in range(18,0,-1):
    P=st.get(f'{s}_1a', st.get(f'{s}_1b')); src='A1/2 (aft body plan)' if f'{s}_1a' in st else 'A1/3 (fwd body plan)'
    r={'station':s,'X_mm':round(STX[s],2)}
    for n in WLN:
        y=ycross(P,WLZ[n]); r['WL_'+n]=round(y,2) if y is not None and y>3.3 else ''
    top=P[np.argmax(P[:,1])]; bot=P[np.argmin(P[:,1])]
    r['top_Y']=round(top[0],2); r['top_Z']=round(top[1],2); r['heel_Y']=round(bot[0],2); r['heel_Z']=round(bot[1],2)
    r['maxY']=round(P[:,0].max(),2); r['Z_at_maxY']=round(P[np.argmax(P[:,0]),1],2); r['source']=src
    rows.append(r)
hdr=list(rows[0].keys())
with open(O+'/offsets_1to48_mm.csv','w',newline='') as f:
    f.write('# Royal Caroline - table of offsets, MODEL 1:48, millimetres. Y=half-breadth from centreline (moulded, from body plan), Z above baseline, X forward of station 18.\n')
    f.write('# WL heights Z(mm): '+', '.join(f'{k}={v:.2f}' for k,v in WLZ.items())+'. Real ship = x48. Empty = WL does not cut this station outside the keel.\n')
    w=csv.DictWriter(f,fieldnames=hdr); w.writeheader(); w.writerows(rows)
for r in rows: print(' '.join(f'{r[k]!s:>7}' for k in hdr[:9]))
