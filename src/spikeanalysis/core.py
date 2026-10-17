"""Core neuronal spike time analysis, with trials as experimental units."""
import numpy as np
import pandas as pd


def check_spikes(times):
    """Validate seconds from the same NWB file; sort and detect duplicates."""
    x=np.asarray(times,dtype=float)
    if x.ndim != 1 or not np.isfinite(x).all() or (x < 0).any():
        raise ValueError('Spike times must be finite, nonnegative, 1-D seconds')
    x=np.sort(x)
    if np.any(np.diff(x) <= 0):
        raise ValueError('Repeated spike times; verify spike sorting or NWB parsing')
    return x


def isi(times):
    """Consecutive-spike intervals in seconds, not across concatenated trial segments."""
    return np.diff(check_spikes(times))


def isi_cv(times):
    v=isi(times)
    return float(v.std(ddof=1)/v.mean()) if len(v)>1 and v.mean()>0 else np.nan


def trial_raster(spike_times, event_times, left=-.5, right=1.0):
    """One sorted vector of spike offsets for each independent presentation."""
    times=check_spikes(spike_times)
    events=np.asarray(event_times,dtype=float)
    if events.ndim != 1 or not np.isfinite(events).all() or len(events)==0:
        raise ValueError('Expected nonempty finite trial event times')
    if right <= left:raise ValueError('Invalid event window')
    return [times[np.searchsorted(times,e+left,side='left'):np.searchsorted(times,e+right,side='left')]-e for e in events]


def psth(raster, bins):
    """Average event-aligned spike counts / (number of presentations * bin width)."""
    if not raster: raise ValueError('At least one trial is required')
    bins=np.asarray(bins,dtype=float)
    if np.any(np.diff(bins)<=0) or not np.allclose(np.diff(bins),np.diff(bins)[0]):
        raise ValueError('PSTH bins must be equally spaced and increasing')
    counts=np.array([np.histogram(t,bins=bins)[0] for t in raster],dtype=float)
    rate=counts.mean(axis=0)/np.diff(bins)
    return (bins[:-1]+bins[1:])/2,rate,counts


def trial_rates(raster, left, right):
    if not right>left:raise ValueError('Positive analysis window required')
    return np.array([np.count_nonzero((s>=left)&(s<right))/(right-left) for s in raster],dtype=float)


def rate_diff_ci(a,b,replicates=2000,seed=42):
    """Bootstrap independently across *trials*, never spikes; within one recording session."""
    a=np.asarray(a,float);b=np.asarray(b,float)
    if len(a)<3 or len(b)<3:raise ValueError('At least three trials per condition')
    rng=np.random.default_rng(seed)
    boot=np.empty(replicates)
    for k in range(replicates):
        boot[k]=rng.choice(a,len(a),replace=True).mean()-rng.choice(b,len(b),replace=True).mean()
    return float(a.mean()-b.mean()),np.quantile(boot,[.025,.975])


def infer_alignment(trials):
    """Prefer an explicit task-event column; do NOT rename trial starts stimulus onsets."""
    candidates=['pole_in','pole_in_time','sample_start','sample_start_time',
                'sample_onset','stimulus_onset','stimulus_start_time',
                'cue_start','cue_start_time','go_cue_time']
    for key in candidates:
        if key in trials:
            a=pd.to_numeric(trials[key],errors='coerce')
            if a.notna().sum()>=6:
                return key,a
    if 'start_time' not in trials:
        raise ValueError(f'No recognized alignment time found; columns: {list(trials.columns)}')
    return 'start_time (TRIAL start; not established stimulus onset)',pd.to_numeric(trials['start_time'],errors='coerce')


def trial_groups(trials):
    """Use documented trial type when present; never infer direction from firing."""
    for key in ('trial_type','stimulus_condition','stimulus_name','trial_response'):
        if key in trials:
            series=trials[key].astype(str).str.strip()
            keep=series[series.notna() & (~series.isin(['nan','None','', 'N/A']))]
            counts=keep.value_counts()
            options=counts[counts>=3]
            if len(options)>=2:
                return key,series,options.index[:2].tolist()
    raise ValueError(f'No condition factor with >=3 trials in each of >=2 groups; columns: {list(trials.columns)}')
