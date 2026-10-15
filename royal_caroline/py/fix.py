import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from track import *
from PIL import Image
S=sys.argv[2]
for name,img,ids_r,yr,ids_c,xr,osr,osc,tops in [
  ('1a',S+'/a/plan_1a_aligned.png',[8,9,10,11],range(900,1460),[8,9,10],None,-1,+1,{8:897}),
  ('1b',S+'/a/plan_1b_aligned.png',[8,7,6,5,4],range(800,1700),[8,7,6,5],range(2950,3250),+1,+1,{6:783,7:793,8:797}),
]:
    B=np.array(Image.open(img).convert('L'))<128
    cur={int(k):np.array(v) for k,v in json.load(open(S+'/tr%s.json'%name)).items()}
    r=snap(B,cur,ids_r,yr,'row',osr); print(name,'row snaps',{i:len(r[i]) for i in r})
    cur=apply_snap(cur,r,'row')
    if xr is not None:
        r=snap(B,cur,ids_c,xr,'col',osc); print(name,'col snaps',{i:len(r[i]) for i in r}); cur=apply_snap(cur,r,'col')
    for i,yt in tops.items():
        c=cur[i]; cur[i]=c[c[:,1]>=yt-0.5]
    json.dump({k:v.tolist() for k,v in cur.items()},open(S+'/tr%s_fix.json'%name,'w'))
