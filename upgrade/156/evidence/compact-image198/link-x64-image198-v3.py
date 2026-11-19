from pathlib import Path
import subprocess,hashlib,json
E=Path(__file__).parent;D=Path('/run/media/terminills/Dev_Stuff/job0254-01a1e62b/x64-image198/v3');D.mkdir(parents=True,exist_ok=True)
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(D)],text=True).strip()=='6bdac9f3-bf42-41f8-9208-3ccb505419e3'
source=E/'native-custom-element191-x64-full-symbols.elf';expected=json.loads((E/'native-custom-element191-x64-symbols.json').read_text())['sha256']
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
renamed=D/'unwind-input.elf'
subprocess.run(['/mnt/short-term/job0254-01a1e62b/src/third_party/llvm-build/Release+Asserts/bin/llvm-objcopy','--rename-section','.eh_frame=.aros_unwind',str(source),str(renamed)],check=True)
script=D/'image.ld';script.write_text('''SECTIONS {
 . = 0;
 .text : { *(.text .text.* .ltext .ltext.*) }
 .rodata ALIGN(4096) : { *(.rodata .rodata.* .lrodata .lrodata.*) }
 .aros_unwind ALIGN(8) : { *(.aros_unwind) }
 .gcc_except_table ALIGN(8) : { *(.gcc_except_table .gcc_except_table.*) }
 .data ALIGN(4096) : { *(.data .data.* .ldata .ldata.*) *(.malloc_hook .malloc_hook.* .flags_help_cold .protodesc_cold) }
 .bss ALIGN(4096) : { *(.bss .bss.* .lbss .lbss.*) *(COMMON) }
}
''')
output=D/'native-final.elf';assert not output.exists()
cmd=['/mnt/short-term/job0254-01a1e62b/src/third_party/llvm-build/Release+Asserts/bin/ld.lld','-m','elf_x86_64','--emit-relocs','--strip-debug','--no-relax','--threads=8','-e','0','-T',str(script),str(renamed),'-o',str(output),'-Map='+str(D/'native-final.map')]
with (D/'link.log').open('x') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
(E/'x64-image198-v3-link-result.json').write_text(json.dumps({'exit_code':r.returncode,'source':str(source),'source_sha256':expected,'command':cmd,'scope':'Host-only final-link experiment from retained191 ELF; not native qualification, not installed, source191 is known to fail multitab navigation.'},indent=2)+'\n');print('link exit',r.returncode,flush=True)
