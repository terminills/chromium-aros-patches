from pathlib import Path
import json,hashlib,subprocess,re,time,socket
E=Path(__file__).parent;D=Path('/run/media/terminills/Dev_Stuff/job0254-01a1e62b/compact234-memory-vm')
while not (E/'compact234-result.json').exists():time.sleep(5)
r=json.loads((E/'compact234-result.json').read_text());pid=int((D/'qemu.pid').read_text());assert pid==r['pid'];cmd=Path('/proc/'+str(pid)+'/cmdline').read_bytes();assert b'job0254-compact234-memory' in cmd and b'/tmp/job0254-compact234/compact234.iso' in cmd
subprocess.run(['python3',str(E/'capture-compact234.py'),'compact234-final'],check=True)
s=socket.socket(socket.AF_UNIX);s.settimeout(15);s.connect(str(D/'qmp.sock'));f=s.makefile('rwb');f.readline();records=[]
for command in ['qmp_capabilities','quit']:
 f.write((json.dumps({'execute':command})+'\n').encode());f.flush()
 while True:
  answer=json.loads(f.readline())
  if 'return' in answer or 'error' in answer:break
 assert 'error' not in answer;records.append({'command':command,'reply':answer})
f.close();s.close()
for _ in range(150):
 if not Path('/proc/'+str(pid)).exists():break
 time.sleep(.1)
assert not Path('/proc/'+str(pid)).exists();(E/'compact234-stop-qmp.json').write_text(json.dumps(records,indent=2)+'\n')
disk=D/'profile-ledger.img';assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(disk)],text=True).strip()=='6bdac9f3-bf42-41f8-9208-3ccb505419e3'
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:c=p.read_bytes()
 except OSError:continue
 if b'qemu-system-' in c:assert str(disk).encode() not in c
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=sha(disk);out=E/'child-ledger234';out.mkdir(exist_ok=False)
subprocess.run(['mcopy','-s','-i',str(disk)+'@@1048576','::/Ledger234',str(out)],check=True);assert sha(disk)==before
pairs={};files={}
for p in out.rglob('*'):
 if not p.is_file():continue
 name=re.fullmatch(r'([1-9]\d*)\.(enter|exit)',p.name,re.I);body=re.fullmatch(r'CEFCHILD1\nid=([1-9]\d*)\ntype=([a-z-]+)\nevent=(enter|exit)\nresult=(-?\d+)\n',p.read_text());assert name and body and name[1]==body[1] and name[2].lower()==body[3]
 key=(body[1],body[3]);assert key not in pairs;pairs[key]=(body[2],int(body[4]));files[str(p.relative_to(out))]=sha(p)
enters={i:t for (i,e),(t,c) in pairs.items() if e=='enter' and c==0};exits={i:t for (i,e),(t,c) in pairs.items() if e=='exit' and c==0};raw=(E/'compact234-serial.log').read_text();observed=set(r['native_child_accounting']['observed_child_ids'])
gates={'all_native_records_zero':all(c==0 for t,c in pairs.values()),'entry_exit_pairs':enters==exits and len(pairs)==len(enters)*2,'all_observed_children_covered':observed<=set(enters),'at_least20_renderers':sum(t=='renderer' for t in enters.values())>=20,'no_ledger_io_failure':'[CEF-LEDGER]' not in raw,'no_native_fault':not r['native_fault'],'terminal_markers':not r['missing_markers'],'ten_pages':r['page_passes']==10,'not_timed_out':not r['timed_out'],'twenty_retirements':r['retire_complete']>=20 and r['retire_deferred']==0}
result={'functional_pass':all(gates.values()),'gates':gates,'children':enters,'files':files,'disk_sha256':before,'disk_read_after_exact_vm_exit':True,'pid_exited':pid,'sqlite_errors':[x for x in raw.splitlines() if 'ERROR:sql/' in x],'scope':'Independent child-owned native DOS entry/exit files after CEF library close. Does not itself qualify memory plateau or profile database behavior.'}
(E/'compact234-ledger-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
