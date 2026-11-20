from pathlib import Path
import mmap,struct,json
E=Path(__file__).parent
f=open('/tmp/job0254-compact318/post-host-analysis.elf','rb');m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
ph=struct.unpack_from('<Q',m,32)[0];sz,n=struct.unpack_from('<HH',m,54);segs=[]
for i in range(n):
 t,flags,o,v,p,fs,ms,a=struct.unpack_from('<IIQQQQQQ',m,ph+i*sz)
 if t==1:segs.append((p,p+fs,o))
def read(p,n):
 for lo,hi,o in segs:
  if lo<=p and p+n<=hi:return m[o+p-lo:o+p-lo+n]
 raise ValueError()
rows=json.loads((E/'task318-snapshots.json').read_text())['host-exited'];out=[]
for r in rows:
 if r['name']!='Chromium worker':continue
 data=read(r['upper']-4096,4096);hits={}
 for off in range(0,4096,8):
  p=struct.unpack_from('<Q',data,off)[0]
  try:
   if struct.unpack('<Q',read(p+0x20,8))[0] != r['task']:continue
   ptr,length=struct.unpack('<QQ',read(p+0x48,16))
   if not 3<=length<=80:continue
   name=read(ptr,length).decode('ascii')
   if not all(32<=ord(c)<127 for c in name):continue
   hits[hex(p)]=name
  except (ValueError,UnicodeDecodeError):pass
 out.append(dict(id=r['id'],candidates=hits));print(r['id'],hits)
(E/'task318-thread-name-candidates.json').write_text(json.dumps(out,indent=2))
