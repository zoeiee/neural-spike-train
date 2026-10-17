"""Download exactly one published NWB session, not a whole massive dataset."""
import argparse
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
# Official NWB-for-education example for DANDI 000006, subject anm372795.
# A fixed public content-addressed blob; no credentials required.
URL='https://dandiarchive.s3.amazonaws.com/blobs/43b/f3a/43bf3a81-4a0b-433f-b471-1f10303f9d35'
FILE='sub-anm372795_ses-20170718.nwb'

def download(path,link=URL):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        print('Using existing NWB file:',path);return
    tmp=path.with_suffix('.partial')
    try:
        with urlopen(Request(link,headers={'User-Agent':'NeuralSpikeTrainStudy/1.0'}),timeout=90) as resp, tmp.open('wb') as dest:
            while True:
                block=resp.read(1024*256)
                if not block:break
                dest.write(block)
        if tmp.stat().st_size<20_000:raise RuntimeError('Downloaded NWB unusually small; inspect source URL')
        # NWB is HDF5; magic signature must precede accepting partial download.
        with tmp.open('rb') as fh:
            if fh.read(8)!=b'\x89HDF\r\n\x1a\n':
                raise RuntimeError('Downloaded file is not an HDF5/NWB file')
        tmp.rename(path)
        (path.parent/'provenance.txt').write_text('DANDI: https://dandiarchive.org/dandiset/000006/0.220126.1855\nAsset: sub-anm372795/sub-anm372795_ses-20170718.nwb\nSource URL: '+link+'\n')
        print('Downloaded verified HDF5 signature, bytes:',path.stat().st_size)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--url',default=URL);p.add_argument('--path',type=Path,default=ROOT/'data/raw'/FILE)
    args=p.parse_args();download(args.path,args.url)
