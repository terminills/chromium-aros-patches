from pathlib import Path
import socket,json,re,time,collections,sys
E=Path(__file__).parent;D=Path('/run/media/terminills/Dev_Stuff/job0254-01a1e62b/packed232-browser-vm');label=sys.argv[1];assert re.fullmatch('[a-z0-9-]+',label);output=E/('packed232-pa-'+label+'.json');assert not output.exists()
pid=int((D/'qemu.pid').read_text());assert b'job0254-packed232-browser' in Path('/proc/'+str(pid)+'/cmdline').read_bytes()
text=(D/'serial.log').read_text(errors='replace');facades={int(x,16) for x in re.findall(r'facade=([0-9a-f]{16})',text) if int(x,16)};assert len(facades)==1;facade=facades.pop()
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
 image=read(blink-18*8)[0]-0x580;assert image%4096==0
 assert read(blink-5*8)[0]-0x160==image
 head=read(image+0x1f893f38)[0];nodes=[];seen=set();at=head;deadline=time.monotonic()+45
 while at:
  assert at not in seen and len(nodes)<10000 and time.monotonic()<deadline
  seen.add(at);v=read(at,8);assert v[7] in [0,1];assert v[2]>0 and v[6]>=v[2];assert v[5]<=v[1] and v[1]+v[2]<=v[5]+v[6]
  nodes.append({'record':at,'next':v[0],'exposed_base':v[1],'exposed_length':v[2],'protected_base':v[3],'protected_length':v[4],'allocation_base':v[5],'allocation_length':v[6],'exec_owned':bool(v[7])});at=v[0]
 owned=[x for x in nodes if x['exec_owned']];backing=sum(x['allocation_length'] for x in owned);exposed=sum(x['exposed_length'] for x in owned)
 result={'pid':pid,'facade':hex(facade),'blink_library':hex(blink),'image_base':hex(image),'head':hex(head),'records':nodes,'exec_backing_bytes':backing,'exec_exposed_bytes':exposed,'exec_retained_slack_bytes':backing-exposed,'exec_backing_mib':round(backing/1048576,2),'exec_exposed_mib':round(exposed/1048576,2),'exec_retained_slack_mib':round((backing-exposed)/1048576,2),'exposed_size_counts':dict(collections.Counter(x['exposed_length'] for x in owned)),'scope':'Paused-VM read-only snapshot of Chromium PA allocation records in exact compact226 image. Two independent library-vector offsets verify image base. Exec backing/requested exposed spans only; not whole-guest memory, heap liveness or V8 allocator totals. No target memory writes. Registry may be paused during update; pointer uniqueness and span bounds checked.'}
 output.write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k not in ['records','scope','exposed_size_counts']})
finally:
 q({'execute':'cont'});f.close();s.close();(E/('packed232-pa-'+label+'-qmp.json')).write_text(json.dumps(raw,indent=2)+'\n')
