#!/usr/bin/env python3
"""Hit-only four-seam pitch-location/contact-depth map. Standard library only."""
from pathlib import Path
import csv,gzip,json,math,collections,statistics,random
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/visualization';OUT.mkdir(parents=True,exist_ok=True)
def num(x):
 try:
  f=float(x);return f if math.isfinite(f) else None
 except (TypeError,ValueError):return None
def q(a,p):
 a=sorted(a);i=(len(a)-1)*p;j=int(i);return round(a[j]+(a[min(j+1,len(a)-1)]-a[j])*(i-j),3) if a else None
hits={'single','double','triple','home_run'};counts=collections.Counter();columns=set();seen=set();groups={h:[] for h in 'RL'};dates=[]
for path in sorted((ROOT/'data/raw/statcast').rglob('*.csv.gz')):
 with gzip.open(path,'rt',encoding='utf-8-sig') as f:
  reader=csv.DictReader(f);columns.update(reader.fieldnames or [])
  for r in reader:
   counts['rows_read']+=1;k=(r.get('game_pk'),r.get('at_bat_number'),r.get('pitch_number'))
   if k in seen:counts['duplicates_removed']+=1;continue
   seen.add(k)
   if r.get('pitch_type')!='FF' or r.get('events') not in hits:continue
   counts['four_seam_hits']+=1
   if r.get('description')!='hit_into_play':counts['excluded_not_in_play']+=1;continue
   x,z,bot,top,depth=[num(r.get(c)) for c in ['plate_x','plate_z','sz_bot','sz_top','intercept_ball_minus_batter_pos_y_inches']];h=r.get('stand')
   if h not in groups or None in (x,z,bot,top) or top<=bot:counts['invalid_location']+=1;continue
   height=(z-bot)/(top-bot)
   if not -17/24<=x<=17/24 or not 0<=height<=1:counts['outside_displayed_zone']+=1;continue
   counts['in_zone_four_seam_hits']+=1
   if depth is None:counts['missing_contact_depth']+=1;continue
   dates.append(r['game_date']);rel=x*12*(-1 if h=='R' else 1) # positive toward hitter / inside
   groups[h].append({'x':round(rel,3),'height':round(height,4),'depth':round(depth,3),'event':r['events'],'batter':r['batter'],'date':r['game_date'],'key':'-'.join(k),'ev':num(r.get('launch_speed')),'angle':num(r.get('launch_angle')),'attack_angle':num(r.get('attack_angle'))})
   counts['plotted_hits']+=1
def angle_stats(rows):
 a=[r['attack_angle'] for r in rows if r['attack_angle'] is not None]
 return {'n':len(a),'median':q(a,.5),'q25':q(a,.25),'q75':q(a,.75)}
result={'source':'MLB Statcast, existing imported 2024–2025 data','pitch_type':'FF','outcomes':sorted(hits),'counts':dict(counts),'contact_columns_available':sorted(c for c in columns if 'intercept' in c or 'batter_pos' in c),'tracked_date_min':min(dates) if dates else None,'tracked_date_max':max(dates) if dates else None,'coordinate_note':'X = batter-relative pitch location at the plate (inches, positive inside). Height = pitch height normalized to the batter strike zone. Depth = contact forward of batter COM (inches). These are a statistical 3D graph, NOT reconstructed physical contact coordinates relative to home plate.','hands':{}}
for h,rows in groups.items():
 cells=[]
 for iy in range(7):
  for ix in range(5):
   a=[r for r in rows if min(4,int((r['x']+8.5)/17*5))==ix and min(6,int(r['height']*7))==iy]
   if not a:continue
   d=[r['depth'] for r in a];cells.append({'ix':ix,'iy':iy,'x':round(-8.5+(ix+.5)*17/5,3),'height':round((iy+.5)/7,4),'n':len(a),'batters':len(set(r['batter'] for r in a)),'depth':q(d,.5),'q25':q(d,.25),'q75':q(d,.75),'attack':angle_stats(a)})
 bands=[]
 for label,lo,hi in [('Outside',-8.5,-8.5/3),('Middle',-8.5/3,8.5/3),('Inside',8.5/3,8.50001)]:
  a=[r['depth'] for r in rows if lo<=r['x']<hi];bands.append({'label':label,'n':len(a),'depth':q(a,.5),'q25':q(a,.25),'q75':q(a,.75)})
 height_bands=[]
 for label,lo,hi in [('Low',0,1/3),('Middle',1/3,2/3),('High',2/3,1.00001)]:
  a=[r for r in rows if lo<=r['height']<hi];height_bands.append({'label':label,'hits':len(a),'attack':angle_stats(a)})
 rng=random.Random(20261030);sample=rng.sample(rows,min(1400,len(rows)))
 result['hands'][h]={'n':len(rows),'batters':len(set(r['batter'] for r in rows)),'cells':cells,'bands':bands,'points':sample,'point_display_limit':1400,'attack':angle_stats(rows),'height_bands':height_bands,'depth_range':[min((r['depth'] for r in rows),default=0),max((r['depth'] for r in rows),default=0)]}
assert counts['in_zone_four_seam_hits']==counts['missing_contact_depth']+counts['plotted_hits']
assert sum(v['n'] for v in result['hands'].values())==counts['plotted_hits']
for v in result['hands'].values():assert sum(c['n'] for c in v['cells'])==v['n']==sum(c['n'] for c in v['bands'])
(OUT/'contact-map.json').write_text(json.dumps(result,separators=(',',':'),allow_nan=False));print(json.dumps({'counts':result['counts'],'columns':result['contact_columns_available'],'hands':{h:{'n':v['n'],'bands':v['bands']} for h,v in result['hands'].items()}},indent=2))
