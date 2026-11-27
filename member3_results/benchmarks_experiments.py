
"""
Member 3 - Weighted Interval Scheduling
Time and Space Complexity Experiments

Run from the main project folder:
python member3_results/benchmarks_experiments.py

Optional:
python member3_results/benchmarks_experiments.py --exhaustive-max 20
"""

from dataclasses import dataclass
from bisect import bisect_right
from pathlib import Path
import argparse
import statistics
import time
import random
import tracemalloc

import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. REQUEST DATA STRUCTURE
# --------------------------------------------------

@dataclass(frozen=True)
class Request:
    id: str
    start: int
    finish: int
    value: int


# --------------------------------------------------
# 2. GENERATE SYNTHETIC DATASETS
# --------------------------------------------------

def generate_requests(n, dataset_type="random", seed=42):

    rng = random.Random(seed)
    requests = []

    for i in range(n):

        if dataset_type == "sparse_chain":
            start = i * 12
            finish = start + rng.randint(3, 8)
            value = rng.randint(10, 100)

        elif dataset_type == "dense_overlap":
            start = rng.randint(0, 40)
            finish = rng.randint(60, 100)
            value = rng.randint(10, 100)

        elif dataset_type == "skewed_values":
            start = rng.randint(0, max(10, n * 3))
            finish = start + rng.randint(1, 15)

            if rng.random() < 0.90:
                value = rng.randint(5, 20)
            else:
                value = rng.randint(150, 300)

        elif dataset_type == "random":
            start = rng.randint(0, max(10, n * 3))
            finish = start + rng.randint(1, 15)
            value = rng.randint(10, 100)

        else:
            raise ValueError("Unknown dataset type")

        requests.append(
            Request(f"R{i + 1:04d}", start, finish, value)
        )

    return requests


# --------------------------------------------------
# 3. SORT REQUESTS BY FINISH TIME
# --------------------------------------------------

def sort_by_finish(requests):

    return sorted(
        requests,
        key=lambda r: (r.finish, r.start, r.id)
    )


# --------------------------------------------------
# 4. COMPUTE PREDECESSORS
# --------------------------------------------------

def predecessor_indices(sorted_requests):

    finishes = [r.finish for r in sorted_requests]
    predecessors = []

    for i, request in enumerate(sorted_requests):

        j = bisect_right(
            finishes,
            request.start,
            0,
            i
        ) - 1

        predecessors.append(j + 1 if j >= 0 else 0)

    return predecessors


# --------------------------------------------------
# 5. EXHAUSTIVE SEARCH
# --------------------------------------------------

def exhaustive_search(requests):

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

                if (
                    previous_finish is not None
                    and previous_finish > item.start
                ):
                    compatible = False
                    break

                total += item.value
                previous_finish = item.finish

        if compatible and total > best:
            best = total

    return best


# --------------------------------------------------
# 6. DYNAMIC PROGRAMMING
# --------------------------------------------------

def dynamic_programming(requests):

    items = sort_by_finish(requests)
    predecessors = predecessor_indices(items)

    dp = [0] * (len(items) + 1)

    for i in range(1, len(items) + 1):

        include_value = (
            items[i - 1].value
            + dp[predecessors[i - 1]]
        )

        exclude_value = dp[i - 1]

        dp[i] = max(include_value, exclude_value)

    return dp[-1]


# --------------------------------------------------
# 7. EARLIEST-FINISH GREEDY
# --------------------------------------------------

def earliest_finish_greedy(requests):

    items = sort_by_finish(requests)

    selected = []
    last_finish = None

    for item in items:

        if last_finish is None or item.start >= last_finish:

            selected.append(item)
            last_finish = item.finish

    return sum(item.value for item in selected)


# --------------------------------------------------
# 8. MEASURE EXECUTION TIME
# --------------------------------------------------

def measure_runtime(function, requests, repeats=5):

    samples = []

    for _ in range(repeats):

        start = time.perf_counter()

        function(requests)

        end = time.perf_counter()

        samples.append(end - start)

    return statistics.median(samples)


