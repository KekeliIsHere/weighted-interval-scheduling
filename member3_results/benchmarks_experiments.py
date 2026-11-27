
"""
Member 3 - B11 Experiments and Benchmarking
Run: python member3_experiments.py
Optional: python member3_experiments.py --exhaustive-max 20
Requires: matplotlib, pandas
"""
from dataclasses import dataclass
from bisect import bisect_right
from pathlib import Path
import argparse
import csv
import random
import statistics
import time
import tracemalloc

import matplotlib.pyplot as plt
import pandas as pd


@dataclass(frozen=True)
class Request:
    id: str
    start: int
    finish: int
    value: int


def generate_requests(n, dataset_type="random", seed=42):
    """Create n reproducible, valid requests with positive values."""
    rng = random.Random(seed)
    requests = []

    for i in range(n):
        if dataset_type == "sparse_chain":
            start = i * 12
            finish = start + rng.randint(3, 8)
            value = rng.randint(10, 100)

        elif dataset_type == "dense_overlap":
            # Every interval contains time 50, so all requests overlap.
            start = rng.randint(0, 40)
            finish = rng.randint(60, 100)
            value = rng.randint(10, 100)

        elif dataset_type == "skewed_values":
            start = rng.randint(0, max(10, n * 3))
            finish = start + rng.randint(1, 15)
            # Most values are small; a few are much larger.
            value = rng.randint(5, 20) if rng.random() < 0.90 else rng.randint(150, 300)

        elif dataset_type == "random":
            start = rng.randint(0, max(10, n * 3))
            finish = start + rng.randint(1, 15)
            value = rng.randint(10, 100)

        else:
            raise ValueError(f"Unknown dataset type: {dataset_type}")

        requests.append(Request(f"R{i+1:04d}", start, finish, value))

    return requests


def sort_by_finish(requests):
    """Stable ordering; ties are resolved by start time then ID."""
    return sorted(requests, key=lambda r: (r.finish, r.start, r.id))


def predecessor_indices(sorted_requests):
    """
    Return 1-based predecessor indices, with 0 meaning 'no predecessor'.
    For activity i, find the rightmost earlier finish <= its start.
    """
    finishes = [r.finish for r in sorted_requests]
    p = []
    for i, request in enumerate(sorted_requests):
        # Search only positions before i.
        j = bisect_right(finishes, request.start, 0, i) - 1
        p.append(j + 1 if j >= 0 else 0)
    return p


def exhaustive_search(requests):
    """
    Enumerate every subset. Requests are sorted by finish time so checking
    consecutive selected requests is enough to test compatibility.
    Intended only for small n because it is exponential.
    Returns the maximum value.
    """
    items = sort_by_finish(requests)
    n = len(items)
    best = 0

    for mask in range(1 << n):
        total = 0
        previous_finish = None
        compatible = True

        for i in range(n):
            if mask & (1 << i):
                item = items[i]
                if previous_finish is not None and previous_finish > item.start:
                    compatible = False
                    break
                total += item.value
                previous_finish = item.finish

        if compatible and total > best:
            best = total

    return best


def dynamic_programming(requests):
    """Weighted interval scheduling DP using binary-search predecessors."""
    items = sort_by_finish(requests)
    p = predecessor_indices(items)  # 1-based predecessor positions
    dp = [0] * (len(items) + 1)

    for i in range(1, len(items) + 1):
        include_value = items[i - 1].value + dp[p[i - 1]]
        exclude_value = dp[i - 1]
        dp[i] = max(include_value, exclude_value)

    return dp[-1]


def earliest_finish_greedy(requests):
    """
    Unweighted earliest-finish selection baseline.
    It maximizes the number of compatible requests, not total priority value.
    Return the total priority value of the selected requests for comparison.
    """
    items = sort_by_finish(requests)
    selected = []
    last_finish = None

    for item in items:
        if last_finish is None or item.start >= last_finish:
            selected.append(item)
            last_finish = item.finish

    return sum(item.value for item in selected)


def measure_runtime(function, requests, repeats=3):
    """Median wall-clock runtime; timing is measured without tracemalloc."""
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        function(requests)
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def measure_peak_memory(function, requests):
    """Approximate peak Python allocation in KiB, measured separately."""
    tracemalloc.start()
    function(requests)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024


