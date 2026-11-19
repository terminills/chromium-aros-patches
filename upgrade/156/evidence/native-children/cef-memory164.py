from pathlib import Path
import subprocess,shutil,json,hashlib,time,re,os
from native_child_accounting import account_children
E=Path(__file__).parent;R=Path('/mnt/short-term/job0254-01a1e62b');S=R/'runtime/native-stage';tools=R/'aros-master-build/bin/linux-x86_64/tools'
assert json.loads((E/'cef-profiles159-result.json').read_text())['functional_pass']
assert not (E/'cef-memory164-inputs.json').exists()
assert hashlib.sha256((S/'Libs/cef-blink.library').read_bytes()).hexdigest()==json.loads((E/'native-directory158-x64-link-result.json').read_text())['engine_sha256']
for src,dst in [('CEFMemorySample-x64','C/CEFMemorySample'),('cef-engine-cycle-url.txt','CEF-cycle-url.txt'),('cef-memory164-startup','S/Job0254-Probes'),('cef-memory164-host-startup','S/CEFHost-Run')]:shutil.copy2(E/src,S/dst)
files={n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in ['Libs/cef-blink.library','Libs/cef.library','Libs/v8.library','C/CEFHost','C/CEFHostBrowser','C/CEFSubprocess','C/CEFMemorySample','CEF-cycle-url.txt','S/Job0254-Probes','S/CEFHost-Run']}
(E/'cef-memory164-inputs.json').write_text(json.dumps({'files':files,'startup':(S/'S/Job0254-Probes').read_text(),'scope':'Ten sequential local-page browser lifecycles in one resident host; same A/primary profile on private FAT; no network fixture. Whole guest memory, not engine-only allocation.'},indent=2)+'\n')
iso=E/'native-probes164.iso';assert not iso.exists()
with (E/'cef-memory164-iso.log').open('x') as f:subprocess.run([str(tools/'grub-mkrescue'),'-d',str(tools/'lib/grub/i386-pc'),'-o',str(iso),str(S)],stdout=f,stderr=subprocess.STDOUT,check=True)
(R/'runtime/native-probes164.iso').symlink_to(iso)
root='/run/media/terminills/Dev_Stuff/job0254-01a1e62b/qemu-x64';env=dict(os.environ,JOB0254_QEMU_X64=root+'/usr/bin/qemu-system-x86_64',QEMU_MODULE_DIR=root+'/usr/lib/x86_64-linux-gnu/qemu')
subprocess.run(['python3',str(E/'boot-native-profile-disk.py'),'164'],env=env,check=True)
p=R/'runtime/serial-probes164.log';pid=int((R/'runtime/qemu.pid').read_text());deadline=time.monotonic()+1200;captured=False;terminal_since=None
while True:
 text=p.read_text(errors='replace') if p.exists() else ''
 alive=Path(f'/proc/{pid}').exists();fatal='[Chromium:FATAL]' in text;alert='[UserAlert] Program failed' in text or 'Software Failure!' in text
 if 'AROS_ENGINE_CYCLE_PASS' in text and not captured and alive:
  subprocess.run(['python3',str(E/'capture-native-desktop.py'),'cef-memory164-first-cycle'],check=True);captured=True
 account=account_children(text)
 terminal='MEM164-finished' in text
 if terminal and terminal_since is None:terminal_since=time.monotonic()
 if not alive or fatal or alert or time.monotonic()>=deadline or (terminal and (account['all_started_children_returned'] or time.monotonic()-terminal_since>30)):break
 time.sleep(2)
(E/'cef-memory164-serial.log').write_text(text)
measurements=[]
for phase,total,free,used,largest in re.findall(r'\[CEF-CYCLE-MEM\] phase=(\S+) total=([0-9a-fA-F]+) free=([0-9a-fA-F]+) used=([0-9a-fA-F]+) largest=([0-9a-fA-F]+)',text):
 values={k:int(v,16) for k,v in [('total',total),('free',free),('used',used),('largest',largest)]};measurements.append({'phase':phase,'whole_guest_bytes':values,'whole_guest_mib':{k:round(v/1048576,2) for k,v in values.items()}})
markers=[f'MEM164-cycle-{n}-returned:0' for n in range(1,11)]+['MEM164-host-returned:0','MEM164-stop-returned:0','MEM164-finished']
console_count=text.count('[CEF-BROWSER] console ARROS_ENGINE_CYCLE_PASS'.replace('ARROS','AROS'))
expected_phases={'before-host','host-ready','host-exited'}|{f'cycle-{n:02d}' for n in range(1,11)}
passed=alive and not fatal and not alert and account['all_started_children_returned'] and all(m in text for m in markers) and console_count==10 and {m['phase'] for m in measurements}==expected_phases
result={'functional_pass':passed,'host_emulator_alive':alive,'fatal':fatal,'native_alert':alert,'timed_out':time.monotonic()>=deadline,'missing_markers':[m for m in markers if m not in text],'console_pass_count':console_count,'native_child_accounting':account,'measurements':measurements,'limits':'Whole guest physical memory at sampled points; includes OS, resident image and caches. Not peak RAM, engine-only RAM or per-app copied engine size. Inspect post-warmup trend before attributing retention.'}
(E/'cef-memory164-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
