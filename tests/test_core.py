"""Unit tests: constructed arrays here are fixtures, NOT reported neuroscience data."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from spikeanalysis.core import check_spikes,isi,isi_cv,trial_raster,psth,trial_rates,rate_diff_ci,infer_alignment,trial_groups

def test_interspike_intervals():
    assert np.allclose(isi([.31,.10,.21]),[.11,.10])
    with pytest.raises(ValueError):check_spikes([.1,.1])
    assert np.isnan(isi_cv([.1,.2]))

def test_psth_correct_hz():
    r=trial_raster([.8,1.1,1.3,1.7,2.1,2.25],[1,2],-.5,.5)
    centers,rate,count=psth(r,np.array([-.5,0,.5]))
    assert np.allclose(count,[[1,2],[1,2]])
    assert np.allclose(rate,[2,4])
    assert np.allclose(trial_rates(r,0,.5),[4,4])

def test_trial_bootstrap_reproducible():
    x,ci=rate_diff_ci([4,4,4],[1,1,1],replicates=100,seed=4)
    assert x==3 and np.allclose(ci,[3,3])

def test_event_column_selection_and_grouping():
    df=pd.DataFrame({'start_time':[10,20,30,40,50,60],'pole_in':[11,21,31,41,51,61],
                     'trial_type':['lick left']*3+['lick right']*3})
    event,onset=infer_alignment(df)
    assert event=='pole_in' and onset.iloc[0]==11
    assert set(trial_groups(df)[2])=={'lick left','lick right'}

def test_dont_call_trial_start_a_stimulus():
    name,_=infer_alignment(pd.DataFrame({'start_time':[1,2,3,4,5,6]}))
    assert 'not established stimulus onset' in name
