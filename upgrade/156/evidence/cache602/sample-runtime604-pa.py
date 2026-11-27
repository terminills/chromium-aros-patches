from pathlib import Path
import socket,json,re,time,collections,sys,datetime,subprocess,hashlib
E=Path(__file__).parent;D=Path('/home/terminills/job0254-release-staging/runtime604');label=sys.argv[1];assert re.fullmatch('[a-z0-9-]+',label);output=E/('runtime604-pa-'+label+'.json');assert not output.exists()
pid=int((D/'qemu.pid').read_text());assert b'job0254-runtime604-lifecycle' in Path('/proc/'+str(pid)+'/cmdline').read_bytes()
text=(D/'serial.log').read_text(errors='replace');facades={int(x,16) for x in re.findall(r'facade=([0-9a-f]{16})',text) if int(x,16)};assert len(facades)==1;facade=facades.pop()
image_file=Path('/home/terminills/job0254-release-staging/native603/x64-image574/native-final.elf')
link=json.loads((E/'native603-x64-cef-link-result.json').read_text())
with image_file.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==link['symbols_sha256']
nm=subprocess.check_output(['nm','-n','-C','--defined-only',str(image_file)],text=True)
def symbol(name):
 matches=re.findall(r'^([0-9a-f]+) [A-Za-z] '+re.escape(name)+r'$',nm,re.M)
 assert len(matches)==1,(name,matches)
 return int(matches[0],16)
allocator_offset=symbol('CEFBlink_18_CEFBlinkGetAllocator')
version_offset=symbol('CEFBlink_5_CEFBlinkVersionInfo')
records_offset=symbol('partition_alloc::internal::(anonymous namespace)::s_pageAllocations')
arenas_offset=symbol('partition_alloc::internal::(anonymous namespace)::s_superPageArenas')
s=socket.socket(socket.AF_UNIX);s.settimeout(15);s.connect(str(D/'qmp.sock'));f=s.makefile('rwb');f.readline();raw=[]
def q(c):
 f.write((json.dumps(c)+'\n').encode());f.flush()
 while True:
  r=json.loads(f.readline())
  if 'return' in r or 'error' in r:break
 raw.append({'command':c,'reply':r});assert 'error' not in r,r
 return r['return']
def read(address,count=1,unit='g'):
 assert 4096<=address<1<<48 and 0<count<=64
 t=q({'execute':'human-monitor-command','arguments':{'command-line':f'x /{count}{unit}x {address:#x}'}});values=[int(v,16) for v in re.findall(r'0x([0-9a-f]+)',t)];assert len(values)==count,(address,count,t);return values
