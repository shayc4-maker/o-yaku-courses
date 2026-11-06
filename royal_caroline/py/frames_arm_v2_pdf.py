# vector PDF (zoomable) of frames 1-8 faces X-4 (blue), X (black), X+4 (red), arm rule v2: one page per frame, 4 panels (whole, bottom, inner line into the offset, upper part)
import json,numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
A=json.load(open('data/frames_arm_v2_1_2_3_4_5_6_7_8.json')); mir=lambda g: affinity.scale(g,xfact=-1,yfact=1,origin=(0,0)); cols={'X-4':'tab:blue','X':'k','X+4':'tab:red'}
def full(half):
    h=Polygon(half).buffer(0); g=unary_union([h.buffer(0.005),mir(h).buffer(0.005)]).buffer(-0.005); return max(g.geoms,key=lambda q:q.area) if hasattr(g,'geoms') else g
with PdfPages('qa/frames_arm_v2_1-8.pdf') as pdf:
    for b in range(1,9):
        d=A[str(b)]; f0=d['faces']['X']; fl,se=f0['floor'],f0['seat']; fig,axs=plt.subplots(2,2,figsize=(16,16)); axs=axs.ravel()
        for k,v in d['faces'].items():
            g=full(v['half']); x,y=g.exterior.xy
            for a in axs: a.plot(x,y,color=cols[k],lw=.8,label=k)
        for a,(xl,yl,t) in zip(axs,(((-85,85),(-5,125),'whole'),((-16,16),(fl-4,se+12),'bottom: wall, floor, seat'),((-40,40),(fl-5,se+30),'inner line into the offset line'),((20,85),(60,125),'upper part'))):
            a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.3); a.set_title('frame %d X=%.1f  %s'%(b,d['X'],t),fontsize=11)
        axs[0].legend(fontsize=9); pdf.savefig(fig); plt.close(fig)
print('pdf ok')
