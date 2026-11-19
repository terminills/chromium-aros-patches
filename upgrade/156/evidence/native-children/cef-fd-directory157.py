from pathlib import Path
import shutil,subprocess,json,hashlib,time
E=Path(__file__).parent;r=Path('/mnt/short-term/job0254-01a1e62b');s=r/'runtime/native-stage';b=r/'aros-master-build/bin/linux-x86_64/tools'
assert not (E/'cef-fd-directory157-inputs.json').exists()
shutil.copy2(E/'CEFFdDirectory157Stress-x64',s/'C/CEFFdDirectory157Stress')
script='FailAt 21\nStack 1048576\nC:CEFFdDirectory157Stress fdopendir\nEcho FD157-fdopendir-returned:$RC >DEBUG:\nEcho FD157-finished >DEBUG:\nWait 3600\n'
(s/'S/Job0254-Probes').write_text(script)
(E/'cef-fd-directory157-inputs.json').write_text(json.dumps({'startup':script,'files':{n:hashlib.sha256((s/n).read_bytes()).hexdigest() for n in ['C/CEFFdDirectory157Stress','Libs/posixc.library','Libs/stdc.library']},'source_sha256':hashlib.sha256((E/'CEFFdDirectory157Stress.cc').read_bytes()).hexdigest(),'native_task_sha256':hashlib.sha256((r/'src/base/threading/aros_native_task.cc').read_bytes()).hexdigest()},indent=2)+'\n')
iso=E/'native-probes157.iso';assert not iso.exists()
with (E/'cef-fd-directory157-iso.log').open('x') as f:subprocess.run([str(b/'grub-mkrescue'),'-d',str(b/'lib/grub/i386-pc'),'-o',str(iso),str(s)],stdout=f,stderr=subprocess.STDOUT,check=True)
(r/'runtime/native-probes157.iso').symlink_to(iso)
subprocess.run(['python3',str(E/'boot-native-profile-disk.py'),'157'],check=True)
p=r/'runtime/serial-probes157.log';deadline=time.monotonic()+240
while True:
 text=p.read_text(errors='replace') if p.exists() else ''
 if 'FD157-finished' in text or '[UserAlert] Program failed' in text or time.monotonic()>=deadline:break
 time.sleep(2)
(E/'cef-fd-directory157-serial.log').write_text(text)
result={'finished':'FD157-finished' in text,'unserialized_run':False,'fdopendir_pass':'[CEF-FD-DIRECTORY] fdopendir=1 serialized=0 completed=4000 errors=0 result=PASS' in text,'timed_out':time.monotonic()>=deadline,'scope':'Native Exec workers share creator CRT descriptor table; RAM directory enumeration concurrent with file creation/readback. Directory creation uses open(O_DIRECTORY) plus fdopendir; no extra admission lock.'}
(E/'cef-fd-directory157-result.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
