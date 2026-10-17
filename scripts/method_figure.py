"""Diagram of the implemented method only. Not a result or simulated experiment."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
    fig,ax=plt.subplots(figsize=(9,2.3))
    ax.set_xlim(-.6,1.1);ax.set_ylim(0,1);ax.axis('off')
    for left,right,txt,color in [(-.5,0,'Baseline\n−0.5 to 0 s','#dbe6ee'),(0,.5,'Response\n0 to 0.5 s','#e9d7c9'),(.5,1,'Late response\n0.5 to 1.0 s','#e3e3e3')]:
        ax.axvspan(left,right,ymin=.27,ymax=.8,color=color)
        ax.text((left+right)/2,.52,txt,ha='center',va='center',fontsize=10)
    ax.annotate('Selected NWB trial event',xy=(0,.84),xytext=(0,.97),ha='center',arrowprops={'arrowstyle':'->'})
    ax.text(.5,.04,'Schematic only — all events and spikes must come from the NWB file',ha='center',transform=ax.transAxes,fontsize=10)
    out=ROOT/'results/figures';out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/'methods_analysis_windows.png',dpi=180,bbox_inches='tight')
    fig.savefig(out/'methods_analysis_windows.pdf',bbox_inches='tight');plt.close(fig)
if __name__=='__main__':main()
