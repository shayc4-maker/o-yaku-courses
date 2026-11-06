# runs frame_allowance_2d.py for all 45 frames in groups of 5 in ONE process (the hull loft is built once)
import sys,runpy,os
os.environ['NOSTEP']='1'; os.environ['INNER_SMOOTH']='1'
groups=[[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15],[16,17,18,19,20],[21,22,23,24,25],[26,27,28,29,30],[31,32,33,34,35],[36,37,38,39,40],[41,42,43,44,45]]
for g in groups:
    sys.argv=['frame_allowance_2d.py']+[str(x) for x in g]; print('== group',g,flush=True)
    try: runpy.run_path('py/frame_allowance_2d.py',run_name='__main__')
    except Exception as e: print('FAILED group',g,repr(e)[:200],flush=True)
