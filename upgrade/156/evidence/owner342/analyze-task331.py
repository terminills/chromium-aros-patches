from pathlib import Path
import json,re,time
E=Path(__file__).parent;deadline=time.monotonic()+7200
while not (E/'compact331-ledger-audit.json').exists():
 assert time.monotonic()<deadline;time.sleep(5)
groups={};phase=None
for line in (E/'compact331-serial.log').read_text().splitlines():
 m=re.search(r'\[TASK318\] begin phase=(\S+) count=(\d+)',line)
 if m:phase=m[1];groups[phase]={'declared':int(m[2]),'rows':[]}
 m=re.search(r'row task=([0-9a-f]+) id=(\d+) state=(\d+) lower=([0-9a-f]+) upper=([0-9a-f]+) name=(.*)',line)
 if m:groups[phase]['rows'].append(dict(task=int(m[1],16),id=int(m[2]),state=int(m[3]),lower=int(m[4],16),upper=int(m[5],16),name=m[6]))
assert all(g['declared']==len(g['rows']) for g in groups.values())
(E/'task331-snapshots.json').write_text(json.dumps({k:v['rows'] for k,v in groups.items()},indent=2))
current=json.loads((E/'compact331-result.json').read_text());baseline=json.loads((E/'compact296-result.json').read_text());measure={r['phase']:r for r in current['measurements']};bmeasure={r['phase']:r for r in baseline['measurements']};phases=[]
for phase,g in groups.items():
 rows=g['rows'];phases.append({'phase':phase,'tasks':len(rows),'stack_bytes':sum(r['upper']-r['lower'] for r in rows),'used_bytes':measure[phase]['bytes']['used'],'baseline296_used_bytes':bmeasure.get(phase,{}).get('bytes',{}).get('used')})
cycles=[(int(p['phase'].split('-')[1]),p['used_bytes']) for p in phases if p['phase'].startswith('cycle-') and int(p['phase'].split('-')[1])>=10]
xm=sum(x for x,y in cycles)/len(cycles);ym=sum(y for x,y in cycles)/len(cycles);slope=sum((x-xm)*(y-ym) for x,y in cycles)/sum((x-xm)**2 for x,y in cycles)
r={'source':'native-scopes329-all-snapshot/manifest.json','engine':'master330-x64-cef-link-result.json','baseline':'compact296-inputs.json','candidate':'compact331-inputs.json','functional_pass':current['functional_pass'],'ledger':json.loads((E/'compact331-ledger-audit.json').read_text()),'phases':phases,'cycle10_to30_growth_mib':(measure['cycle-30']['bytes']['used']-measure['cycle-10']['bytes']['used'])/1048576,'cycle10_to30_slope_mib':slope/1048576,'scope':'Whole-guest thirty-cycle comparison against296 same OS/client workload.331 adds task-resource diagnostic also used318/323; no CPU performance claim. Growth remains release gate until characterized.'}
(E/'task331-comparison.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in ['functional_pass','cycle10_to30_growth_mib','cycle10_to30_slope_mib','phases']},indent=2))
