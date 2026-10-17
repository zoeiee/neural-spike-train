"""Load a real DANDI NWB recording, analyze spikes and repeated task presentations."""
import argparse
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spikeanalysis.core import (check_spikes,isi_cv,trial_raster,psth,trial_rates,rate_diff_ci,infer_alignment,trial_groups)
from spikeanalysis.plots import draw

def extract(path):
    try:from pynwb import NWBHDF5IO
    except ImportError as e:raise SystemExit('Install PyNWB via requirements.txt first') from e
    with NWBHDF5IO(str(path),'r',load_namespaces=True) as io:
        file=io.read()
        if file.trials is None or file.units is None:
            raise ValueError('NWB needs Units and trials data; do not use non-spiking sessions')
        u=file.units.to_dataframe()
        tr=file.trials.to_dataframe()
        if u.empty or tr.empty:raise ValueError('NWB contains empty units/trials')
        if 'spike_times' not in u:raise ValueError(f'No unit spike times: {list(u.columns)}')
        # Eagerly extract arrays before NWB/HDF5 IO closes.
        records=[(str(k),np.asarray(s,float)) for k,s in u['spike_times'].items()]
        quality={str(k):str(u.loc[k,'quality']) for k in u.index} if 'quality' in u else {}
        tr=tr.copy()
    return records,tr,quality

