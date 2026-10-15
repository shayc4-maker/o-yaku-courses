import json,subprocess,sys
O=sys.argv[1]; py=sys.argv[2]
for it in range(5):
    subprocess.run([sys.executable,'-I',py,'notabs'],check=True,capture_output=True)
    col=json.load(open(O+'/collisions_v9_notabs.json'))
    bad=set()
    for v,a,b in col:
        for n in (a,b):
            if 'KNEE' in n or n.startswith('PILLAR'): bad.add(n)
    print('iteration',it,'collisions',len(col),'removing',sorted(bad))
    if not col: break
    if not bad: print('non-knee collisions remain'); break
    parts=json.load(open(O+'/parts_v9.json'))
    # remove both sides of a knee if one side collides
    base=set(n[:-2] for n in bad)
    parts=[p for p in parts if not (p['name'][:-2] in base and ('KNEE' in p['name']))  and p['name'] not in bad]
    json.dump(parts,open(O+'/parts_v9.json','w'))
