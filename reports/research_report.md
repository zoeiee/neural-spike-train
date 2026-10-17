# Event-aligned neural spike train analysis of mouse ALM

*Research report status: methods implemented and algorithmically tested; no empirical spike train data were accessible during packaging.*

## Abstract
We specify an analysis of actual extracellular neuronal unit spike times in a mouse anterior lateral motor cortex delay-response task, using a single session from DANDI 000006. ISI variability, trial-aligned rasters, mean rates, PSTHs and condition comparisons are implemented in Python. **Neural response measurements and inferential summaries have not yet been produced.**

## Introduction and scientific question
How do neuronal spike dynamics change across task events, and how do trial conditions relate to subsequent neural activity? Spike trains represent actual electrical discharge events isolated by extracellular spike sorting.

## Dataset
DANDI 000006, Economo et al. 2018: mouse anterior lateral motor cortex extracellular recordings during a delay response task. Selected public asset: `sub-anm372795/sub-anm372795_ses-20170718.nwb` (a ~452-kB session). This is **not** an Allen visual-coding grating experiment; orientation selectivity cannot be inferred.

## Methods
The repository downloads the genuine NWB asset, inspects trials and units using PyNWB, selects a measurable unit, validates timestamps, aligns spikes to documented events when available (otherwise labels trial start accurately), and creates 50-ms PSTHs, ISI histograms and per-trial firing rates. The response window [0, 0.5) s is compared with [-0.5, 0) s baseline. Differences across two supported task conditions use a bootstrap over **trials**, never over individual spikes. A methods timeline figure is included and explicitly depicts a schematic, not neural data.

## Results
No empirical spike times, firing rates, ISI CV, raster, PSTH, or confidence interval have been calculated in the packaging environment. Run the documented workflow to generate the actual CSVs, figures and populated report.

## Discussion
Conditional differences in motor-cortex activity would be associated with a task but may reflect sensory input, motor planning, action execution or reward signals, not any one process on its own.

## Limitations
One session and one selected unit; spike sorting may not isolate a unique neuron. Trials are repeated within an animal rather than independent animal replicates. Some task-event fields may be absent; the code labels the fallback clearly and never calls trial-start time a confirmed stimulus onset. Internet/PyNWB were unavailable in the packaging environment.

## Conclusion
This repo is an auditable, independently testable analysis implementation. It requires the true NWB recording for scientific findings.

## References
1. [DANDI 000006](https://dandiarchive.org/dandiset/000006/0.220126.1855).
2. Economo MN et al. (2018), *Nature*, doi:10.1038/s41586-018-0642-9.
3. [Neurodata Without Borders](https://www.nwb.org/).
