from pathlib import Path
import subprocess,shutil,json,hashlib,urllib.request
r=Path('/mnt/short-term/job0254-01a1e62b');e=Path('/run/media/terminills/Amiwest/job0254-01a1e62b/evidence')
b=r/'aros-master-build';stage=r/'runtime/native-stage';out=b/'bin/pc-x86_64-smp/AROS'
assert (e/'cef-profiles151-result.json').exists()
assert json.loads((e/'cef-profiles151-result.json').read_text())['functional_pass'] or ((e/'cef-profiles151-fragment-audit.json').exists() and json.loads((e/'cef-profiles151-fragment-audit.json').read_text())['functional_pass'])
assert not (e/'cef-profiles152-inputs.json').exists()
served_fixture=urllib.request.urlopen("http://127.0.0.1:40255/profile-persistence.html",timeout=5).read()
assert served_fixture == (e/"cef-network-http/profile-persistence.html").read_bytes(), "fixture server must serve exact candidate bytes"
files={}
for source,target in [('Libs/v8.library','Libs/v8.library'),('Libs/cef-blink.library','Libs/cef-blink.library'),('Libs/cef.library','Libs/cef.library'),('System/CEFHost','C/CEFHost'),('System/CEFSubprocess','C/CEFSubprocess'),('System/CEFHostProbe','C/CEFHostProbe'),('external/aros-web/libs/cef/test_cef_host_browser','C/CEFHostBrowser')]:
 shutil.copy2(out/source,stage/target);files[target]=hashlib.sha256((stage/target).read_bytes()).hexdigest()
shutil.copy2(e/'CEFClockContract-x64', stage/'C/CEFClockContract')
files['C/CEFClockContract'] = hashlib.sha256((stage/'C/CEFClockContract').read_bytes()).hexdigest()
shutil.copy2(e/'CEFOomCallback-x64', stage/'C/CEFOomCallback')
files['C/CEFOomCallback'] = hashlib.sha256((stage/'C/CEFOomCallback').read_bytes()).hexdigest()
shutil.copy2(e/'CEFProfilePathProbe-x64',stage/'C/CEFProfilePathProbe')
files['C/CEFProfilePathProbe']=hashlib.sha256((stage/'C/CEFProfilePathProbe').read_bytes()).hexdigest()
shutil.copy2(e/'CEFRootCanonical134Probe-x64',stage/'C/CEFRootCanonicalProbe')
files['C/CEFRootCanonicalProbe']=hashlib.sha256((stage/'C/CEFRootCanonicalProbe').read_bytes()).hexdigest()
shutil.copy2(e/'CEFWaitFile-x64',stage/'C/CEFWaitFile')
files['C/CEFWaitFile']=hashlib.sha256((stage/'C/CEFWaitFile').read_bytes()).hexdigest()
shutil.copy2(e/'CEFProfileDiskProbe-x64',stage/'C/CEFProfileDiskProbe')
files['C/CEFProfileDiskProbe']=hashlib.sha256((stage/'C/CEFProfileDiskProbe').read_bytes()).hexdigest()
for n in ['L/fat-handler','boot/aros-fs.pkg.xz']:
 files[n]=hashlib.sha256((stage/n).read_bytes()).hexdigest()
 assert files[n]==json.loads((e/'cef-profiles151-inputs.json').read_text())['files'][n]
(stage/'S/CEFHost-Run').write_text('FailAt 21\nStack 1048576\nC:CEFHost CEFSTORE:Profiles --allow-stop --native-children --debug-native\nEcho PROFILE152-host-returned:$RC >DEBUG:\nEcho done >T:CEFHost152.done\n')
files['S/CEFHost-Run']=hashlib.sha256((stage/'S/CEFHost-Run').read_bytes()).hexdigest()
script='FailAt 21\nAssign Developer: SYS:Developer\nMakeDir RAM:CEFProfile\nAssign PROFILE: RAM:CEFProfile\nStack 1048576\nC:CEFProfileDiskProbe\nIf WARN\nEcho PROFILE152-storage-unavailable >DEBUG:\nQuit 20\nEndIf\nAssign AROSTCP: SYS:System/Network/AROSTCP\nRun <NIL: >RAM:AROSTCP-startup.log QUIET AROSTCP:C/AROSTCP\nC:WaitForPort AROSTCP\nRun >RAM:CEF-host.log Execute S:CEFHost-Run\nC:CEFHostProbe wait\nIf WARN\nEcho PROFILE152-host-unavailable >DEBUG:\nQuit 20\nEndIf\nEcho PROFILE152-read-start >DEBUG:\nC:CEFHostBrowser A "http://10.0.2.2:40255/profile-persistence.html?phase=read&token=PROFILE151" 1000 6000 primary\nEcho PROFILE152-read-returned:$RC >DEBUG:\nWait 5\nEcho PROFILE152-other-app-case-start >DEBUG:\nC:CEFHostBrowser a "http://10.0.2.2:40255/profile-persistence.html?phase=empty&token=PROFILE151" 1000 6000 primary\nEcho PROFILE152-other-app-case-returned:$RC >DEBUG:\nWait 5\nEcho PROFILE152-other-profile-case-start >DEBUG:\nC:CEFHostBrowser A "http://10.0.2.2:40255/profile-persistence.html?phase=empty&token=PROFILE151" 1000 6000 Primary\nEcho PROFILE152-other-profile-case-returned:$RC >DEBUG:\nWait 5\nC:CEFHostProbe stop\nEcho PROFILE152-stop-returned:$RC >DEBUG:\nC:CEFWaitFile T:CEFHost152.done\nIf WARN\nEcho PROFILE152-host-exit-timeout >DEBUG:\nQuit 20\nEndIf\nEcho PROFILE152-finished >DEBUG:\nWait 3600\n'
(stage/'S/Job0254-Probes').write_text(script)
assert files['Libs/cef-blink.library']==json.loads((e/'cef-profiles151-inputs.json').read_text())['files']['Libs/cef-blink.library'], 'profile host test must retain exact native151 engine'
source_manifest=json.loads((e/'cef-profiles151-inputs.json').read_text())['source_manifest']
web=e.parent/'aros-web'
web_sources={str(p.relative_to(web)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [web/'tools/CEFHost/CEFHost.c',web/'tools/CEFHost/profile_identity.h',web/'tools/CEFHost/CEFSubprocess.c',web/'libs/cef/test_cef_host_browser.c',web/'libs/cef/test_cef_browser.c',web/'libs/v8/v8findenginesymbol.c',web/'libs/v8/mmakefile.src',web/'build/v8-import-table.py']}
(e/'cef-profiles152-inputs.json').write_text(json.dumps({'files':files,'web_commit':subprocess.check_output(['git','-C',str(web),'rev-parse','HEAD'],text=True).strip(),'startup':script,'source_manifest':source_manifest,'web_source_sha256':web_sources,'fixture_sha256':hashlib.sha256((e/'cef-network-http/profile-persistence.html').read_bytes()).hexdigest()},indent=2))
iso=e/'native-probes152.iso';link=r/'runtime/native-probes152.iso';assert not iso.exists() and not link.exists()
tools=b/'bin/linux-x86_64/tools'
with (e/'cef-profiles152-iso.log').open('w') as f:subprocess.run([str(tools/'grub-mkrescue'),'-d',str(tools/'lib/grub/i386-pc'),'-o',str(iso),str(stage)],stdout=f,stderr=subprocess.STDOUT,check=True)
link.symlink_to(iso)
subprocess.run(['python3',str(e/'boot-native-profile-disk.py'),'152'],check=True)
