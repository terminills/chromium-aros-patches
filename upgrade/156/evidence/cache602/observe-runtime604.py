from pathlib import Path
import time,json,re,subprocess,socket
from native_child_accounting import account_children
from PIL import Image
E=Path(__file__).parent;D=Path('/home/terminills/job0254-release-staging/runtime604')
end=time.monotonic()+14400
while not (D/'qemu.pid').exists():
 assert time.monotonic()<end;time.sleep(5)
pid=int((D/'qemu.pid').read_text());deadline=time.monotonic()+5400;captured=False;terminal_at=None;sampled=set()
while True:
 s=(D/'serial.log').read_text(errors='replace');alive=Path('/proc/'+str(pid)).exists();fault=any(x in s for x in ['[Chromium:FATAL]','[UserAlert] Program failed','Software Failure!']);account=account_children(s)
 if 'MEM604-finished' in s and terminal_at is None:terminal_at=time.monotonic()
 if not alive or fault or time.monotonic()>deadline or (terminal_at and (account['all_started_children_returned'] or time.monotonic()-terminal_at>30)):break
 time.sleep(2)
(E/'runtime604-lifecycle.log').write_text(s)
measure=[]
for phase,total,free,used,largest in re.findall(r'\[CEF-CYCLE-MEM\] phase=(\S+) total=([0-9a-fA-F]+) free=([0-9a-fA-F]+) used=([0-9a-fA-F]+) largest=([0-9a-fA-F]+)',s):
 v={k:int(x,16) for k,x in [('total',total),('free',free),('used',used),('largest',largest)]};measure.append({'phase':phase,'bytes':v,'mib':{k:round(x/1048576,2) for k,x in v.items()}})
markers=[f'MEM604-cycle-{n}-returned:0' for n in range(1,101)]+['MEM604-host-returned:0','MEM604-stop-returned:0','MEM604-finished'];missing=[x for x in markers if x not in s];pages=s.count('[CEF-BROWSER] console AROS_ENGINE_CYCLE_PASS');retired=s.count('[Chromium:AROS:IsolateRetire] complete');deferred=s.count('[Chromium:AROS:IsolateRetire] deferred')
r={'functional_pass':alive and not fault and not missing and pages==100 and account['all_started_children_returned'],'pid':pid,'native_fault':fault,'timed_out':time.monotonic()>deadline,'missing_markers':missing,'page_passes':pages,'retire_complete':retired,'retire_deferred':deferred,'native_child_accounting':account,'measurements':measure,'scope':'Matched527 GPU hundred-cycle memory validation local-page/host-stop test with fresh private FAT profile and child ledger. Native ledger extraction and long-run memory interpretation remain separate.'}
(E/'runtime604-lifecycle-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)

s=socket.socket(socket.AF_UNIX);s.connect(str(D/'qmp.sock'));f=s.makefile('rwb',buffering=0);f.readline()
for cmd,args in [('qmp_capabilities',{}),('screendump',{'filename':str(D/'lifecycle-final.ppm')})]:
 f.write((json.dumps({'execute':cmd,'arguments':args})+'\n').encode())
 while True:
  reply=json.loads(f.readline())
  if 'return' in reply or 'error' in reply:break
 assert 'error' not in reply,reply
Image.open(D/'lifecycle-final.ppm').save(E/'runtime604-lifecycle-final.png')
