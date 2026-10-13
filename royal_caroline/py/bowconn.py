import json, numpy as np, networkx as nx
from scipy.spatial import cKDTree
R=[np.array(l) for l in json.load(open('scan/raw_lines.json'))]
D=json.load(open('scan2/dots_merged.json'))
G=nx.Graph(); pts=[]; 
def add(p):
    pts.append(tuple(p)); return len(pts)-1
ends=[]
for l in R:
    # densify
    seg=np.hypot(*np.diff(l,axis=0).T); u=np.r_[0,np.cumsum(seg)]; uu=np.arange(0,u[-1]+1e-9,0.1)
    q=np.c_[np.interp(uu,u,l[:,0]),np.interp(uu,u,l[:,1])]
    ids=[add(p) for p in q]
    for a,b in zip(ids[:-1],ids[1:]): G.add_edge(a,b)
    ends+= [ids[0],ids[-1]]
P=np.array(pts); tr=cKDTree(P)
# join gaps between line endpoints and anything within 0.7
for e in ends:
    for j in tr.query_ball_point(P[e],0.7):
        if j!=e: G.add_edge(e,j)
dot_nodes={}
for d in D:
    if d['X']<436: continue
    dist,j=tr.query([d['X'],d['Z']])
    if dist<1.0:
        n=('d',d['id']); G.add_edge(n,j); dot_nodes[n]=j
own={}
for n,j in dot_nodes.items():
    for k in tr.query_ball_point(P[j],0.35): own.setdefault(k,set()).add(n)
edges=set()
for n in dot_nodes:
    # BFS not passing through other dots
    seen={n}; fr=[n]
    while fr:
        nf=[]
        for v in fr:
            for w in G[v]:
                if w in seen: continue
                seen.add(w)
                if isinstance(w,tuple): continue
                oth=own.get(w,set())-{n}
                if oth:
                    for o in oth: edges.add(tuple(sorted((n[1],o[1]))))
                    continue
                nf.append(w)
        fr=nf
print(len(dot_nodes),'snapped;',len(edges),'edges')
print(sorted(edges))
json.dump(sorted(edges),open('scan2/bow_edges.json','w'))
