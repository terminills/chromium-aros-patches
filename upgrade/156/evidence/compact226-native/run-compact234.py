from pathlib import Path
import subprocess,json,hashlib,os,time,re,sys
from native_child_accounting import account_children
E=Path(__file__).parent;D=Path('/run/media/terminills/Dev_Stuff/job0254-01a1e62b/compact234-memory-vm');Q=D.parent/'qemu-x64';m=json.loads((E/'compact234-inputs.json').read_text());disk=Path(m['disk']);iso=Path(m['iso'])
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(disk)==m['disk_before_sha256'] and sha(iso)==m['iso_sha256'];assert not (D/'qemu.pid').exists()
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:c=p.read_bytes()
 except OSError:continue
 if b'qemu-system-' in c:assert str(disk).encode() not in c
args=[str(Q/'usr/bin/qemu-system-x86_64'),'-name','job0254-compact234-memory','-machine','pc,accel=kvm','-cpu','host','-m','4096','-smp','1','-cdrom',str(iso),'-drive','file='+str(disk)+',format=raw,if=ide,index=0','-boot','d','-display','none','-vga','std','-serial','file:'+str(D/'serial.log'),'-qmp','unix:'+str(D/'qmp.sock')+',server=on,wait=off','-nic','user,model=pcnet','-pidfile',str(D/'qemu.pid'),'-daemonize']
(E/'compact234-command.json').write_text(json.dumps(args,indent=2)+'\n');subprocess.run(args,env=dict(os.environ,QEMU_MODULE_DIR=str(Q/'usr/lib/x86_64-linux-gnu/qemu')),check=True)
pid=int((D/'qemu.pid').read_text());deadline=time.monotonic()+1800;captured=False;terminal_at=None
while True:
 s=(D/'serial.log').read_text(errors='replace');alive=Path('/proc/'+str(pid)).exists();fault=any(x in s for x in ['[Chromium:FATAL]','[UserAlert] Program failed','Software Failure!']);account=account_children(s)
 if 'AROS_ENGINE_CYCLE_PASS' in s and not captured:
  subprocess.run(['python3',str(E/'capture-compact234.py'),'compact234-first-cycle'],check=True);captured=True
 if 'MEM234-finished' in s and terminal_at is None:terminal_at=time.monotonic()
 if not alive or fault or time.monotonic()>deadline or (terminal_at and (account['all_started_children_returned'] or time.monotonic()-terminal_at>30)):break
 time.sleep(2)
(E/'compact234-serial.log').write_text(s)
measure=[]
for phase,total,free,used,largest in re.findall(r'\[CEF-CYCLE-MEM\] phase=(\S+) total=([0-9a-fA-F]+) free=([0-9a-fA-F]+) used=([0-9a-fA-F]+) largest=([0-9a-fA-F]+)',s):
 v={k:int(x,16) for k,x in [('total',total),('free',free),('used',used),('largest',largest)]};measure.append({'phase':phase,'bytes':v,'mib':{k:round(x/1048576,2) for k,x in v.items()}})
markers=[f'MEM234-cycle-{n}-returned:0' for n in range(1,11)]+['MEM234-host-returned:0','MEM234-stop-returned:0','MEM234-finished'];missing=[x for x in markers if x not in s];pages=s.count('[CEF-BROWSER] console AROS_ENGINE_CYCLE_PASS');retired=s.count('[Chromium:AROS:IsolateRetire] complete');deferred=s.count('[Chromium:AROS:IsolateRetire] deferred')
r={'functional_pass':alive and not fault and not missing and pages==10 and account['all_started_children_returned'],'pid':pid,'native_fault':fault,'timed_out':time.monotonic()>deadline,'missing_markers':missing,'page_passes':pages,'retire_complete':retired,'retire_deferred':deferred,'native_child_accounting':account,'measurements':measure,'scope':'Compact226 ten-cycle local-page/host-stop test with fresh private FAT profile and child ledger. Native ledger extraction and long-run memory interpretation remain separate.'}
(E/'compact234-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
