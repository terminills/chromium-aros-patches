from pathlib import Path
import json,hashlib,subprocess,shutil,os
E=Path(__file__).parent;D=Path('/run/media/terminills/Dev_Stuff/job0254-01a1e62b');W=D/'cold313-x64-vm';T=Path('/tmp/job0254-cold313')
# Run only after the observed write/read result and clean browser shutdown.
gate=json.loads((E/'master312-profile-result.json').read_text())
assert gate['write_pass'] and gate['read_pass'] and gate['browser_closed_cleanly']
old=D/'master312-x64-vm';assert not (old/'qmp.sock').exists() or not Path('/proc/'+(old/'qemu.pid').read_text().strip()).exists()
source=old/'profile.img'
# No process may have the source disk open, even if the PID file was removed.
for proc in Path('/proc').glob('[0-9]*'):
 try:
  for fd in (proc/'fd').iterdir():
   try: assert fd.resolve()!=source,(proc,fd)
   except FileNotFoundError: pass
 except (FileNotFoundError,PermissionError): pass
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(D)],text=True).strip()=='6bdac9f3-bf42-41f8-9208-3ccb505419e3'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
base=json.loads((E/'master312-inputs.json').read_text());assert sha(Path(base['iso']))==base['iso_sha256']
W.mkdir(exist_ok=False);T.mkdir(exist_ok=False)
before=sha(source);disk=W/'profile.img';shutil.copyfile(source,disk);assert sha(source)==sha(disk)==before
startup=Path('/tmp/job0254-master312/overlay/S/Job0254-Probes').read_text()
first='If EXISTS CEF312:EnvArchive312\n    Echo ICON312-profile-already-exists >DEBUG:\n    Quit 20\nEndIf\nMakeDir CEF312:EnvArchive312\nIf WARN\n    Echo ICON312-profile-create-failed >DEBUG:\n    Quit 20\nEndIf\n'
assert startup.count(first)==1
replacement='If NOT EXISTS CEF312:EnvArchive312\n    Echo COLD313-existing-profile-missing >DEBUG:\n    Quit 20\nEndIf\nEcho COLD313-existing-profile-reused >DEBUG:\n'
startup=startup.replace(first,replacement)
script=T/'Job0254-Probes';script.write_text(startup)
iso=T/'cold313.iso'
with (E/'cold313-iso.log').open('x') as log:
 subprocess.run(['xorriso','-indev',base['iso'],'-outdev',str(iso),'-boot_image','any','replay','-map',str(script),'/S/Job0254-Probes'],stdout=log,stderr=subprocess.STDOUT,check=True)
args=[v.replace('job0254-master312-browser','job0254-cold313-browser').replace(base['iso'],str(iso)).replace(str(old),str(W)) for v in base['qemu_command']]
manifest={'source':str(source),'source_disk_sha256':before,'cloned_disk':str(disk),'base_iso_sha256':base['iso_sha256'],'iso':str(iso),'iso_sha256':sha(iso),'qemu_command':args,'scope':'Cold VM boot with byte-identical saved profile disk copy and unchanged Chromium binaries. Persistence result requires native read-page inspection.'}
(E/'cold313-inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
subprocess.run(args,env=dict(os.environ,QEMU_MODULE_DIR=str(D/'qemu-x64/usr/lib/x86_64-linux-gnu/qemu')),check=True)
# Preserve the same MASTER312 origin/token, changing only runtime and evidence paths.
for name in ['capture-master312.py','interact-master312.py']:
 text=(E/name).read_text().replace('master312-x64-vm','cold313-x64-vm').replace('master312.iso','cold313.iso').replace("label='master312-'","label='cold313-'")
 (E/name.replace('master312','cold313')).write_text(text)
print('Cold profile VM started; no persistence pass implied.',flush=True)
