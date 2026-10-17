# Neural spike-train analysis | DANDI 000006

Fundamental analysis of **real** extracellular spike times in one mouse anterior lateral motor-cortex (ALM) session during a delay-response task. No deep learning, invented neural spikes, or dashboard.

**Artifact status:** modular implementation and algorithmic unit tests available; **actual NWB download, trial analysis, result CSVs, main figures and empirical report have not been run** because network access/PyNWB installation were unavailable during ZIP generation. The packaged method timeline illustration is a **schematic, not measured data**. When run on a network-connected Mac, the pipeline will create trial-level data CSVs, figures and a full report from the genuine recording.

## Why this dataset rather than Allen Visual Coding Neuropixels?
Official Allen visual-coding sessions can be multiple gigabytes. Dandiset **000006** from Economo et al. (2018) provides trial-annotated extracellular spike sorting in NWB and a documented ~450-kB individual file. This study analyzes **task/event-locked sensorimotor firing, not visual grating orientation tuning**. Do not describe output as visual tuning or neural coding of visual stimulus orientation.

Dataset: https://dandiarchive.org/dandiset/000006/0.220126.1855
Subject/session: `sub-anm372795/sub-anm372795_ses-20170718.nwb`. Educational data access instructions: https://nwb4edu.github.io/Lesson_1/01-Obtaining_Datasets_with_DANDI.html . The downloader uses a fixed content-addressed public S3 object shown in those instructions, not the complete Dandiset.

## Set up on Apple Silicon Mac (VS Code)
Use **Python 3.12** (standard venv/pip; no Conda):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/download_data.py
python scripts/run_analysis.py
```

All commands assume the repository root is the working directory. Or download the single NWB from the DANDI archive manually and save as `data/raw/sub-anm372795_ses-20170718.nwb`. The end-to-end remote download and PyNWB execution were **not available for verification during packaging**; if a selected session lacks explicitly timed event columns, the pipeline uses `start_time` and accurately labels it *trial start, not stimulus onset*.

## What each computation tells you
- **Spikes:** estimated times of neuronal action potentials obtained through extracellular spike sorting; the NWB unit label is not a guaranteed single biological neuron.
- **Firing rate (Hz):** spikes divided by measurement time in seconds. 4 spikes over 0.5 seconds = 8 spikes/s (per trial).
- **Inter-spike intervals (ISI):** separation of successive spikes in the continuous recording; coefficient of variation CV = sample SD(ISIs)/mean(ISIs); CV near 1 is consistent with, but does not prove, irregular Poisson-like timing.
- **Raster:** spike times relative to each selected experimental trial event, one row per trial (window -0.5 to +1 s).
- **PSTH:** average count per time bin divided by its bin width; 50-ms bins yield spikes/s and reveal trial-locked activity changes.
- **Trial response:** baseline in [-0.5,0) s vs response in [0,0.5) s. We compare the two best supported recorded trial conditions without inventing orientation angles.
- **Uncertainty:** 95% nonparametric bootstrap percentile interval from repeated resampling of individual *trials*, not spikes (2,000 iterations, fixed seed 42). These intervals describe within-session repeatability only.
- **Trial types:** task conditions may correspond to left/right response preparation; movement, reward and condition could confound interpretation.

## Generated artifacts after successful empirical run
`data/processed/` is reserved for future intermediate products. `results/tables/trial_firing_rates.csv`, `psth.csv`, and `summary.json` hold real analysis outputs. `results/figures/01_raster`, `02_isi_histogram`, `03_psth`, `04_rate_distribution`, `05_condition_psth`, and `06_condition_comparison` each appear in PNG and PDF format, alongside the explicitly schematic `methods_analysis_windows`. `reports/research_report.md` is overwritten with an empirical report with measured rates, sample sizes, bootstrap interval and limitations.

## Validity checks / limitations
Automatically check nonempty NWB Units+trials, unique spike timestamps, finite event timestamps, >=3 trials per condition and nonoverlapping 1.5-second trial windows. When quality labels are missing, selecting the most active unit is not evidence of well-isolated sorting. This project does not establish orientation tuning, multi-animal inference or cause/effect. Quality, event semantics, and session selection need review against the original paper before publication.

Unit tests exercise exact unit conversions, ISI, trial-based PSTH, resampled CI reproducibility, event selection and failure modes. They use **small manufactured arrays only for testing**; test fixtures are never claimed as scientific results.

## Scientific references
- Economo MN et al., Distinct descending motor cortex pathways and their roles in movement, *Nature* 2018. DOI: https://doi.org/10.1038/s41586-018-0642-9
- DANDI 000006: https://dandiarchive.org/dandiset/000006/0.220126.1855
- Neurodata Without Borders: https://www.nwb.org/

## Resume bullets (accurate after real-data execution)
- Developed a reproducible PyNWB-based pipeline for extracellular spike-train and trial-locked firing analyses from the DANDI archive.
- Implemented ISI/CV statistics, firing rates, event-aligned raster plots, 50-ms PSTHs and two-condition response comparisons.
- Quantified uncertainty with reproducible trial-level bootstrap intervals and automated tests, while documenting session-level interpretation limits.
