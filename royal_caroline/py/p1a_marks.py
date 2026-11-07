# builder's coloured pixel marks on plan_1a (PDF image 11365x2451 = plan_1a.tif) -> model X,Z (new->aligned affine, inverse of the sheer-plan calibration)
import sys,json,numpy as np,cv2; sys.path.insert(0,'py')
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from p1a_strip import ink,KX,X0,KZ,ZR
af=json.load(open('data/plan1a_new_to_aligned.json')); ax,ay=af['ax'],af['ay']
im=np.array(Image.open('/tmp/pdfx/img-000.png').convert('RGB')).astype(int)
sat=im.max(2)-im.min(2); m=(sat>60).astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(m,connectivity=8)
def model(px,py_):
    xa=ax[0]*px+ax[1]*py_+ax[2]; ya=ay[0]*px+ay[1]*py_+ay[2]
    xi=xa*KX+X0; zi=(ZR-ya)*KZ; X,Z=xi,zi
    for _ in range(5):
        a,c=ink(X,Z); X+=xi-a; Z+=zi-c
    return float(X),float(Z)
def grp(c):
    r,g,b=c
    if g>r+15 and g>b+15: return 'green'
    if abs(r-g)<30 and b<r-40: return 'yellow'
    if abs(r-b)<30 and g<r-40: return 'purple'
    if r>g+40 and r>b+40: return 'red'
    return 'other'
P=[]
for i in range(1,n):
    c=im[lab==i].mean(0); X,Z=model(*cen[i]); P.append(dict(g=grp(c),X=round(X,2),Z=round(Z,2),px=round(float(cen[i][0]),1),py=round(float(cen[i][1]),1)))
P.sort(key=lambda p:p['X'])
for k,p in enumerate(P): p['id']='M%d'%k
json.dump(P,open('data/p1a_marks_v1.json','w'),indent=1)
if __name__=='__main__':
    for p in P: print(p['id'],p['g'],p['X'],p['Z'])
