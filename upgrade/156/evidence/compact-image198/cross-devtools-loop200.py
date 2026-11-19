from pathlib import Path
import subprocess,shlex,json,concurrent.futures
E=Path(__file__).parent;D=E/'devtools-loop200-draft';S=Path('/mnt/short-term/job0254-01a1e62b/src')
rel='third_party/blink/renderer/core/exported/web_dev_tools_agent_impl.cc'
def run(lane,out):
 O=S/out;B=D/lane;B.mkdir(exist_ok=True);target='obj/third_party/blink/renderer/core/exported/exported/web_dev_tools_agent_impl.o';cmd=shlex.split(subprocess.check_output(['ninja','-t','commands',target],cwd=O).splitlines()[-1].decode());cmd[cmd.index('-c')+1]=str(D/'candidate'/rel);cmd[cmd.index('-o')+1]=str(B/'scope.o');cmd[cmd.index('-MF')+1]=str(B/'scope.d');cmd.insert(1,'-I'+str(D/'candidate'))
 with (B/'build.log').open('x') as f:r=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT)
 (B/'result.json').write_text(json.dumps({'exit_code':r.returncode,'scope':'Isolated object compilation only; candidate not applied to shared build source.'})+'\n');print(lane,r.returncode)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:list(p.map(lambda x:run(*x),[('x64','out/aros-cef156'),('arm','out/aros-cef156-arm64')]))
