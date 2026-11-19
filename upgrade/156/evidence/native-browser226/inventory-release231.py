from pathlib import Path
import hashlib,json,sys,struct
E=Path(__file__).parent
manifest=Path(sys.argv[1]);stage=Path(sys.argv[2]);arch=sys.argv[3];output=Path(sys.argv[4]);assert arch in ['x64','arm'];assert not output.exists()
source=json.loads(manifest.read_text());expected=source['files'];selected=[]
for rel in expected:
 if rel in ['Libs/cef-blink.library','Libs/cef.library','Libs/v8.library','System/Chromium','System/CEFHost','System/CEFHostProbe','System/CEFSubprocess','System/Chromium.info','Applications.info','S/CEFHost-Run'] or rel.startswith('Applications/') or rel.startswith('System/CEF/'):
  selected.append(rel)
required=['Libs/cef-blink.library','Libs/cef.library','Libs/v8.library','System/Chromium','System/CEFHost','System/CEFHostProbe','System/CEFSubprocess','S/CEFHost-Run','Applications/Internet/Chromium/Chromium','Applications/Internet/Chromium/Chromium.info','Applications/Internet/Chromium.info','Applications/Internet.info','Applications.info','System/Chromium.info']
assert set(required)<=set(selected)
files={}
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for rel in sorted(selected):
 p=stage/rel;assert p.is_file() and not p.is_symlink();sha=digest(p);assert sha==expected[rel],rel
 if rel in required[:7]:
  with p.open('rb') as f:header=f.read(20)
  assert header[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',header,18)[0]==({'x64':62,'arm':183}[arch]),rel
 if rel.endswith('.info'):
  with p.open('rb') as f:assert f.read(2)==b'\xe3\x10',rel
 files[rel]={'source':str(p),'bytes':p.stat().st_size,'sha256':sha}
licenses=E/'release-licenses199';lm=json.loads((licenses/'manifest.json').read_text())['files']
for rel in ['CEF-LICENSE.txt','CHROMIUM-LICENSE.txt','V8-LICENSE.txt','CREDITS-'+arch+'.html']:
 p=licenses/rel;assert digest(p)==lm[rel]['sha256'];files['Documentation/Chromium/'+rel]={'source':str(p),'bytes':p.stat().st_size,'sha256':lm[rel]['sha256']}
notices=E/'release-runtime-notices230'
for rel,metadata in json.loads((notices/'manifest.json').read_text())['files'].items():
 p=notices/rel;assert digest(p)==metadata['sha256'];files['Documentation/Chromium/'+rel]={'source':str(p),'bytes':p.stat().st_size,'sha256':metadata['sha256']}
assert not any('EnvArchive' in p or 'Profiles' in p or p.startswith('C/') or p=='S/User-Startup' for p in files)
output.write_text(json.dumps({'architecture':arch,'input_manifest':str(manifest),'files':files,'total_bytes':sum(v['bytes'] for v in files.values()),'scope':'Read-only packaging inventory: exact hashes, ELF architecture, native icon magic and allowlisted installed resources. No user profiles or test startup. Does not qualify native behavior; verbatim runtime notices included; final source-provenance review and RC acceptance remain required.'},indent=2)+'\n');print('Packaging inventory checked:',len(files),'files')
