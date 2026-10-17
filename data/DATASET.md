# Dataset provenance

- DANDI: https://dandiarchive.org/dandiset/000006/0.220126.1855 (Economo et al., 2018).
- NWB asset: `sub-anm372795/sub-anm372795_ses-20170718.nwb`, published task-based ALM mouse recording.
- Official teaching resource documents the approximately 452-kB file: https://nwb4edu.github.io/Lesson_1/01-Obtaining_Datasets_with_DANDI.html
- Download the **single asset**, not all files in the Dandiset, with `python scripts/download_data.py`.
- Only if verified actual event-time columns exist can a plot be called stimulus-aligned. Otherwise the software explicitly identifies trial-start alignment.
- The pre-generated methods schematic is **not** a neural result.
