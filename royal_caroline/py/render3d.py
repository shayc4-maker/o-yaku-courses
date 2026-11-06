import sys,json,subprocess,numpy as np,os,glob
parts=np.load('/tmp/claude-0/x/parts3d.npy',allow_pickle=True).item(); hull=np.load('/tmp/claude-0/x/hull_patch.npy',allow_pickle=True).item()
def pack(p,mirror=False):
    v=np.asarray(p['v'],float); t=np.asarray(p['t'],int)
    if mirror: v=v*np.array([1,-1,1]); t=t[:,::-1]
    return dict(v=np.round(v,3).ravel().tolist(),t=t.ravel().tolist())
scene=[]
for k,p in parts.items():
    col='#c8a165' if k.startswith('FRAME') and k.endswith('_A') else ('#a77b45' if k.startswith('FRAME') else ('#6b8f5a' if k=='KEELSON' else '#7a4f2b'))
    scene.append(dict(name=k,color=col,opacity=1.0,**pack(p)))
scene.append(dict(name='HULL_R',color='#7fa6c9',opacity=0.22,**pack(hull))); scene.append(dict(name='HULL_L',color='#7fa6c9',opacity=0.22,**pack(hull,True)))
json.dump(scene,open('/tmp/claude-0/x/scene.json','w'))
html='''<!doctype html><html><head><meta charset=utf-8><style>html,body{margin:0;background:#fff}</style></head><body>
<script src="three.min.js"></script><script>
async function run(cfg){
 const sc=await (await fetch('scene.json')).json();
 const W=cfg.w,H=cfg.h,ren=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});ren.setSize(W,H);ren.setClearColor(0xf4f4f2);document.body.appendChild(ren.domElement);
 const scene=new THREE.Scene();
 const m2t=(x,y,z)=>new THREE.Vector3(x,z,-y);
 for(const p of sc){ if(cfg.hide&&cfg.hide.some(h=>p.name.startsWith(h)))continue; if(cfg.only&&!cfg.only.some(h=>p.name.startsWith(h)))continue;
  const g=new THREE.BufferGeometry(); const v=p.v,pos=new Float32Array(v.length); for(let i=0;i<v.length;i+=3){pos[i]=v[i];pos[i+1]=v[i+2];pos[i+2]=-v[i+1];}
  g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setIndex(p.t); g.computeVertexNormals();
  const hullp=p.name.startsWith('HULL');
  const mat=new THREE.MeshStandardMaterial({color:p.color,roughness:.75,metalness:0,side:hullp?THREE.DoubleSide:THREE.FrontSide,transparent:hullp,opacity:p.opacity,depthWrite:!hullp,flatShading:false});
  const me=new THREE.Mesh(g,mat);scene.add(me);
  if(!hullp){const eg=new THREE.EdgesGeometry(g,35);const l=new THREE.LineSegments(eg,new THREE.LineBasicMaterial({color:0x222222,transparent:true,opacity:.35}));scene.add(l);} }
 scene.add(new THREE.HemisphereLight(0xffffff,0x888877,1.0)); const d=new THREE.DirectionalLight(0xffffff,1.6);d.position.set(...cfg.light);scene.add(d);
 const cam=new THREE.PerspectiveCamera(cfg.fov,W/H,0.5,3000); cam.position.copy(m2t(...cfg.eye)); cam.lookAt(m2t(...cfg.target)); cam.up.set(0,1,0); ren.render(scene,cam); window.done=true;}
</script></body></html>'''
os.makedirs('/tmp/claude-0/x/three/web',exist_ok=True); open('/tmp/claude-0/x/three/web/index.html','w').write(html)
import shutil; shutil.copy('/tmp/claude-0/x/three/node_modules/three/build/three.min.js','/tmp/claude-0/x/three/web/three.min.js'); shutil.copy('/tmp/claude-0/x/scene.json','/tmp/claude-0/x/three/web/scene.json')
print('scene parts',len(scene),'json MB %.1f'%(os.path.getsize('/tmp/claude-0/x/scene.json')/1e6))
