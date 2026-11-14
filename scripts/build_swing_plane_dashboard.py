"""Export audited analysis outputs to the buildless dashboard. Run after analysis/analyze.py."""
from pathlib import Path
import csv,json,shutil

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'analysis'
BASE=ROOT/'contact-atlas'
def records(name):
    with (A/'output'/name).open() as f:
        rows=list(csv.DictReader(f))
    for row in rows:
        for k,v in row.items():
            if k not in ['stand','band','side','method','metric']:
                row[k]=float(v)
                if k in ['hits','hitters','n','units']:row[k]=int(row[k])
    return rows
audit=json.loads((A/'output/audit.json').read_text())
medians=records('height_summaries.csv')
contrasts=records('within_hitter_results.csv')
assert sum(r['hits'] for r in medians if r['stand']=='All')==audit['complete_angles']
assert all(r['ci_low']<=r['estimate']<=r['ci_high'] for r in contrasts)
assert {(r['stand'],r['band']) for r in medians}=={(s,b) for s in ['All','R','L'] for b in ['Low','Middle','High']}
payload={'title':'Swing plane and attack angle by pitch height','source':'MLB Statcast / Baseball Savant','seasons':[2024,2025],
 'scope':'Regular-season successful four-seam hits, pitch centers in the defined strike zone, both angles available',
 'audit':audit,'medians':medians,'contrasts':contrasts,
 'definitions':{'swing_path_tilt':'Plane of the barrel path over the 40 ms before contact; lower is flatter.',
 'attack_angle':'Vertical direction of the bat sweet spot at impact; positive is upward.'}}
(BASE/'data/swing-plane.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
(BASE/'downloads').mkdir(exist_ok=True)
for name in ['height_summaries.csv','within_hitter_results.csv','audit.json']:
    shutil.copy(A/'output'/name,BASE/'downloads'/name)
shutil.copy(A/'README.md',BASE/'downloads/analysis-notes.md')
print('PASS: complete cohorts, nine median groups, confidence intervals and dashboard exports')
