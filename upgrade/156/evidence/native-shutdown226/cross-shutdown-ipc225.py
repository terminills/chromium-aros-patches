from pathlib import Path
import subprocess,shlex,json,concurrent.futures,re
E=Path(__file__).parent;D=E/'shutdown-ipc225-draft';S=Path('/mnt/short-term/job0254-01a1e62b/src');m=json.loads((D/'manifest.json').read_text())
def run(lane,out):
 O=S/out;B=D/lane;B.mkdir(exist_ok=True);results=[]
 for rel in m['files']:
  if not rel.endswith('.cc'):continue
  stem=Path(rel).stem
  matches=[]
  for p in (O/'obj/third_party/blink/renderer').rglob('*.ninja'):
   for line in p.read_text().splitlines():
    if line.startswith('build ') and (': cxx ../../'+rel+' ') in line:matches.append(line.split(':')[0][6:])
  assert len(matches)==1,(rel,matches)
  cmd=shlex.split(subprocess.check_output(['ninja','-t','commands',matches[0]],cwd=O).splitlines()[-1].decode());cmd[cmd.index('-c')+1]=str(D/'candidate'/rel);cmd[cmd.index('-o')+1]=str(B/(stem+'.o'));cmd[cmd.index('-MF')+1]=str(B/(stem+'.d'));cmd.insert(1,'-I'+str(D/'candidate'))
  with (B/(stem+'.log')).open('x') as f:r=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT)
  results.append({'file':rel,'exit_code':r.returncode});assert r.returncode==0,results
 (B/'result.json').write_text(json.dumps({'exit_code':0,'objects':results,'scope':'Isolated candidate objects only; source221 unchanged.'},indent=2)+'\n');print(lane,'PASS',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:list(p.map(lambda x:run(*x),[('x64','out/aros-cef156'),('arm','out/aros-cef156-arm64')]))
