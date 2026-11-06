import json,numpy as np,os,shutil
D=np.load('/tmp/claude-0/x/parts_blanks.npy',allow_pickle=True).item(); parts=D['parts']; lines=D['lines']
def pack(p): return dict(v=np.round(np.asarray(p['v'],float),3).ravel().tolist(),t=np.asarray(p['t'],int).ravel().tolist())
scene=[]
for k,p in parts.items():
    if k=='KEELSON' or k=='KEEL_DEADWOOD':
        v=np.asarray(p['v']); m=(v[:,0]>440)
        # keep whole keel/keelson (small)
    col='#d9b98a' if k.startswith('FRAME') and k.endswith('_A') else ('#c9a46c' if k.startswith('FRAME') else ('#6b8f5a' if k=='KEELSON' else '#7a4f2b'))
    scene.append(dict(name=k,color=col,kind='mesh',**pack(p)))
for l in lines: scene.append(dict(name=l['name'],kind='line',pts=np.asarray(l['pts']).ravel().tolist(),color='#d01818'))
json.dump(scene,open('/tmp/claude-0/x/three/web/scene.json','w'))
html=open('/tmp/claude-0/x/three/web/index.html').read()
html=html.replace("const hullp=p.name.startsWith('HULL');","const hullp=p.name.startsWith('HULL');")
# add line support: tubes
html=html.replace("for(const p of sc){ if(cfg.hide","for(const p of sc){ if(p.kind==='line'){ if(cfg.hide&&cfg.hide.some(h=>p.name.startsWith(h)))continue; if(cfg.only&&!cfg.only.some(h=>p.name.startsWith(h)))continue; const q=[];for(let i=0;i<p.pts.length;i+=3){q.push(new THREE.Vector3(p.pts[i],p.pts[i+2],-p.pts[i+1]));} const curve=new THREE.CatmullRomCurve3(q.filter((_,i)=>i%3===0),false); const tg=new THREE.TubeGeometry(curve,Math.min(q.length,600),cfg.lw||0.12,5,false); scene.add(new THREE.Mesh(tg,new THREE.MeshBasicMaterial({color:p.color}))); continue;} if(cfg.hide")
open('/tmp/claude-0/x/three/web/index.html','w').write(html)
print(len(scene))
