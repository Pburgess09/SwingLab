'use strict';
(() => {
  const el=id=>document.getElementById(id);
  const f=(x,signed=false)=>(signed&&x>0?'+':'')+x.toFixed(1)+'°';
  let dataset,side='All';
  const names={All:'All hitters',R:'Right-handed hitters',L:'Left-handed hitters'};
  function graph(rows,metric,label,color){
    const bands=['Low','Middle','High'],vals=bands.map(b=>rows.find(r=>r.band===b)[metric]);
    const xs=[70,210,350],y=v=>205-v/45*170;
    return `<svg viewBox="0 0 420 250" role="img" aria-label="${names[side]}: ${label}. ${bands.map((b,i)=>`${b}: ${f(vals[i])}`).join('; ')}"><title>${label} by pitch height</title>${[0,15,30,45].map(v=>`<line x1="45" x2="390" y1="${y(v)}" y2="${y(v)}" stroke="#dbe5f0"/><text x="35" y="${y(v)+4}" text-anchor="end">${v}°</text>`).join('')}<polyline points="${vals.map((v,i)=>`${xs[i]},${y(v)}`).join(' ')}" fill="none" stroke="${color}" stroke-width="3"/>${vals.map((v,i)=>`<circle cx="${xs[i]}" cy="${y(v)}" r="5" fill="${color}"/><text x="${xs[i]}" y="${y(v)-14}" text-anchor="middle" class="value">${f(v,true)}</text><text x="${xs[i]}" y="235" text-anchor="middle">${bands[i]} pitch</text>`).join('')}</svg>`;
  }
  function render(){
    const d=dataset,rows=d.medians.filter(r=>side==='All'||r.stand===side);
    const medSide=side,medRows=d.medians.filter(r=>r.stand===medSide);
    const effects=d.contrasts.filter(r=>r.side===side&&r.method==='fixed_effects');
    const tilt=effects.find(r=>r.metric==='swing_path_tilt'),attack=effects.find(r=>r.metric==='attack_angle');
    el('analysisFinding').textContent=`${names[side]}: a ${Math.abs(tilt.estimate).toFixed(1)}° flatter swing plane on high pitches, with a ${attack.estimate.toFixed(1)}° more upward attack angle at impact.`;
    el('tiltEffect').textContent=f(tilt.estimate);el('attackEffect').textContent=f(attack.estimate,true);
    el('tiltCI').textContent=`95% CI ${f(tilt.ci_low)} to ${f(tilt.ci_high)} · high minus low`;
    el('attackCI').textContent=`95% CI ${f(attack.ci_low,true)} to ${f(attack.ci_high,true)} · high minus low`;
    el('analysisModelScope').textContent=`Within-hitter comparison: ${tilt.n.toLocaleString()} hits · ${tilt.hitters} hitters. Adjusted for horizontal location, pitch velocity and pitcher handedness; separate baselines for each hitter, season and batting side. Confidence intervals account for repeated hits by the same hitter.`;
    el('medianScope').textContent=`Observed medians · ${names[medSide]}. `;
    el('tiltChart').innerHTML=graph(medRows,'tilt_median','Swing-path tilt','#1765c1');
    el('attackChart').innerHTML=graph(medRows,'attack_median','Attack angle at impact','#167f88');
    el('analysisRows').innerHTML=medRows.map(r=>`<tr><th scope="row">${r.band}</th><td>${r.hits.toLocaleString()}</td><td>${f(r.tilt_median)}</td><td>${f(r.attack_median,true)}</td></tr>`).join('');
    document.querySelectorAll('[data-analysis-side]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.analysisSide===side)));
    el('analysisStatus').textContent='';
  }
  document.querySelectorAll('[data-analysis-side]').forEach(b=>b.addEventListener('click',()=>{side=b.dataset.analysisSide;if(dataset)render();}));
  fetch('data/swing-plane.json').then(r=>{if(!r.ok)throw Error('Unavailable');return r.json();}).then(d=>{dataset=d;el('analysisCoverage').textContent=`${d.audit.complete_angles.toLocaleString()} hits with both angles · ${d.audit.batters} hitters · 2024–2025 regular seasons. ${d.audit.missing_in_zone.swing_path_tilt.toLocaleString()} in-zone hits excluded for missing angle measurements. Successful four-seam hits only.`;render();}).catch(()=>{el('analysisStatus').textContent='Analysis data could not load. Refresh to retry, or open the downloadable results below.';});
})();
