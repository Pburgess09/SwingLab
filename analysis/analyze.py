"""Reproduce descriptive and within-hitter comparisons from downloaded Statcast CSVs.
Run: python analyze.py. Requires numpy, pandas, scipy, matplotlib.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
df=pd.concat([pd.read_csv(p,encoding='utf-8-sig',low_memory=False) for p in sorted(list((ROOT/'raw').glob('*.csv'))+list((ROOT/'raw').glob('*.csv.gz')))],ignore_index=True)
audit={'downloaded_rows':len(df),'downloaded_dates':[str(df.game_date.min()),str(df.game_date.max())]}
keys=['game_pk','at_bat_number','pitch_number']
audit['duplicates']=int(df.duplicated(keys).sum())
df=df.drop_duplicates(keys)
assert df.pitch_type.eq('FF').all()
assert df.events.isin(['single','double','triple','home_run']).all()
assert df.game_type.eq('R').all()
assert df.game_year.isin([2024,2025]).all()
audit['missing_all_hits']={c:int(df[c].isna().sum()) for c in ['attack_angle','swing_path_tilt','plate_x','plate_z','sz_bot','sz_top']}
df['height']=(df.plate_z-df.sz_bot)/(df.sz_top-df.sz_bot)
df['inside_inches']=df.plate_x*12*np.where(df.stand.eq('R'),-1,1)
eligible=df.description.eq('hit_into_play')&df.stand.isin(['R','L'])&df.sz_top.gt(df.sz_bot)&df.height.between(0,1)&df.plate_x.between(-17/24,17/24)
df=df.loc[eligible].copy()
audit['in_zone_hits']=len(df)
audit['missing_in_zone']={c:int(df[c].isna().sum()) for c in ['attack_angle','swing_path_tilt','intercept_ball_minus_batter_pos_y_inches']}
df=df.dropna(subset=['attack_angle','swing_path_tilt']).copy()
audit['complete_angles']=len(df)
audit['batters']=int(df.batter.nunique())
audit['by_year']=df.groupby('game_year').size().to_dict()
audit['by_side']=df.groupby('stand').size().to_dict()
audit['ranges']={c:[float(df[c].min()),float(df[c].max())] for c in ['attack_angle','swing_path_tilt']}
assert df.attack_angle.between(-90,90).all()
assert df.swing_path_tilt.between(0,90).all()
df['band']=pd.cut(df.height,[-1e-9,1/3,2/3,1.000001],labels=['Low','Middle','High'],right=False)
df['width_band']=pd.cut(df.inside_inches,[-8.500001,-8.5/3,8.5/3,8.500001],labels=['Outside','Middle','Inside'],right=False)
df['unit']=df.batter.astype(str)+'_'+df.game_year.astype(str)+'_'+df.stand
df.to_csv(OUT/'eligible_hits.csv.gz',index=False,compression='gzip')
summary=df.groupby(['stand','band'],observed=True).agg(hits=('batter','size'),hitters=('batter','nunique'),tilt_median=('swing_path_tilt','median'),tilt_mean=('swing_path_tilt','mean'),attack_median=('attack_angle','median'),attack_mean=('attack_angle','mean'))
pooled=df.groupby('band',observed=True).agg(hits=('batter','size'),hitters=('batter','nunique'),tilt_median=('swing_path_tilt','median'),tilt_mean=('swing_path_tilt','mean'),attack_median=('attack_angle','median'),attack_mean=('attack_angle','mean')).reset_index()
pooled['stand']='All'
summary=pd.concat([summary.reset_index(),pooled],ignore_index=True).set_index(['stand','band'])
summary.to_csv(OUT/'height_summaries.csv')

def fixed_effects(data,outcome,depth=False):
    d=data.dropna(subset=['release_speed','p_throws']+(['intercept_ball_minus_batter_pos_y_inches'] if depth else [])).copy()
    # Only hitter-season-side units with observed height variation inform this contrast.
    keep=d.groupby('unit',observed=True).band.transform('nunique').gt(1)
    d=d.loc[keep].copy()
    X=pd.DataFrame({'high':d.band.eq('High').astype(float),'middle':d.band.eq('Middle').astype(float),'x':d.inside_inches,'x2':d.inside_inches**2,'speed':d.release_speed,'pitcher_left':d.p_throws.eq('L').astype(float)},index=d.index)
    if depth:X['depth']=d.intercept_ball_minus_batter_pos_y_inches
    X=X-X.groupby(d.unit).transform('mean')
    y=d[outcome]-d.groupby('unit')[outcome].transform('mean')
    x=X.to_numpy();y=y.to_numpy();beta=np.linalg.lstsq(x,y,rcond=None)[0];res=y-x@beta
    scores=pd.DataFrame(x*res[:,None]).groupby(d.batter.to_numpy()).sum().to_numpy()
    bread=np.linalg.pinv(x.T@x);G=len(scores);N=len(d);K=np.linalg.matrix_rank(x);U=d.unit.nunique()
    cov=bread@(scores.T@scores)@bread*(G/(G-1))*((N-1)/(N-U-K))
    se=np.sqrt(np.maximum(np.diag(cov),0));crit=t.ppf(.975,G-1)
    return {'method':'fixed_effects_depth_adjusted' if depth else 'fixed_effects','metric':outcome,'estimate':float(beta[0]),'ci_low':float(beta[0]-crit*se[0]),'ci_high':float(beta[0]+crit*se[0]),'n':N,'hitters':G,'units':int(U)}

results=[]
for side in ['All','R','L']:
    d=df if side=='All' else df[df.stand.eq(side)]
    for metric in ['swing_path_tilt','attack_angle']:
        for depth in [False,True]:
            results.append(dict(side=side,**fixed_effects(d,metric,depth)))
        for minimum in [3,5,10]:
            # Compare medians in the same hitter-season-side and horizontal third.
            pairs=d.groupby(['batter','game_year','stand','width_band','band'],observed=True)[metric].agg(['median','size']).reset_index()
            pairs=pairs[pairs['size'].ge(minimum)]
            wide=pairs.pivot(index=['batter','game_year','stand','width_band'],columns='band',values='median')
            if not {'High','Low'}.issubset(wide.columns):continue
            delta=(wide.High-wide.Low).dropna()
            # Equal weight per hitter after averaging all their eligible strata.
            by_batter=delta.groupby(level='batter').mean()
            values=by_batter.to_numpy();rng=np.random.default_rng(20261112)
            boot=np.array([rng.choice(values,len(values),replace=True).mean() for _ in range(5000)])
            results.append({'side':side,'method':f'paired_medians_min{minimum}','metric':metric,'estimate':float(values.mean()),'ci_low':float(np.quantile(boot,.025)),'ci_high':float(np.quantile(boot,.975)),'n':len(delta),'hitters':len(values),'units':len(delta)})
res=pd.DataFrame(results);res.to_csv(OUT/'within_hitter_results.csv',index=False)
(OUT/'audit.json').write_text(json.dumps(audit,indent=2))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,axs=plt.subplots(1,2,figsize=(11,4.5),sharey=True)
for ax,metric,title in zip(axs,['swing_path_tilt','attack_angle'],['Swing-path tilt','Attack angle at impact']):
    r=res[(res.method=='fixed_effects')&(res.metric==metric)].set_index('side').loc[['All','R','L']]
    ys=np.array([2,1,0]);v=r.estimate.to_numpy()
    ax.errorbar(v,ys,xerr=np.vstack([v-r.ci_low.to_numpy(),r.ci_high.to_numpy()-v]),fmt='o',color='#1765a8',capsize=5,ms=7)
    ax.axvline(0,color='#888888',ls='--',lw=1)
    ax.set_title(title,fontweight='bold',pad=14)
    ax.set_yticks(ys,['All hitters','Right-handed','Left-handed'])
    ax.set_xlabel('High minus low pitches (degrees)')
    ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    for y,a,b,c in zip(ys,v,r.ci_low,r.ci_high):ax.annotate(f'{a:+.1f}°', (a,y),xytext=(0,13),textcoords='offset points',ha='center',fontsize=10)
    ax.set_ylim(-.45,2.5)
    ax.set_xlim(-11,4)
fig.suptitle('Does the approach flatten as pitch height rises?',fontsize=17,fontweight='bold',x=.055,ha='left',y=.99)
fig.text(.055,.89,'2024–2025 MLB regular season · successful four-seam hits within the strike zone',fontsize=11,color='#444444')
fig.text(.055,.02,'Within hitter-season-side estimates adjusted for horizontal location, velocity and pitcher handedness.\nBars: 95% confidence intervals clustered by hitter. Associations do not establish cue effectiveness.',fontsize=9,color='#444444')
fig.subplots_adjust(left=.15,right=.97,top=.75,bottom=.25,wspace=.24)
fig.savefig(OUT/'swing_plane_analysis.png',dpi=180,facecolor='white')
print(json.dumps(audit,indent=2));print(summary.to_string());print(res.to_string(index=False))
