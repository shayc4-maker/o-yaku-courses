# side view: the whole existing backbone (STEP profiles, NOT moved) on the original sheer plan + the lower end of every frame (outer line at the keel wall, pocket floor, seat) at X-4..X+4
import sys,json,numpy as np
sys.path.insert(0,'py')
from frame_arm import *
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
BB=json.load(open('data/step44_profiles.json'))
PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
rows=[]
for n,X in enumerate(F.XF,1):
    b=46-n
    try:
        for nm,x in (('m',X-4),('c',X),('p',X+4)):
            p,i=arm(x); rows.append((b,nm,x,i['hull_at_wall'],i['floor'],i['seat']))
    except Exception as e: print('frame',b,'failed',str(e)[:60])
json.dump(rows,open('data/frames_bottom_side_shift.json','w'))
