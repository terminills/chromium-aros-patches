from pathlib import Path
import struct,json,sys
p=Path(sys.argv[1]);o=Path(sys.argv[2])
with p.open('rb') as f:
 h=f.read(64);assert h[:6]==b'\x7fELF\x02\x01';v=struct.unpack('<16sHHIQQQIHHHHHH',h);offset,size,count=v[6],v[11],v[12]
 f.seek(offset);first=f.read(size);count=count or struct.unpack('<IIQQQQIIQQ',first[:64])[5]
 f.seek(offset);data=f.read(size*count)
 buckets={'allocated_code':0,'allocated_writable':0,'allocated_readonly':0,'allocated_nobits':0,'nonallocated':0};types={};large=[]
 for i in range(count):
  name,typ,flags,addr,off,n,link,info,align,entsize=struct.unpack_from('<IIQQQQIIQQ',data,i*size)
  types[str(typ)]=types.get(str(typ),0)+n
  if flags&2:
   category='allocated_nobits' if typ==8 else 'allocated_code' if flags&4 else 'allocated_writable' if flags&1 else 'allocated_readonly'
  else:category='nonallocated'
  buckets[category]+=n
  if n>=1024*1024:large.append({'section_index':i,'type':typ,'flags':flags,'bytes':n})
 result={'file':str(p),'file_bytes':p.stat().st_size,'elf_type':v[1],'section_count':count,'section_table_bytes':size*count,'section_payload_bytes':buckets,'section_payload_mib':{k:round(v/1048576,2) for k,v in buckets.items()},'section_type_bytes':types,'largest_sections':sorted(large,key=lambda x:x['bytes'],reverse=True)[:12],'scope':'Static ELF section accounting; not resident memory, peak memory, allocation overhead, or measured savings.'}
o.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['elf_type','section_count','section_table_bytes','section_payload_mib']}))
