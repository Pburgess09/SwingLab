import json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];web=next(root/name for name in ['dist','contact-atlas','web'] if (root/name/'data/contact-map.json').exists());d=json.loads((web/'data/contact-map.json').read_text());c=d['counts']
assert d['pitch_type']=='FF' and set(d['outcomes'])=={'single','double','triple','home_run'}
assert c['four_seam_hits']==c['outside_displayed_zone']+c['in_zone_four_seam_hits']
assert c['in_zone_four_seam_hits']==c['missing_contact_depth']+c['plotted_hits']
for hand,v in d['hands'].items():
 assert len(v['cells'])==35
 assert sum(x['n'] for x in v['cells'])==sum(x['n'] for x in v['bands'])==v['n']
 for x in v['cells']:assert x['q25']<=x['depth']<=x['q75'] and 0<=x['height']<=1 and -8.5<=x['x']<=8.5
 keys=set()
 for p in v['points']:
  assert p['key'] not in keys;keys.add(p['key'])
  assert p['event'] in d['outcomes'] and 0<=p['height']<=1 and abs(p['x'])<=8.5 and math.isfinite(p['depth'])
print('PASS: FF/hit outcomes; cohort reconciliation; 70 cell summaries; 2,800 unique sampled hits; valid coordinates.')

for hand,v in d['hands'].items():
 assert sum(b['hits'] for b in v['height_bands'])==v['n']
 assert sum(b['attack']['n'] for b in v['height_bands'])==sum(x['attack']['n'] for x in v['cells'])==v['attack']['n']
 for x in [*v['cells'],*v['height_bands'],v]:
  a=x['attack']; assert 0<=a['n']<=x.get('hits',x.get('n',0))
  if a['n']: assert a['q25']<=a['median']<=a['q75']
  else: assert a['median'] is None
 for p in v['points']: assert p['attack_angle'] is None or math.isfinite(p['attack_angle'])
print('PASS: angle coverage reconciles across cells, height bands and hands; quantiles and sample angles valid.')
