from pathlib import Path
import json,struct,hashlib
E=Path(__file__).parent
exec((E/'inspect-buckets601.py').read_text().split('roots={}')[0])
rows=json.loads((E/'runtime588-retained262k602.json').read_text());verified=[]
for row in rows:
 data=read(int(row['address'],16),262144)
 assert hashlib.sha256(data).hexdigest()==row['sha256']
 count=0
 for i in range(8192):
  ptr,lo,hi,length,unused=struct.unpack_from('<QQQII',data,i*32)
  if not ptr:continue
  assert 0<length<=16 and unused==0
  assert ((((lo^hi^length)*0x9e3779b97f4a7c15)&((1<<64)-1))>>(64-13))==i
  count+=1
 verified.append({'address':row['address'],'entries':count})
assert len(verified)==100
result={'scope':'100 live PA slots; every populated entry matches exact SmallStringCache Fibonacci hash, layout, length and padding. Not proof of total guest-memory savings.','allocations':len(rows),'bytes':len(rows)*262144,'distinct_payload_hashes':len(set(r['sha256'] for r in rows)),'verified':verified}
print(json.dumps(result,indent=2))