def run(repo:Path,nwb_path:Path):
    rec, trials, quality=extract(nwb_path)
    tab=repo/'results/tables';tab.mkdir(parents=True,exist_ok=True)
    proc=repo/'data/processed';proc.mkdir(parents=True,exist_ok=True)
    figures=repo/'results/figures';figures.mkdir(parents=True,exist_ok=True)
    # Prefer validated QC labels when present, otherwise choose high spike count
    # and state that unit quality could not be independently established.
    selected=[]
    for uid,x in rec:
        try: t=check_spikes(x)
        except ValueError: continue
        q=quality.get(uid,'unavailable').lower()
        if len(t)>=30 and (not quality or q in {'good','excellent','single'}):selected.append((uid,t))
    if not selected:
        raise ValueError('No acceptable units: check quality fields/threshold and spike times')
    uid,times=max(selected,key=lambda z:len(z[1]))
    align,events=infer_alignment(trials)
    gkey,labels,pair=trial_groups(trials)
    usable=events.notna() & labels.isin(pair)
    if 'trial_is_good' in trials:
        usable &= trials['trial_is_good'].astype(str).str.lower().isin(['1','true','yes'])
    if 'trial_response' in trials and gkey!='trial_response':
        # Restrict to task-correct presentations when a corresponding column exists.
        correct=trials['trial_response'].astype(str).str.lower().eq('correct')
        if (usable & correct).sum()>=6:usable &= correct
    intervals=events[usable].to_numpy(float)
    conditions=labels[usable].to_numpy(str)
    if any((conditions==x).sum()<3 for x in pair):
        raise ValueError('Fewer than 3 usable trial onsets per group after filtering')
    # Reject overlapping windows rather than counting same spike as independent in repeated events.
    evsort=np.sort(intervals)
    if len(evsort)>1 and (np.diff(evsort)<1.5).any():
        raise ValueError('Overlapping [-0.5,1] s trial windows; choose nonoverlapping events')
    raster=trial_raster(times,intervals)
    baseline=trial_rates(raster,-.5,0)
    response=trial_rates(raster,0,.5)
    saved=pd.DataFrame({'trial_id':trials.index[usable].astype(str), 'condition':conditions,
                        'alignment_time_s':intervals,'baseline_rate_hz':baseline,'response_rate_hz':response,
                        'response_minus_baseline_hz':response-baseline})
    saved.to_csv(tab/'trial_firing_rates.csv',index=False)
    pd.DataFrame({'time_s':np.arange(-.475,.976,.05),
                  'mean_rate_hz':psth(raster,np.arange(-.5,1.0001,.05))[1]}).to_csv(tab/'psth.csv',index=False)
    keys=list(pair);a=response[conditions==keys[0]];b=response[conditions==keys[1]]
    delta,ci=rate_diff_ci(a,b)
    summary={'dandiset':'000006','asset':nwb_path.name,'selected_unit':uid,
             'unit_selection':'quality={good,excellent,single} if available; >=30 spikes; otherwise most spikes',
             'quality_label':quality.get(uid,'NOT PROVIDED IN NWB'),'total_spikes_selected_unit':len(times),
             'recording_rate_hz':float(len(times)/(times[-1]-times[0])) if len(times)>1 else None,
             'isi_cv':isi_cv(times),'alignment_column':align,'trial_condition_column':gkey,
             'total_trials':len(intervals),'trial_conditions':keys,'trial_counts':{x:int((conditions==x).sum()) for x in keys},
             'response_rate_difference_hz':delta,'response_rate_difference_95pct_trial_bootstrap_CI_hz':ci.tolist(),
             'baseline_window_s':[-.5,0],'response_window_s':[0,.5],
             'warning':'Within-session trial confidence intervals do not generalize across animals.'}
    (tab/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
    draw(times,conditions,intervals,raster,keys,figures,align)
    report=f"""# Trial-aligned neural spike train analysis

## Abstract
Extracellular neural units from DANDI 000006, a mouse anterior lateral motor-cortex delay-response task, were analyzed in a single session. Unit **{uid}** contributed {len(times)} recorded spikes. {len(intervals)} nonoverlapping trial events were aligned to **{align}** and grouped according to **{gkey}**. Post-event responses for {keys[0]} versus {keys[1]} differed by {delta:.3f} spikes/s; trial-bootstrap 95% interval [{ci[0]:.3f}, {ci[1]:.3f}]. This is a descriptive within-session result, not a population claim.

## Introduction and scientific question
How do spike timing, firing rate and trial-averaged activity relate to the task and its trial conditions? Spikes are action-potential events, not artificial network outputs.

## Dataset
One open NWB session from Dandiset 000006, the Economo et al. 2018 mouse anterior lateral motor-cortex experiment (subject anm372795; recording date 2017-07-18). Single-session extracellular sorted units and experimental trial annotations were loaded directly using PyNWB. Session and NWB metadata should be checked before any cross-animal conclusion.

## Methods
Unit QC: available good/excellent/single labels plus at least 30 spikes, or spike-count-based selection when labels are absent (uncertain isolation quality). Interspike intervals are consecutive differences across the recording; CV is sample SD / mean of positive intervals. Event times come from `{align}` (which is explicitly **not** necessarily visual or sensory onset). For each event, spikes were offset into [-0.5, 1.0) s, with 50-ms PSTH bins. Each rate is spike count / time; PSTH is mean spike counts across trials / bin duration. Baseline [-0.5,0) and response [0,0.5) use equal lengths. We selected the first two supported groups from `{gkey}` and bootstrapped the difference of mean response rates by resampling **trials** (2000 replicates, seed 42). Overlapping event windows are disallowed. Data and plots are generated from the NWB event and spike arrays, not simulated activity.

## Results
- Selected unit ID: {uid}; spike count: {len(times)}; recording-average rate: {summary['recording_rate_hz']:.3f} spikes/s (first-to-last-spike denominator, approximate).
- ISI coefficient of variation: {summary['isi_cv']:.3f}.
- Trial count: {len(intervals)}. {keys[0]}: {len(a)} presentations; {keys[1]}: {len(b)} presentations.
- Mean response rate: {keys[0]} {a.mean():.3f} spikes/s; {keys[1]} {b.mean():.3f} spikes/s.
- Mean trial-rate difference ({keys[0]} minus {keys[1]}): {delta:.3f} spikes/s; bootstrap CI [{ci[0]:.3f},{ci[1]:.3f}].
- CSV: `results/tables/trial_firing_rates.csv`, `psth.csv`, and `summary.json`. Raster, ISI histogram, PSTH, firing-rate distribution, condition PSTHs and comparison are in `results/figures/`.

## Discussion
Event-locked spike dynamics and differences between task trials support characterization of response timing/condition association in this selected unit. They cannot isolate stimulus encoding from planned movement, reward expectation or trial selection.

## Limitations
One selected unit, one session and one animal. Trial bootstrap treats trials as resampling units within this session; repeated trials are not biological replicates, so the intervals must not be described as population generalization. Quality metrics may be absent. If alignment uses `start_time`, the figures are **trial-start aligned, not stimulus-onset aligned**. The two condition labels may represent instructed direction or behavior, not orientation tuning; no orientation-selectivity claim is made. Single-session time averages can obscure nonstationarity. The sample rate based on first-to-last spike is approximate.

## Conclusion
The reproducible NWB pipeline quantifies ISIs, event-aligned firing, trial-level variability and descriptive tuning by existing task conditions in actual recorded extracellular spike trains.

## References
1. DANDI 000006: https://dandiarchive.org/dandiset/000006/0.220126.1855
2. Economo MN et al. Distinct descending motor cortex pathways and their roles in movement. Nature (2018). https://doi.org/10.1038/s41586-018-0642-9
3. NWB standard / PyNWB: https://www.nwb.org/ and https://pynwb.readthedocs.io/
"""
    (repo/'reports/research_report.md').write_text(report)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--nwb',type=Path,default=ROOT/'data/raw/sub-anm372795_ses-20170718.nwb')
    a=p.parse_args()
    if not a.nwb.exists():raise SystemExit('NWB is absent: run python scripts/download_data.py first')
    run(ROOT,a.nwb)
