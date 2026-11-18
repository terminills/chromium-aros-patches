from pathlib import Path
import shutil,subprocess,json,hashlib
r=Path('/mnt/short-term/job0254-01a1e62b')
e=Path('/run/media/terminills/Amiwest/job0254-01a1e62b/evidence')
a=r/'aros-arm64-gcc16-build/bin/raspi-aarch64-smp/AROS'
w=e.parent/'arm-runtime';stage=w/'stage'
required=['aros-aarch64-raspi.img','aros-aarch64-bsp.rom','System/About','System/Wanderer/Wanderer','Libs/stdcio.library','Libs/posixc.library','boot/raspi-smp/Libs/debug.library','Libs/cef-blink.library','Libs/cef.library','Libs/v8.library','S/Startup-Sequence']
for f in required: assert (a/f).is_file(),f
assert (e/'cef156-arm64-native-module10-elf.json').is_file()
assert not stage.exists()
stage.mkdir()
(stage/"AROS.boot").write_text("aarch64\n")
for name in ['C','Classes','Devs','Fonts','L','Libs','Locale','Prefs','S','Storage','System','Tools','Utilities','WBStartup']:
 if (a/name).is_dir(): shutil.copytree(a/name,stage/name,symlinks=True)
shutil.copy2(a/'boot/raspi-smp/Libs/debug.library',stage/'Libs/debug.library')
# mtools rejects AUX as a DOS reserved name; AROS creates it during boot.
shutil.move(stage/'Devs/DOSDrivers/AUX', stage/'S/AUX-Mountlist')
startup=stage/'S/Startup-Sequence'
startup.write_text('Copy >NIL: S:AUX-Mountlist DEVS:DOSDrivers/AUX\n'+startup.read_text())
for name in ['cef-blink.library','cef.library','v8.library']:
 subprocess.run([str(r/'aros-arm64-gcc16-crosstools/aarch64-aros-strip'),'--strip-debug',str(stage/'Libs'/name)],check=True)
out=r/'src/out/aros-cef156-arm64';res=stage/'Developer/CEF';res.mkdir(parents=True)
for name in ['chrome_100_percent.pak','chrome_200_percent.pak','resources.pak']:
 shutil.copy2(out/name,res/name)
(res/'locales').mkdir();shutil.copy2(out/'locales/en-US.pak',res/'locales/en-US.pak')
shutil.copy2(e/'CEF156Browser-arm64',stage/'C/CEF156Browser-arm64')
shutil.copy2(e/'ARM-MemorySnapshot',stage/'C/ARM-MemorySnapshot')
(stage/'S/User-Startup').write_text('Assign Developer: SYS:Developer\nMakeDir RAM:CEFProfile\nAssign PROFILE: RAM:CEFProfile\nRun >RAM:ARM-screenshot.log Execute S/ARM-Screenshot\n')
(stage/'S/ARM-Screenshot').write_text('Wait 20\nC:ARM-MemorySnapshot idle-desktop\nStack 1048576\nRun >RAM:CEF-browser.log C:CEF156Browser-arm64 RAM:CEF-arm.ppm "data:text/html,%3Cbody%20bgcolor=cyan%3E%3Ch1%3EChromium%20156%20on%20AROS%20AArch64%3C/h1%3E%3C/body%3E" 30000\nRun >NIL: SYS:System/About\nWait 30\nC:ARM-MemorySnapshot browser-about-30s\nType RAM:CEF-browser.log >DEBUG:\nType RAM:ARM-screenshot.log >DEBUG:\nWait 30\nC:ARM-MemorySnapshot browser-about-60s\nWait 30\nC:ARM-MemorySnapshot browser-about-90s\nWait 30\nC:ARM-MemorySnapshot browser-about-120s\nWait 30\nC:ARM-MemorySnapshot browser-about-150s\nWait 30\nC:ARM-MemorySnapshot browser-about-180s\nWait 30\nC:ARM-MemorySnapshot browser-about-210s\nWait 30\nC:ARM-MemorySnapshot browser-about-240s\nWait 30\nC:ARM-MemorySnapshot browser-about-270s\nWait 30\nC:ARM-MemorySnapshot browser-about-300s\nWait 30\nC:ARM-MemorySnapshot browser-about-330s\nWait 30\nC:ARM-MemorySnapshot browser-about-360s\nWait 30\nC:ARM-MemorySnapshot browser-about-390s\nWait 30\nC:ARM-MemorySnapshot browser-about-420s\nWait 30\nC:ARM-MemorySnapshot browser-about-450s\nWait 30\nC:ARM-MemorySnapshot browser-about-480s\nWait 30\nC:ARM-MemorySnapshot browser-about-510s\nWait 30\nC:ARM-MemorySnapshot browser-about-540s\nWait 30\nC:ARM-MemorySnapshot browser-about-570s\nWait 30\nC:ARM-MemorySnapshot browser-about-600s\n')
manifest={f:hashlib.sha256((a/f).read_bytes()).hexdigest() for f in required}
(e/'arm-desktop-inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
for item in sorted(stage.iterdir()):
 subprocess.run(['mcopy','-s','-i',str(w/'aros-arm-sd.img')+'@@1048576',str(item),'::/'],check=True)
print('ARM SD staged; no boot success claim')