# --------------------------------------------------
# 9. MEASURE PEAK MEMORY
# --------------------------------------------------

def measure_peak_memory(function, requests):

    tracemalloc.start()

    try:
        function(requests)

        _, peak = tracemalloc.get_traced_memory()

    finally:
        tracemalloc.stop()

    return peak / 1024


# --------------------------------------------------
# 10. RUN ALL EXPERIMENTS
# --------------------------------------------------

def run_benchmarks(exhaustive_max=18, repeats=5):

    records = []

    distributions = [
        "random",
        "dense_overlap",
        "sparse_chain",
        "skewed_values"
    ]

    algorithms = {
        "Exhaustive": exhaustive_search,
        "Dynamic Programming": dynamic_programming,
        "Earliest-Finish Greedy": earliest_finish_greedy
    }

    # Exhaustive Search is tested only on small inputs.
    small_sizes = [
        n for n in [8, 10, 12, 14, 16, 18, 20]
        if n <= exhaustive_max
    ]

    # DP and Greedy are tested on larger inputs too.
    large_sizes = [100, 250, 500, 1000, 2000, 5000]

    for distribution in distributions:

        print(f"\nTesting dataset: {distribution}")

        # SMALL INPUT EXPERIMENTS
        for n in small_sizes:

            data = generate_requests(
                n,
                distribution,
                seed=1000 + n
            )

            # Verify DP against Exhaustive Search.
            exact = exhaustive_search(data)
            dp_result = dynamic_programming(data)

            if exact != dp_result:
                raise AssertionError(
                    f"Incorrect result for {distribution}, n={n}"
                )

            for name, function in algorithms.items():

                runtime = measure_runtime(
                    function,
                    data,
                    repeats
                )

                memory = measure_peak_memory(
                    function,
                    data
                )

                records.append({
                    "dataset": distribution,
                    "algorithm": name,
                    "n": n,
                    "runtime_seconds": runtime,
                    "peak_memory_kib": memory,
                    "total_value": function(data)
                })

        # LARGE INPUT EXPERIMENTS
        for n in large_sizes:

            data = generate_requests(
                n,
                distribution,
                seed=2000 + n
            )

            scalable_algorithms = {
                "Dynamic Programming": dynamic_programming,
                "Earliest-Finish Greedy": earliest_finish_greedy
            }

            for name, function in scalable_algorithms.items():

                runtime = measure_runtime(
                    function,
                    data,
                    repeats
                )

                memory = measure_peak_memory(
                    function,
                    data
                )

                records.append({
                    "dataset": distribution,
                    "algorithm": name,
                    "n": n,
                    "runtime_seconds": runtime,
                    "peak_memory_kib": memory,
                    "total_value": function(data)
                })

    return pd.DataFrame(records)


# --------------------------------------------------
# 11. GRAPH GENERATION
# --------------------------------------------------

