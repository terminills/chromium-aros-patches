from pathlib import Path
import subprocess,json,time
r=Path('/mnt/short-term/job0254-01a1e62b')
e=Path('/run/media/terminills/Amiwest/job0254-01a1e62b/evidence')
w=r/'runtime-arm';a=r/'aros-arm64-gcc16-build/bin/raspi-aarch64-smp/AROS'
assert (e/'arm-desktop-inputs.json').is_file()
assert not (w/'qemu.pid').exists(), 'Inspect the existing owned ARM VM before replacing it'
cmd=[str(e.parent/'arm-runtime/qemu-package/matching/usr/bin/qemu-system-aarch64'),'-name','job0254-cef156-arm-desktop','-M','raspi4b','-m','2G','-smp','4','-kernel',str(a/'aros-aarch64-raspi.img'),'-initrd',str(a/'aros-aarch64-bsp.rom'),'-dtb',str(w/'bcm2711-rpi-4-b.dtb'),'-drive','file='+str(e.parent/'arm-runtime/aros-arm-sd.img')+',if=sd,format=raw','-display','none','-serial','file:'+str(w/'serial.log'),'-qmp','unix:'+str(w/'qmp.sock')+',server=on,wait=off','-device','usb-kbd','-device','usb-mouse','-no-reboot']
(e/'arm-desktop-qemu-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
cmd += ['-serial','file:'+str(w/'aux-serial.log'),'-no-shutdown','-daemonize','-pidfile',str(w/'qemu.pid')]
(e/'arm-desktop-qemu-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with (w/'qemu.log').open('w') as f:
 subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
print('ARM QEMU launched; inspect both serial logs and screen for actual boot result')
