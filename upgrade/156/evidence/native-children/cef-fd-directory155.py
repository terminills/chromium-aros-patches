from pathlib import Path
import shutil,subprocess,json,hashlib,time
E=Path(__file__).parent;r=Path('/mnt/short-term/job0254-01a1e62b');s=r/'runtime/native-stage';b=r/'aros-master-build/bin/linux-x86_64/tools'
assert not (E/'cef-fd-directory155-inputs.json').exists()
shutil.copy2(E/'CEFFdDirectoryStress-x64',s/'C/CEFFdDirectoryStress')
script='FailAt 21\nStack 1048576\nC:CEFFdDirectoryStress\nEcho FD155-unserialized-returned:$RC >DEBUG:\nC:CEFFdDirectoryStress serialized\nEcho FD155-serialized-returned:$RC >DEBUG:\nEcho FD155-finished >DEBUG:\nWait 3600\n'
(s/'S/Job0254-Probes').write_text(script)
(E/'cef-fd-directory155-inputs.json').write_text(json.dumps({'startup':script,'files':{n:hashlib.sha256((s/n).read_bytes()).hexdigest() for n in ['C/CEFFdDirectoryStress','Libs/posixc.library','Libs/stdc.library']},'source_sha256':hashlib.sha256((E/'CEFFdDirectoryStress.cc').read_bytes()).hexdigest(),'native_task_sha256':hashlib.sha256((r/'src/base/threading/aros_native_task.cc').read_bytes()).hexdigest()},indent=2)+'\n')
iso=E/'native-probes155.iso';assert not iso.exists()
with (E/'cef-fd-directory155-iso.log').open('x') as f:subprocess.run([str(b/'grub-mkrescue'),'-d',str(b/'lib/grub/i386-pc'),'-o',str(iso),str(s)],stdout=f,stderr=subprocess.STDOUT,check=True)
(r/'runtime/native-probes155.iso').symlink_to(iso)
subprocess.run(['python3',str(E/'boot-native-profile-disk.py'),'155'],check=True)
p=r/'runtime/serial-probes155.log';deadline=time.monotonic()+240
while True:
 text=p.read_text(errors='replace') if p.exists() else ''
 if 'FD155-finished' in text or time.monotonic()>=deadline:break
 time.sleep(2)
(E/'cef-fd-directory155-serial.log').write_text(text)
result={'finished':'FD155-finished' in text,'unserialized_pass':'[CEF-FD-DIRECTORY] serialized=0 completed=4000 errors=0 result=PASS' in text,'serialized_pass':'[CEF-FD-DIRECTORY] serialized=1 completed=4000 errors=0 result=PASS' in text,'timed_out':time.monotonic()>=deadline,'scope':'Native Exec workers share creator CRT descriptor table; RAM directory enumeration concurrent with file creation/readback. Serialized mode gates descriptor-creating open/opendir calls only.'}
(E/'cef-fd-directory155-result.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
