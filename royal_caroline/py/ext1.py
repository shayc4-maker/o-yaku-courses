import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from track import *
S=sys.argv[2]; D=load_dark(S+'/a/plan_1b_aligned.png')
cur=json.load(open(S+'/tr1b_fix.json')); c=np.array(cur['1'])
top=c[np.argmin(c[:,1])]; print('st1 top',top)
stop=lambda p: p[1]<500
t=trace(D,top+[0,-4],np.array([0.,-1.]),stop,maxang=8)
t=cut_turns(t,0,maxturn=np.radians(40)); print('ext',t[0],t[-1],len(t))
if c[0,1]<c[-1,1]: c=np.r_[t[::-1],c]
else: c=np.r_[c,t]
cur['1']=c.tolist(); json.dump(cur,open(S+'/tr1b_fix.json','w'))
