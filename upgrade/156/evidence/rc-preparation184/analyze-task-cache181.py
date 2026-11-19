"""Summarize native exit observations without calling them reclaimed memory."""
from pathlib import Path
import json
import re
import statistics

E = Path(__file__).parent
result = json.loads((E / 'cef-memory181-result.json').read_text())
import importlib.util
spec=importlib.util.spec_from_file_location('memory181_review',E/'verify-memory181-reviewed.py');review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
review.require_acceptance()
assert result['retirement_exercised']
text = (E / 'cef-memory181-serial.log').read_text()
rows = []
pending = []
observations = []
for number, line in enumerate(text.splitlines(), 1):
    cache = re.search(r'\[Chromium:AROS:TaskCacheExit\] cached=(\d+) metadata=(\d+)\s*$', line)
    if cache:
        item = dict(line=number, cached_bytes=int(cache[1]), metadata_bytes=int(cache[2]))
        pending.append(item)
        observations.append(item)
    sample = re.search(r'\[CEF-CYCLE-MEM\] phase=(\S+) total=([0-9a-fA-F]+) free=([0-9a-fA-F]+) used=([0-9a-fA-F]+) largest=([0-9a-fA-F]+)', line)
    if sample:
        rows.append(dict(phase=sample[1], whole_guest_used_bytes=int(sample[4], 16),
                         exit_observations_since_previous_sample=len(pending),
                         observed_cache_payload_bytes=sum(x['cached_bytes'] for x in pending),
                         observed_cache_metadata_bytes=sum(x['metadata_bytes'] for x in pending)))
        pending = []
cycles = [x['whole_guest_used_bytes'] for x in rows if x['phase'].startswith('cycle-')]
assert len(cycles) == 10
report = dict(functional_pass_after_review=True, retirement_complete_count=result['retirement_complete_count'],
              observations=observations, samples=rows, observations_after_last_sample=pending,
              total_observed_cached_bytes=sum(x['cached_bytes'] for x in observations),
              total_observed_metadata_bytes=sum(x['metadata_bytes'] for x in observations),
              cache_exit_markers=text.count('[Chromium:AROS:TaskCacheExit]'),
              complete_cache_exit_records=len(observations),
              mean_cycle_growth_mib=(cycles[-1]-cycles[0])/9/1048576,
              median_cycle_growth_mib=statistics.median(b-a for a,b in zip(cycles,cycles[1:]))/1048576,
              limits='Cache bytes observed immediately before native worker exit, not proof of leaked or reclaimed bytes. Whole guest samples include resident engine, OS and caches; not peak or per-app engine size. Main DOS task caches are not instrumented. Interleaved or partial cache records are excluded and marker count is reported separately.')
(E / 'cef-memory181-cache-analysis.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('observations','samples')}, indent=2))
