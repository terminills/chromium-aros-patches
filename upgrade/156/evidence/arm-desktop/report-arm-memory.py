from pathlib import Path
import json,re
r=Path('/mnt/short-term/job0254-01a1e62b/runtime-arm')
e=Path('/run/media/terminills/Amiwest/job0254-01a1e62b/evidence')
s=(r/'aux-serial.log').read_text(errors='replace')
records=[]
for match in re.finditer(r'\[ARM-MEM\] label=(\S+) total=(\S+) free=(\S+) used=(\S+) largest=(\S+)',s):
 item={'label':match[1]}
 for name,v in zip(['total','free','used','largest'],match.groups()[1:]):item[name+'_bytes']=int(v,16)
 records.append(item)
assert records,'No native ARM memory readings; do not infer guest use from host memory'
baseline=next((x for x in records if x['label']=='idle-desktop'),None)
for item in records:
 if baseline:item['used_delta_from_idle_bytes']=item['used_bytes']-baseline['used_bytes']
host={}
try:
 pid=int((r/'qemu.pid').read_text())
 for line in Path(f'/proc/{pid}/status').read_text().splitlines():
  if line.startswith(('VmRSS:','VmSize:')):host[line.split(':')[0]+'_KiB']=int(line.split()[1])
except FileNotFoundError:pass
report={'architecture':'AArch64','guest_measurement':'Exec AvailMem; system totals, not exclusive application attribution','guest_records':records,'host_qemu_separate':host,'first_paint_observed':'[CEF-BROWSER] first paint' in s}
(e/'arm-desktop-memory.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
