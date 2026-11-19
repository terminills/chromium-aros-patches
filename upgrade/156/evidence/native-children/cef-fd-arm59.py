from pathlib import Path
import subprocess,hashlib,json
E=Path(__file__).parent;B=E.parent;R=Path('/mnt/short-term/job0254-01a1e62b/runtime-arm')
assert not (E/'cef-fd-arm59-inputs.json').exists()
pid=int((R/'qemu.pid').read_text())
subprocess.run(['python3',str(E/'restart-arm-desktop.py'),'desktop57','--hold'],check=True)
assert not Path(f'/proc/{pid}').exists()
image=B/'arm-runtime/aros-arm-sd.img'
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try: cmd=p.read_bytes()
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 if b'qemu-system-' in cmd:assert str(image).encode() not in cmd
probe=E/'CEFFdDirectory159Stress-arm64';header=probe.read_bytes()[:20];assert header[7]==15 and header[16:18]==b'\x01\x00'
startup=E/'cef-fd-arm59-startup';startup.write_text('FailAt 21\nWait 20\nStack 1048576\nC:CEFFdDirectoryStress fdopendir\nEcho ARM59-fd-stress-returned:$RC >DEBUG:\nEcho ARM59-finished >DEBUG:\nWait 3600\n')
files={}
for src,dst in [(probe,'C/CEFFdDirectoryStress'),(startup,'S/ARM-Screenshot')]:
 files[dst]=hashlib.sha256(src.read_bytes()).hexdigest()
 subprocess.run(['mcopy','-o','-i',str(image)+'@@1048576',str(src),'::'+dst],check=True)
 check=E/'arm59-readback.tmp';subprocess.run(['mcopy','-o','-i',str(image)+'@@1048576','::'+dst,str(check)],check=True)
 assert hashlib.sha256(check.read_bytes()).hexdigest()==files[dst];check.unlink()
(E/'cef-fd-arm59-inputs.json').write_text(json.dumps({'files':files,'native_tls_sha256':hashlib.sha256((B/'aros-web/libs/v8/engine/emutls-aros.c').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((E/'CEFFdDirectory157Stress.cc').read_bytes()).hexdigest(),'scope':'Native AROS Exec workers share creator CRT descriptor table. open(O_DIRECTORY)+fdopendir, no extra serialization. No browser executes; same ARM56 OS and SDK.'},indent=2)+'\n')
subprocess.run(['python3',str(E/'boot-arm-desktop.py')],check=True)