def run_benchmarks(exhaustive_max=18, repeats=3):
    records = []
    distributions = ["random", "dense_overlap", "sparse_chain", "skewed_values"]

    # Exponential method: deliberately cap at a small n.
    exhaustive_sizes = [n for n in [8, 10, 12, 14, 16, 18, 20]
                        if n <= exhaustive_max]

    for distribution in distributions:
        for n in exhaustive_sizes:
            data = generate_requests(n, distribution, seed=1000 + n)
            # Verify the methods agree on the optimum before recording.
            exact = exhaustive_search(data)
            dp_value = dynamic_programming(data)
            if exact != dp_value:
                raise AssertionError(
                    f"Exhaustive/DP mismatch for {distribution}, n={n}: "
                    f"{exact} != {dp_value}"
                )

            for name, function in [
                ("Exhaustive", exhaustive_search),
                ("Dynamic Programming", dynamic_programming),
                ("Earliest-Finish Greedy", earliest_finish_greedy),
            ]:
                runtime = measure_runtime(function, data, repeats)
                memory = measure_peak_memory(function, data)
                records.append({
                    "dataset": distribution,
                    "algorithm": name,
                    "n": n,
                    "runtime_seconds": runtime,
                    "peak_memory_kib": memory,
                    "total_value": function(data),
                })

    # Larger sizes for polynomial-time methods.
    scalable_sizes = [100, 250, 500, 1000, 2000, 5000]
    for distribution in distributions:
        for n in scalable_sizes:
            data = generate_requests(n, distribution, seed=2000 + n)
            for name, function in [
                ("Dynamic Programming", dynamic_programming),
                ("Earliest-Finish Greedy", earliest_finish_greedy),
            ]:
                runtime = measure_runtime(function, data, repeats)
                memory = measure_peak_memory(function, data)
                records.append({
                    "dataset": distribution,
                    "algorithm": name,
                    "n": n,
                    "runtime_seconds": runtime,
                    "peak_memory_kib": memory,
                    "total_value": function(data),
                })

    return pd.DataFrame(records)


def create_plots(results, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    # Plot 1: runtime for all methods on the random dataset.
    subset = results[results["dataset"] == "random"]
    plt.figure(figsize=(9, 5.5))
    for algorithm in subset["algorithm"].unique():
        part = subset[subset["algorithm"] == algorithm].sort_values("n")
        plt.plot(part["n"], part["runtime_seconds"], marker="o", label=algorithm)
    plt.yscale("log")
    plt.xlabel("Number of requests (n)")
    plt.ylabel("Median runtime (seconds, log scale)")
    plt.title("Runtime comparison - random requests")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "runtime_random.png", dpi=300)
    plt.close()

    # Plot 2: DP and greedy scaling across all four data types.
    scalable = results[results["algorithm"] != "Exhaustive"]
    for distribution in scalable["dataset"].unique():
        part = scalable[scalable["dataset"] == distribution]
        plt.figure(figsize=(9, 5.5))
        for algorithm in part["algorithm"].unique():
            alg = part[part["algorithm"] == algorithm].sort_values("n")
            plt.plot(alg["n"], alg["runtime_seconds"], marker="o", label=algorithm)
        plt.xlabel("Number of requests (n)")
        plt.ylabel("Median runtime (seconds)")
        plt.title(f"Runtime scaling - {distribution.replace('_', ' ').title()}")
        plt.grid(True, linestyle="--", linewidth=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"runtime_{distribution}.png", dpi=300)
        plt.close()

    # Plot 3: peak memory for the random dataset.
    plt.figure(figsize=(9, 5.5))
    for algorithm in results["algorithm"].unique():
        part = results[(results["dataset"] == "random") &
                       (results["algorithm"] == algorithm)].sort_values("n")
        plt.plot(part["n"], part["peak_memory_kib"], marker="o", label=algorithm)
    plt.xlabel("Number of requests (n)")
    plt.ylabel("Peak traced Python memory (KiB)")
    plt.title("Peak memory comparison - random requests")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "memory_random.png", dpi=300)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive-max", type=int, default=18,
                        help="Largest n to test with exhaustive search (default: 18)")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="member3_results")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = run_benchmarks(args.exhaustive_max, args.repeats)
    results.to_csv(output_dir / "benchmark_results.csv", index=False)
    create_plots(results, output_dir)

    print("\nBenchmark results saved to:", output_dir.resolve())
    print("CSV:", (output_dir / "benchmark_results.csv").resolve())
    print("Plots:", output_dir.resolve())
    print("\nSmall-input correctness check: Exhaustive Search and DP agreed "
          "for every tested dataset and input size.")
    print("\nExhaustive-search timing summary:")
    print(results[results["algorithm"] == "Exhaustive"]
          .groupby("n")["runtime_seconds"].median().to_string())


if __name__ == "__main__":
    main()
