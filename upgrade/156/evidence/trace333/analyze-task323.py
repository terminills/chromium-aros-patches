from pathlib import Path
import json,re,time
E=Path(__file__).parent;deadline=time.monotonic()+7200
while not (E/'compact323-ledger-audit.json').exists():
 assert time.monotonic()<deadline;time.sleep(5)
groups={};phase=None
for line in (E/'compact323-serial.log').read_text().splitlines():
 m=re.search(r'\[TASK318\] begin phase=(\S+) count=(\d+)',line)
 if m:phase=m[1];groups[phase]={'declared':int(m[2]),'rows':[]}
 m=re.search(r'row task=([0-9a-f]+) id=(\d+) state=(\d+) lower=([0-9a-f]+) upper=([0-9a-f]+) name=(.*)',line)
 if m:groups[phase]['rows'].append(dict(task=int(m[1],16),id=int(m[2]),state=int(m[3]),lower=int(m[4],16),upper=int(m[5],16),name=m[6]))
assert all(g['declared']==len(g['rows']) for g in groups.values())
(E/'task323-snapshots.json').write_text(json.dumps({k:v['rows'] for k,v in groups.items()},indent=2))
before=json.loads((E/'task318-snapshots.json').read_text());baseline=json.loads((E/'compact318-result.json').read_text());current=json.loads((E/'compact323-result.json').read_text());measure={r['phase']:r for r in current['measurements']};bmeasure={r['phase']:r for r in baseline['measurements']};phases=[]
for phase,g in groups.items():
 rows=g['rows'];br=before[phase];phases.append({'phase':phase,'before_tasks':len(br),'after_tasks':len(rows),'before_stack_bytes':sum(r['upper']-r['lower'] for r in br),'after_stack_bytes':sum(r['upper']-r['lower'] for r in rows),'before_used_bytes':bmeasure[phase]['bytes']['used'],'after_used_bytes':measure[phase]['bytes']['used']})
r={'source':'native-scopes319-all-snapshot/manifest.json','engine':'master320-x64-cef-link-result.json','baseline':'compact318-inputs.json','candidate':'compact323-inputs.json','functional_pass':current['functional_pass'],'ledger':json.loads((E/'compact323-ledger-audit.json').read_text()),'phases':phases,'scope':'Same ten-cycle OS/client/workload comparison, only native engine changed from287/288 to319/320. Whole-guest memory and reserved task stacks are distinct. This does not replace longer plateau or concurrent-app qualification. The reused run helper textual label Fresh-master288 is stale; input manifest hashes identify the actual320 engine.'}
(E/'task323-comparison.json').write_text(json.dumps(r,indent=2));print(json.dumps({'functional_pass':r['functional_pass'],'phases':phases},indent=2))
