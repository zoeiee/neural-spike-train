"""Empirical single-unit figures: event-aligned raster, rates, ISI, PSTH, tuning."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .core import psth,isi,trial_rates

def save(fig,path,name):
    path.mkdir(parents=True,exist_ok=True)
    fig.tight_layout();fig.savefig(path/f'{name}.png',dpi=190,bbox_inches='tight')
    fig.savefig(path/f'{name}.pdf',bbox_inches='tight');plt.close(fig)

def draw(times,conditions,events,raster,groups,out,alignment,bin_width=.05):
    fig,ax=plt.subplots(figsize=(9,5))
    for i,spikes in enumerate(raster):
        ax.vlines(spikes,i+.5,i+1.45,color='#314e65',lw=.55)
    ax.axvline(0,c='#bd5339',lw=1.3)
    ax.set(xlabel=f'Time relative to {alignment} (seconds)',ylabel='Trial index',title='Extracellular unit raster (each row = one trial)')
    save(fig,out,'01_raster')

    intervals=isi(times)
    fig,ax=plt.subplots(figsize=(7,4));ms=intervals*1e3
    ax.hist(ms,bins=np.linspace(0,min(500,max(50,float(np.percentile(ms,99)))),55),color='#456e88')
    ax.set(xlabel='Interspike interval (ms)',ylabel='Interval count',title='Interspike interval distribution (continuous recording)')
    save(fig,out,'02_isi_histogram')

    bins=np.arange(-.5,1.0001,bin_width)
    centers,rate,_=psth(raster,bins)
    fig,ax=plt.subplots(figsize=(8,4))
    ax.bar(centers,rate,width=bin_width,edgecolor='none',color='#506f87')
    ax.axvline(0,color='#b65e47',lw=1.2)
    ax.set(xlabel=f'Time from {alignment} (s)',ylabel='Mean spikes/s per trial',title=f'Peri-event time histogram ({int(bin_width*1000)} ms bins)')
    save(fig,out,'03_psth')

    whole=trial_rates(raster,0,.5)
    fig,ax=plt.subplots(figsize=(6,4))
    ax.hist(whole,bins=min(20,max(5,int(np.sqrt(len(whole))))),color='#5a708c')
    ax.set(xlabel='Trial firing rate in 0–0.5 s (spikes/s)',ylabel='Trials',title='Trialwise response firing-rate distribution')
    save(fig,out,'04_rate_distribution')

    fig,ax=plt.subplots(figsize=(8,4))
    for ix,group in enumerate(groups):
        indices=np.flatnonzero(conditions==group)
        rr=[raster[i] for i in indices]
        center,one,_=psth(rr,bins)
        ax.plot(center,one,label=f'{group} (n={len(rr)})',lw=1.5)
    ax.axvline(0,c='gray',ls='--')
    ax.set(xlabel=f'Time from {alignment} (s)',ylabel='Mean firing rate (spikes/s)',title='PSTH by trial condition')
    ax.legend();save(fig,out,'05_condition_psth')

    fig,ax=plt.subplots(figsize=(6,4))
    vals=[trial_rates([raster[i] for i in np.flatnonzero(conditions==g)],0,.5) for g in groups]
    ax.boxplot(vals,tick_labels=groups,showmeans=True)
    ax.set(ylabel='0–0.5 s response firing rate (spikes/s)',xlabel='Trial condition',title='Condition comparison: trials are the sampling units')
    save(fig,out,'06_condition_comparison')