q({'execute':'qmp_capabilities'});assert q({'execute':'query-status'})['status']=='running';q({'execute':'stop'})
try:
 # Exact installed facade disassembly: vector18 movabs CEFBlinkBase,%rax;
 # mov (%rax),%rdx; jmp *-0x90(%rdx). x64 AROS vectors are pointer-sized.
 wrapper=read(facade-18*8)[0];code=bytes(read(wrapper,19,'b'));assert code[:2]==b'\x48\xb8' and code[10:19]==b'\x48\x8b\x10\xff\xa2\x70\xff\xff\xff',code.hex()
 blink=read(int.from_bytes(code[2:10],'little'))[0]
 image=read(blink-18*8)[0]-allocator_offset;assert image%4096==0
 assert read(blink-5*8)[0]-version_offset==image
 head=read(image+records_offset)[0];nodes=[];seen=set();at=head;deadline=time.monotonic()+45
 while at:
  assert at not in seen and len(nodes)<10000 and time.monotonic()<deadline
  seen.add(at);v=read(at,10);assert v[7] in [0,1];assert v[2]>0 and v[6]>=v[2];assert v[5]<=v[1] and v[1]+v[2]<=v[5]+v[6]
  nodes.append({'record':at,'next':v[0],'exposed_base':v[1],'exposed_length':v[2],'protected_base':v[3],'protected_length':v[4],'allocation_base':v[5],'allocation_length':v[6],'exec_owned':bool(v[7]),'arena':v[8],'arena_slot':v[9]&0xffffffff});at=v[0]
 owned=[x for x in nodes if x['exec_owned']];unique_backings={x['allocation_base']:x['allocation_length'] for x in owned};backing=sum(unique_backings.values());exposed=sum(x['exposed_length'] for x in owned)
 result={'snapshot_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'last_guest_phase_at_sampler_start':re.findall(r'\[CEF-CYCLE-MEM\] phase=(\S+)',text)[-1],'pid':pid,'facade':hex(facade),'blink_library':hex(blink),'image_base':hex(image),'head':hex(head),'records':nodes,'exec_backing_bytes':backing,'exec_exposed_bytes':exposed,'exec_retained_slack_bytes':backing-exposed,'exec_backing_mib':round(backing/1048576,2),'exec_exposed_mib':round(exposed/1048576,2),'exec_retained_slack_mib':round((backing-exposed)/1048576,2),'exposed_size_counts':dict(collections.Counter(x['exposed_length'] for x in owned)),'scope':'Paused-VM read-only snapshot of Chromium PA allocation records in exact native527 image. Two independent library-vector offsets verify image base. Exec backing/requested exposed spans only; not whole-guest memory, heap liveness or V8 allocator totals. No target memory writes. Registry may be paused during update; pointer uniqueness and span bounds checked.'}
 arenas=[];seen_arena=set();at=read(image+arenas_offset)[0]
 while at:
  assert at not in seen_arena and len(arenas)<10000
  seen_arena.add(at);v=read(at,5);mask=v[4]&0xffffffff
  assert 0<mask<16 and v[2]==10*1024*1024 and v[3]%(2*1024*1024)==0
  arena_records=[n for n in nodes if n['arena']==at]
  assert len(arena_records)==mask.bit_count()
  assert sum(1<<n['arena_slot'] for n in arena_records)==mask
  for n in arena_records:
   assert n['allocation_base']==v[1] and n['allocation_length']==v[2]
   assert n['exposed_base']==v[3]+n['arena_slot']*2*1024*1024
  arenas.append({'arena':at,'backing':v[1],'backing_bytes':v[2],'slots_base':v[3],'used_mask':mask})
  at=v[0]
 assert all(not n['arena'] or n['arena'] in seen_arena for n in nodes)
 result['arenas']=arenas;result['unique_backing_count']=len(unique_backings)
 result['symbols_sha256']=link['symbols_sha256'];result['record_layout_bytes']=80
 result['scope']='Paused native603 QEMU PA records and unique arena backing. Shared backing counted once. Exact image symbols and two vectors verified; arena masks reconciled with ownership records. Not guest RSS or heap liveness.'
 result['all_verified_partition_roots']={}
 result['unclassified_superpages']=[]
 for node in nodes:
  if node['exposed_length']!=2097152 or node['exposed_base']%2097152:continue
  try:
   root=read(node['exposed_base']+4096)[0]
   if not (4096<=root<(1<<48)) or read(root+14984)[0]!=(root^((1<<64)-1)):
    result['unclassified_superpages'].append(node['exposed_base']);continue
   key=hex(root)
   if key not in result['all_verified_partition_roots']:
    counters={'superpage_records':0}
    for field,offset in {'committed':6656,'superpages':6672,'direct_mapped':6680,'allocated':6688,'max_allocated':6696}.items():counters[field]=read(root+offset)[0]
    result['all_verified_partition_roots'][key]=counters
   result['all_verified_partition_roots'][key]['superpage_records']+=1
  except AssertionError as error:
   result['unclassified_superpages'].append({'address':node['exposed_base'],'read_error':str(error)})

 result['bucket262144']={}
 for key in result['all_verified_partition_roots']:
  root=int(key,16);bucket=root+376+95*56;v=read(bucket,5)
  assert v[3]==262144
  flags=v[4]&0xffffffff;pages=flags&255;full=flags>>8
  allocated=full*((pages*4096)//262144);seen=set();chains={}
  for name,at in zip(['active','empty','decommitted'],v[:3]):
   entries=[]
   while at:
    data=read(at,4)
    if data[2]==0:break
    assert data[2]==bucket and at not in seen and len(seen)<10000
    seen.add(at);count=data[3]&32767;allocated+=count
    entries.append({'metadata':hex(at),'allocated':count});at=data[1]
   chains[name]=entries
  result['bucket262144'][key]={'full_spans':full,'allocated_slots':allocated,'allocated_bytes':allocated*262144,'chains':chains}
 result['root_layout_evidence']='partition601/layout.s and buckets.s; unchanged PA source/build flags in native603'

 output.write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k not in ['records','scope','exposed_size_counts']})
finally:
 q({'execute':'cont'});f.close();s.close();(E/('runtime604-pa-'+label+'-qmp.json')).write_text(json.dumps(raw,indent=2)+'\n')
