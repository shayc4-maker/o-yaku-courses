import sys,json,numpy as np
sys.path.insert(0,'py')
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import bodyplan_points_all as B
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
D=json.load(open('data/frames_outer_all_v1.json'))['21']; C=json.load(open('data/bodyplan_centered_v1.json')); S8=np.array(C['8']['curve']); S9=np.array(C['9']['curve'])
col={'back':'tab:blue','mid':'k','front':'tab:red'}
print('nearest original line = station 8 (X=303.4); frame 21 faces X:',{k:round(v['X'],1) for k,v in D.items()},'-> distances to station 8: ',{k:round(303.4-v['X'],1) for k,v in D.items()},'; station 9 (270.9) is %.1f mm behind the back face'%(D['back']['X']-270.9))
yz=lambda L,z: float(np.interp(z,L[:,1],L[:,0]))
print('Y at Z | station 8 | back | mid | front | (face - station 8)')
for z in (3,6,10,15,20,30,40,50,60,70,80,90,100):
    r=[yz(S8,z)]+[yz(np.array(D[k]['curve']),z) for k in ('back','mid','front')]; print(z,[round(v,2) for v in r],[round(v-r[0],2) for v in r[1:]])
fig,axs=plt.subplots(3,1,figsize=(15,34),gridspec_kw={'height_ratios':[1.1,.7,1.3]})
for a in axs[:2]:
    a.plot(S8[:,0],S8[:,1],color='orange',lw=1.6,label='station 8 (original body plan line, centre-aligned)'); a.plot(S9[:,0],S9[:,1],color='gray',ls='--',lw=.8,label='station 9')
    for nm,v in D.items(): L=np.array(v['curve']); a.plot(L[:,0],L[:,1],color=col[nm],lw=1.1,label='frame 21 %s X=%.1f (%+.1f mm from station 8)'%(nm,v['X'],v['X']-303.4))
axs[0].set_xlim(0,80); axs[0].set_ylim(-3,125); axs[0].set_aspect('equal'); axs[0].legend(fontsize=8); axs[0].grid(alpha=.3); axs[0].set_title('Frame 21 faces vs the nearest original body plan line (station 8)')
axs[1].set_xlim(0,75); axs[1].set_ylim(55,125); axs[1].set_aspect('equal'); axs[1].grid(alpha=.3); axs[1].set_title('upper part')
# on the original plan image: raw Y = Ycentred + Yc(Z)
cf=B.CFG['fwd']; box=(2380,500,3750,2150); im=Image.open('plans/plan_1b_aligned.png').convert('RGB').crop(box); axs[2].imshow(im,extent=(box[0],box[2],box[3],box[1]))
ycf=lambda z:1.645-0.00799*z
for L,c,lw,lab in [(S8,'orange',1.6,'station 8')]+[(np.array(v['curve']),col[k],1.0,'frame 21 '+k) for k,v in D.items()]:
    x,y=B.px(cf,L[:,0]+ycf(L[:,1]),L[:,1]); axs[2].plot(x,y,color=c,lw=lw,label=lab)
axs[2].set_xlim(box[0],box[2]); axs[2].set_ylim(box[3],box[1]); axs[2].axis('off'); axs[2].legend(fontsize=8,loc='upper right'); axs[2].set_title('same lines on the original forward body plan (plan_1b)')
fig.savefig('qa/frame21_vs_station8.png',dpi=55,bbox_inches='tight')
with PdfPages('qa/frame21_vs_station8.pdf') as pdf: pdf.savefig(fig)
