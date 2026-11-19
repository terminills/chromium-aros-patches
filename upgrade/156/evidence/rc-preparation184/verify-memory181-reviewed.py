from pathlib import Path
import hashlib
import json
from native_child_accounting import account_children

E = Path(__file__).parent

def require_acceptance():
    audit = json.loads((E/'cef-memory181-accounting-audit.json').read_text())
    raw = (E/'cef-memory181-serial.log').read_bytes()
    reviewed = (E/'cef-memory181-reviewed-serial.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == audit['raw_sha256']
    assert hashlib.sha256(reviewed).hexdigest() == audit['reviewed_sha256']
    fragment = audit['raw_fragment']
    text = raw.decode()
    assert text.count(fragment) == 1
    diagnostic = fragment[len('[CEF-CHILD-'):fragment.index('EVENT] X 76 gpu-process 0')]
    assert diagnostic == '[110:17529232:1119/190503.697877:INFO:base/threading/platform_thread_posix.cc:153] [Chromium:AROS:TaskCacheExit] cached=12944 metadata=2624\n'
    assert text.replace(fragment, '[CEF-CHILD-EVENT] X 76 gpu-process 0\n'+diagnostic) == reviewed.decode()
    assert account_children(reviewed.decode())['all_started_children_returned']
    r = json.loads((E/'cef-memory181-result.json').read_text())
    assert r['host_emulator_alive'] and not r['fatal'] and not r['native_alert'] and not r['timed_out']
    assert not r['missing_markers'] and r['console_pass_count'] == 10
    assert r['retirement_complete_count'] == 20 and r['retirement_deferred_count'] == 0
    assert {x['phase'] for x in r['measurements']} == {'before-host','host-ready','host-exited'} | {f'cycle-{n:02d}' for n in range(1,11)}
    return r

if __name__ == '__main__':
    require_acceptance()
    print('PASS: exact reviewed interruption and complete native lifecycle accounting')
