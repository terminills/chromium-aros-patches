#!/usr/bin/env python3
"""Host ownership regression with mocked cppgc handles; not native GC proof.
Usage: python3 run.py /path/to/candidate/chromium/src /path/to/new/output
Requires the candidate header recorded by persistent-singleton172-candidate-status.json.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source',type=Path);p.add_argument('output',type=Path)
a=p.parse_args();here=Path(__file__).resolve().parent
src=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
name=Path('third_party/blink/renderer/platform/wtf/std_lib_extras.h')
header=(src/name).read_bytes()
status=json.loads((here.parent/'persistent-singleton172-candidate-status.json').read_text())
assert hashlib.sha256(header).hexdigest()==status['draft_sha256'], 'candidate header differs'
results={}
for label in ['const-control','candidate']:
    overlay=out/label;hp=overlay/name;hp.parent.mkdir(parents=True)
    content=header.decode()
    if label=='const-control':
        old='IsArosHeapPersistent<std::remove_cv_t<Type>>::value'
        assert content.count(old)==1
        content=content.replace(old,'IsArosHeapPersistent<Type>::value')
    hp.write_text(content)
    binary=overlay/'test'
    cmd=['g++','-std=c++20','-fsanitize=address,undefined','-g','-pthread',
         '-I'+str(here/'stubs'),'-I'+str(overlay),'-I'+str(src),str(here/'test.cc'),'-o',str(binary)]
    with (overlay/'compile.log').open('w') as f:
        subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
    run=subprocess.run([str(binary)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
                       env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
    (overlay/'run.log').write_text(run.stdout)
    results[label]={'returncode':run.returncode,'output':run.stdout}
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
assert results['const-control']['returncode']!=0 and 'FAIL 14' in results['const-control']['output']
assert results['candidate']['returncode']==0 and 'PASS 15' in results['candidate']['output']
print('PASS: const-root control fails at expected assertion; candidate passes 15 host checks')