def create_plots(results, output_dir):

    output_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------
    # GRAPH 1: SMALL INPUT RUNTIME - ALL ALGORITHMS
    # ----------------------------------------------

    small = results[
        (results["dataset"] == "random")
        & (results["algorithm"] == "Exhaustive")
    ]

    small_n = small["n"].tolist()

    plt.figure(figsize=(10, 6))

    for algorithm in [
        "Exhaustive",
        "Dynamic Programming",
        "Earliest-Finish Greedy"
    ]:

        part = results[
            (results["dataset"] == "random")
            & (results["algorithm"] == algorithm)
            & (results["n"].isin(small_n))
        ].sort_values("n")

        plt.plot(
            part["n"],
            part["runtime_seconds"],
            marker="o",
            label=algorithm
        )

    plt.yscale("log")
    plt.xlabel("Number of requests (n)")
    plt.ylabel("Median runtime (seconds, log scale)")
    plt.title("Runtime Comparison - All Algorithms")
    plt.grid(True, which="both", linestyle="--")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        output_dir / "runtime_all_algorithms_random.png",
        dpi=300
    )
    plt.close()

    # ----------------------------------------------
    # GRAPH 2: LARGE INPUT RUNTIME
    # DP AND GREEDY FOR ALL DATASET TYPES
    # ----------------------------------------------

    for distribution in results["dataset"].unique():

        part = results[
            (results["dataset"] == distribution)
            & (results["algorithm"] != "Exhaustive")
        ]

        plt.figure(figsize=(10, 6))

        for algorithm in part["algorithm"].unique():

            alg = part[
                part["algorithm"] == algorithm
            ].sort_values("n")

            plt.plot(
                alg["n"],
                alg["runtime_seconds"],
                marker="o",
                label=algorithm
            )

        plt.xlabel("Number of requests (n)")
        plt.ylabel("Median runtime (seconds)")
        plt.title(
            f"Runtime Scaling - {distribution.replace('_', ' ').title()}"
        )
        plt.grid(True, linestyle="--")
        plt.legend()
        plt.tight_layout()

        plt.savefig(
            output_dir / f"runtime_scaling_{distribution}.png",
            dpi=300
        )
        plt.close()

    # ----------------------------------------------
    # GRAPH 3: SMALL INPUT MEMORY - ALL ALGORITHMS
    # ----------------------------------------------

    plt.figure(figsize=(10, 6))

    for algorithm in [
        "Exhaustive",
        "Dynamic Programming",
        "Earliest-Finish Greedy"
    ]:

        part = results[
            (results["dataset"] == "random")
            & (results["algorithm"] == algorithm)
            & (results["n"].isin(small_n))
        ].sort_values("n")

        plt.plot(
            part["n"],
            part["peak_memory_kib"],
            marker="o",
            label=algorithm
        )

    plt.xlabel("Number of requests (n)")
    plt.ylabel("Peak traced Python memory (KiB)")
    plt.title("Space Usage Comparison - All Algorithms")
    plt.grid(True, linestyle="--")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        output_dir / "memory_all_algorithms_random.png",
        dpi=300
    )
    plt.close()

    # ----------------------------------------------
    # GRAPH 4: LARGE INPUT MEMORY - DP AND GREEDY
    # ----------------------------------------------

    for distribution in results["dataset"].unique():

        part = results[
            (results["dataset"] == distribution)
            & (results["algorithm"] != "Exhaustive")
        ]

        plt.figure(figsize=(10, 6))

        for algorithm in part["algorithm"].unique():

            alg = part[
                part["algorithm"] == algorithm
            ].sort_values("n")

            plt.plot(
                alg["n"],
                alg["peak_memory_kib"],
                marker="o",
                label=algorithm
            )

        plt.xlabel("Number of requests (n)")
        plt.ylabel("Peak traced Python memory (KiB)")
        plt.title(
            f"Space Usage Scaling - {distribution.replace('_', ' ').title()}"
        )
        plt.grid(True, linestyle="--")
        plt.legend()
        plt.tight_layout()

        plt.savefig(
            output_dir / f"memory_scaling_{distribution}.png",
            dpi=300
        )
        plt.close()


# --------------------------------------------------
# 12. MAIN PROGRAM
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--exhaustive-max",
        type=int,
        default=18
    )

    parser.add_argument(
        "--repeats",
        type=int,
        default=5
    )

    parser.add_argument(
        "--output",
        default="member3_results"
    )

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Starting Weighted Interval Scheduling Experiments...")

    results = run_benchmarks(
        exhaustive_max=args.exhaustive_max,
        repeats=args.repeats
    )

    # Save experimental results.
    csv_path = output_dir / "benchmark_results.csv"
    results.to_csv(csv_path, index=False)

    # Generate graphs.
    create_plots(results, output_dir)

    print("\nEXPERIMENTS COMPLETED SUCCESSFULLY")

    print("\nCSV saved to:")
    print(csv_path.resolve())

    print("\nGraphs saved to:")
    print(output_dir.resolve())

    print("\nCorrectness check:")
    print("Exhaustive Search and DP agreed on all tested small inputs.")

    print("\nExhaustive Search runtime summary:")

    print(
        results[
            results["algorithm"] == "Exhaustive"
        ].groupby("n")["runtime_seconds"].median()
    )


if __name__ == "__main__":
    main()
