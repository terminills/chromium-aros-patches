from pathlib import Path
import hashlib,json,os,shutil,socket,subprocess,time
E=Path(__file__).parent;D=Path('/run/media/terminills/Dev_Stuff/job0254-01a1e62b/packed198-load-vm');S=D/'stage';R=Path('/mnt/short-term/job0254-01a1e62b');Q=Path('/run/media/terminills/Dev_Stuff/job0254-01a1e62b/qemu-x64')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(D)],text=True).strip()=='6bdac9f3-bf42-41f8-9208-3ccb505419e3'
assert not (D/'qemu.pid').exists()
assert sha(S/'Libs/cef-blink.library')==json.loads((E/'native-custom-element191-x64-symbols.json').read_text())['runtime_engine_sha256']
packed=Path('/run/media/terminills/Dev_Stuff/job0254-01a1e62b/x64-image198/v3/cef-blink.library');m=json.loads((E/'x64-image198-v3-manifest.json').read_text());assert sha(packed)==m['files'][str(packed)]['sha256']
shutil.copy2(packed,S/'Libs/cef-blink.library');shutil.copy2(E/'CEFImage198Load',S/'C/CEFImage198Load')
(S/'S/User-Startup').write_text('Run >NIL: Execute S:Packed198-Load\n');(S/'S/Packed198-Load').write_text('FailAt 21\nStack 1048576\nC:CEFMemorySample packed198-before-load\nC:CEFImage198Load\nEcho PACKED198-load-returned:$RC >DEBUG:\nC:CEFMemorySample packed198-after-close\nEcho PACKED198-finished >DEBUG:\n')
for p in (S/'Devs/DOSDrivers').glob('*'):
 if p.name.lower().startswith('cefstore'):
  dest=D/'unused-mounts';dest.mkdir(exist_ok=True);p.rename(dest/p.name)
files=['Libs/cef-blink.library','Libs/v8.library','Libs/cef.library','C/CEFImage198Load','C/CEFMemorySample','S/User-Startup','S/Packed198-Load','boot/grub/grub.cfg']
(E/'packed198-native-inputs.json').write_text(json.dumps({'files':{p:sha(S/p) for p in files},'scope':'Diskless native cold-load test of packed191; no browser or memory plateau qualification; separate VM and no profile disk.'},indent=2)+'\n')
iso=D/'packed198.iso';assert not iso.exists();T=R/'aros-master-build/bin/linux-x86_64/tools'
with (E/'packed198-iso.log').open('x') as f:subprocess.run([str(T/'grub-mkrescue'),'-d',str(T/'lib/grub/i386-pc'),'-o',str(iso),str(S)],stdout=f,stderr=subprocess.STDOUT,check=True)
args=[str(Q/'usr/bin/qemu-system-x86_64'),'-name','job0254-packed198-load-only','-machine','pc,accel=kvm','-cpu','host','-m','4096','-smp','1','-cdrom',str(iso),'-boot','d','-display','none','-vga','std','-serial','file:'+str(D/'serial.log'),'-qmp','unix:'+str(D/'qmp.sock')+',server=on,wait=off','-nic','none','-pidfile',str(D/'qemu.pid'),'-daemonize']
subprocess.run(args,env=dict(os.environ,QEMU_MODULE_DIR=str(Q/'usr/lib/x86_64-linux-gnu/qemu')),check=True);print('packed198 independent diskless VM started',flush=True)
deadline=time.monotonic()+900
while True:
 text=(D/'serial.log').read_text(errors='replace');fatal='Software Failure!' in text or '[UserAlert] Program failed' in text or '[Chromium:FATAL]' in text
 if 'PACKED198-finished' in text or fatal or time.monotonic()>=deadline:break
 time.sleep(2)
(E/'packed198-native-serial.log').write_text(text);result={'functional_pass':'PACKED198-load-returned:0' in text and '[CEF-LOAD] sequential-open PASS' in text and not fatal,'fatal':fatal,'timed_out':time.monotonic()>=deadline,'scope':'Native AROS cold-load only. No browser or exception handling qualification.'};(E/'packed198-native-result.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
