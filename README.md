# CS456 Final Project – Question B11: Weighted Activity Selection

## Repository Structure
- `i.py`: Request model, `data.csv` loader, and Exhaustive Subset Search baseline.
- `ii.py`: Divide-and-Conquer Merge Sort by finish time and Binary Search predecessor computation.
- `iii.py`: Bottom-up Weighted Interval Dynamic Programming and solution recovery.
- `iv.py`: Earliest-Finish Greedy heuristic.
- `v.py`: Minimal counterexample demonstrating Greedy suboptimality.
- `experiments.py`: Generates synthetic datasets, verifies DP vs. Exhaustive Search, and exports benchmark figures.
- `data.csv`: 25-row facility booking dataset (`id, start, finish, startm, finishm, value`).

## How to Reproduce Verification & Plots
1. Ensure Python 3.10+ and `matplotlib` are installed:
   ```bash
   pip install matplotlib


# Experimental Methodology

## Experimental Objective

The experiments investigate the practical performance of the Exhaustive Search, Dynamic Programming, and Earliest-Finish Greedy algorithms.

Evaluation focuses on two performance measures: **execution time** and **auxiliary memory consumption**. The goal is to observe how both metrics scale as the number of requests increases and compare empirical behavior against theoretical complexity analysis.

## Dataset Generation

Four categories of synthetic datasets test the algorithms across distinct scheduling conditions:

1. **Random Dataset:** Requests use randomly selected start times, finish times, and values to represent general scheduling conditions.
2. **Dense Overlap Dataset:** Start times cluster within a narrow range and finish times fall within a later range, creating heavy request overlap.
3. **Sparse Chain Dataset:** Requests form sequential, non-overlapping intervals, allowing many requests to be selected together.
4. **Skewed Values Dataset:** Most requests receive small values while a smaller subset receives much higher values, testing performance under uneven value distributions.

Key setup details:

* **Reproducibility:** Fixed random seeds generate all datasets.
* **Input sizing:** Small input sizes compare all three algorithms because Exhaustive Search grows too slow at larger scales. Larger input sizes evaluate the scalability of Dynamic Programming and Earliest-Finish Greedy.

## Execution Time Measurement

* **Timer:** Measured with Python's `time.perf_counter()` function.
* **Aggregation:** Each algorithm runs multiple times on the same generated input, recording the **median** execution time to limit the effect of outliers.
* **Scope:** Timing starts after dataset generation, so reported execution times exclude synthetic request creation.

## Memory Measurement

* **Profiler:** Peak memory consumption is measured with Python's `tracemalloc` module.
* **Metric and units:** Peak traced memory allocated during each algorithm's run is recorded in **kibibytes (KiB)** to capture additional memory used by the Python implementation.
* **Scope:** Measurements reflect traced Python allocations rather than total operating system process memory.