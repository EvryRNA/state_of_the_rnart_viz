# State-of-the-RNArt visualisations

This code runs the different visualisations of the paper `State-of-the-RNArt`. 

All the different visualisations can be run in this repository.

Here are some example of the available visualisations:

### Heatmap
RNASolo | RNA_Puzzles | CASP_RNA
:-------------------------:|:-------------------------:|:-------------------------:
![](docker_data/plots/heatmap/RNASOLO_heatmap.png) | ![](docker_data/plots/heatmap/RNA_PUZZLES_heatmap.png)| ![](docker_data/plots/heatmap/CASP_RNA_heatmap.png)

### Box plot
RNASolo |                    RNA_Puzzles                     | CASP_RNA
:-------------------------:|:--------------------------------------------------:|:-------------------------:
![](docker_data/plots/boxplot/RNASOLO_box.png) | ![](docker_data/plots/boxplot/RNA_PUZZLES_box.png) | ![](docker_data/plots/boxplot/CASP_RNA_box.png)

### Polar plot 
RNASolo | RNA_Puzzles | CASP_RNA
:-------------------------:|:-------------------------:|:-------------------------:
![](docker_data/plots/polar/RNASOLO.png) | ![](docker_data/plots/polar/RNA_PUZZLES.png)| ![](docker_data/plots/polar/CASP_RNA.png)

## Installation

The installations can be done to do the different visualisations. 

To do so, you can use: 
```bash
pip install -r requirements.txt
```

## Usage

To run the visualisations, one can use:
```bash
make viz
```
or 
```bash
python -m src.viz_cli
```

It will run all the visualisations and save them in the `docker_data/plots` folder.


## Metrics computation

You can find the different metrics computation in the `docker_data/output` folder.

There are metrics computation for the `RNA_PUZZLES`,`CASP_RNA` and `RNASOLO` datasets.

You can recompute the metrics by running:
```bash
make run
```
or 
```bash
python -m src.benchmark.score_computation
```

## Directory

This repository is organised as follows:
- `docker_data`: the different predictions from the nine benchmarked tools for `RNA_PUZZLES`,`CASP_RNA` and `RNASOLO` datasets.
                 It also includes the different metrics computation for these datasets (in the `docker_data/output` folder).
                 The visualisations are saved in the `docker_data/plots` folder.
- `src`: the different scripts to run the visualisations and the metrics computation.
- `Makefile`: a Makefile to run the different scripts.
- `requirements.txt`: the different requirements to run the scripts.

## Citation

If you use this code, please cite the following paper:

```
State-of-the-RNArt: benchmarking current methods for RNA 3D structure prediction
Clément Bernard, Guillaume Postic, Sahar Ghannay, Fariza Tahi
bioRxiv 2023.12.22.573067; doi: https://doi.org/10.1101/2023.12.22.573067
```