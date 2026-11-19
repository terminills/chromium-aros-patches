from pathlib import Path
from collections import Counter
import time,json,re,subprocess
E=Path(__file__).parent;log=Path('/mnt/short-term/job0254-01a1e62b/runtime/serial-probes152.log');deadline=time.monotonic()+900;captures=set()
runtime_pid=int(Path('/mnt/short-term/job0254-01a1e62b/runtime/qemu.pid').read_text())
host_exited=False
terminal_since=None
while True:
 host_exited=not Path(f'/proc/{runtime_pid}').exists()
 text=log.read_text(errors='replace') if log.exists() else ''
 if not host_exited and 'AROS_PROFILE_READ_FAIL' in text and 'READ_FAIL' not in captures:
  subprocess.run(['python3',str(E/'capture-native-desktop.py'),'cef-profiles152-read-failure'],check=True);captures.add('READ_FAIL')
 for phase in ('WRITE','READ','EMPTY'):
  if not host_exited and 'AROS_PROFILE_'+phase+'_PASS token=PROFILE151' in text and phase not in captures:
   subprocess.run(['python3',str(E/'capture-native-desktop.py'),'cef-profiles152-'+phase.lower()],check=True);captures.add(phase)
 enters=re.findall(r'\[CEF-CHILD-EVENT\] E (\d+) ([a-z-]+)',text)
 exits=re.findall(r'\[CEF-CHILD-EVENT\] X (\d+) ([a-z-]+) (-?\d+)',text)
 observed_child_ids=set(re.findall(r'\[CEF-CHILD-DETAIL\][^\n]*\bid=(\d+)',text)) | set(re.findall(r'spawned pid=(\d+)',text))
 em=dict(enters);xm={i:t for i,t,c in exits if int(c)==0}
 children=bool(observed_child_ids) and set(em)==observed_child_ids and bool(enters) and len(enters)==len(em) and len(exits)==len(xm) and em==xm and all(int(c)==0 for _,_,c in exits)
 markers=['AROS_PROFILE_READ_PASS token=PROFILE151','PROFILE152-read-returned:0','PROFILE152-other-app-case-returned:0','PROFILE152-other-profile-case-returned:0','PROFILE152-stop-returned:0','PROFILE152-host-returned:0','[CEF-HOST] shutdown returned','PROFILE152-finished','[CEF-PROFILE-DISK] write-read PASS']
 empty_count=text.count('[CEF-BROWSER] console AROS_PROFILE_EMPTY_PASS token=PROFILE151')
 profile_fail=bool(re.search(r'AROS_PROFILE_(WRITE|READ|EMPTY)_FAIL|PROFILE152-(?:storage-unavailable|host-unavailable|host-exit-timeout)',text))
 storage_db_failure='[Chromium:AROS:DomStorage] SQLite operation failed' in text
 fatal='[Chromium:FATAL]' in text;alert=any(x in text for x in ['[UserAlert] Program failed','Software Failure!'])
 cache_fallback='Defaulting to in-memory storage' in text
 functional=not storage_db_failure and not cache_fallback and empty_count==2 and children and all(x in text for x in markers) and not profile_fail and not fatal and not alert
 terminal='PROFILE152-finished' in text and '[CEF-HOST] shutdown returned' in text
 if terminal and terminal_since is None:terminal_since=time.monotonic()
 terminal_expired=terminal_since is not None and time.monotonic()-terminal_since>=30
 if host_exited or profile_fail or functional or terminal_expired or fatal or alert or time.monotonic()>=deadline:break
 time.sleep(2)
(E/'cef-profiles152-serial.log').write_text(text)
if not host_exited:
 subprocess.run(['python3',str(E/'capture-native-desktop.py'),'cef-profiles152-final'],check=True)
result={'functional_pass':functional and not host_exited,'host_emulator_exited':host_exited,'profile_failure':profile_fail,'storage_db_failure':storage_db_failure,'cache_fallback':cache_fallback,'fatal':fatal,'native_alert':alert,'timed_out':time.monotonic()>=deadline,'empty_profile_pass_count':empty_count,'missing_markers':[x for x in markers if x not in text],'observed_child_ids':sorted(observed_child_ids),'child_entries':enters,'child_exits':exits,'all_started_children_returned':children,'captures':sorted(captures),'scope':'x64 QEMU clean OS boot reads synthetic cookie/localStorage written by native151 to a private FAT disk, with case-distinct app/profile EMPTY checks; not credentials or hardware qualification.'}
(E/'cef-profiles152-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
