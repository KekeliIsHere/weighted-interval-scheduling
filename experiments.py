import random
import time
import matplotlib.pyplot as plt

from i import Request, load_data, exhaustive_search
from ii import merge_sort_by_finish, compute_predecessors
from iii import activitySelector
from iv import earliest_finish_greedy


def run_dp(requests):
    reqs = list(requests)
    if not reqs:
        return 0
    sorted_reqs, P = compute_predecessors(reqs)
    # Convert 0-based P (-1 sentinel) to 1-based indexing if iii.py expects 1-based
    v = [0] + [r.value for r in sorted_reqs]
    p_1based = [0] + [idx + 1 for idx in P]
    return activitySelector(len(sorted_reqs), v, p_1based)[0]


def make_synthetic(n, mode="random", seed=42):
    rng = random.Random(seed)
    reqs = []
    for k in range(n):
        if mode == "dense":
            s = rng.randint(0, 100)
            f = s + rng.randint(200, 500)
            v = rng.randint(10, 100)
        elif mode == "skewed":
            # Short low-value traps vs. longer high-value blocks
            if k % 2 == 0:
                s = k * 10
                f = s + 5
                v = rng.randint(1, 5)
            else:
                s = k * 10 - 3
                f = s + 25
                v = rng.randint(60, 100)
        else:  # random
            s = rng.randint(0, n * 10)
            f = s + rng.randint(5, 60)
            v = rng.randint(5, 100)
        reqs.append(Request(f"R{k}", s, f, v))
    return reqs


def main():
    # 1. Verify on 25-row dataset + small random equivalence tests
    dataset = load_data([])
    # Ensure integer minutes if load_data stored strings
    dataset_int = [
        Request(r.id, int(r.start), int(r.finish), int(r.value))
        for r in dataset
    ] if isinstance(dataset[0].start, int) else dataset

    dp_data = run_dp(dataset_int)
    greedy_val, greedy_sched = earliest_finish_greedy(dataset_int)
    print(f"Dataset (n={len(dataset_int)}): DP={dp_data}, Greedy={greedy_val} ({len(greedy_sched)} items)")

    for trial in range(20):
        sample = make_synthetic(12, mode="random", seed=trial)
        opt_val, _ = exhaustive_search(sample)
        assert run_dp(sample) == opt_val, f"Mismatch on trial {trial}"
    print("20/20 randomized equivalence checks (DP == Exhaustive) PASSED.")

    # 2. Graph 1: Small-n runtime (Exhaustive vs DP vs Greedy)
    small_ns = [4, 6, 8, 10, 12, 14, 16, 18, 20]
    t_exh, t_dp_s, t_gr_s = [], [], []
    for n in small_ns:
        data = make_synthetic(n, "random", seed=n)
        t0 = time.perf_counter()
        exhaustive_search(data)
        t_exh.append((time.perf_counter() - t0) * 1000)

        t0 = time.perf_counter()
        run_dp(data)
        t_dp_s.append((time.perf_counter() - t0) * 1000)

        t0 = time.perf_counter()
        earliest_finish_greedy(sorted(data, key=lambda r: r.finish))
        t_gr_s.append((time.perf_counter() - t0) * 1000)

    plt.figure(figsize=(6, 4))
    plt.plot(small_ns, t_exh, "o-", label="Exhaustive Search")
    plt.plot(small_ns, t_dp_s, "s-", label="Weighted Interval DP")
    plt.plot(small_ns, t_gr_s, "^-", label="Earliest-Finish Greedy")
    plt.yscale("log")
    plt.xlabel("Number of Requests (n)")
    plt.ylabel("Runtime (ms, log scale)")
    plt.title("Small-n Runtime Scaling (n = 4 to 20)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("fig1_small_n.png", dpi=300)

    # 3. Graph 2: Large-n scaling (DP pipeline vs Theoretical n log n)
    large_ns = [500, 1000, 2500, 5000, 10000, 20000]
    t_dp_l, t_gr_l = [], []
    for n in large_ns:
        data = make_synthetic(n, "random", seed=n)
        t0 = time.perf_counter()
        run_dp(data)
        t_dp_l.append((time.perf_counter() - t0) * 1000)

        t0 = time.perf_counter()
        reqs_copy = list(data)
        merge_sort_by_finish(reqs_copy, 0, len(reqs_copy) - 1)
        earliest_finish_greedy(reqs_copy)
        t_gr_l.append((time.perf_counter() - t0) * 1000)

    plt.figure(figsize=(6, 4))
    plt.plot(large_ns, t_dp_l, "s-", label="DP Pipeline (Sort + Pred + DP)")
    plt.plot(large_ns, t_gr_l, "^-", label="Greedy Pipeline (Sort + Scan)")
    plt.xlabel("Number of Requests (n)")
    plt.ylabel("Runtime (ms)")
    plt.title("Large-n Runtime Scaling (n = 500 to 20,000)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("fig2_large_n.png", dpi=300)

    # 4. Graph 3: Greedy Optimality Ratio across Input Patterns
    patterns = ["random", "dense", "skewed"]
    ratios = []
    for pat in patterns:
        data = make_synthetic(200, pat, seed=99)
        opt = run_dp(data)
        g_val, _ = earliest_finish_greedy(sorted(data, key=lambda r: r.finish))
        ratios.append((g_val / opt) * 100 if opt > 0 else 100)

    plt.figure(figsize=(6, 4))
    bars = plt.bar(["Random Uniform", "Dense Overlap", "Skewed Value Traps"], ratios, color=["#4C72B0", "#DD8452", "#C44E52"])
    plt.ylim(0, 110)
    plt.ylabel("Greedy Value (% of Optimal DP)")
    plt.title("Greedy Optimality Retention by Input Pattern (n = 200)")
    for bar, r in zip(bars, ratios):
        plt.text(bar.get_x() + bar.get_width() / 2, r + 2, f"{r:.1f}%", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig("fig3_greedy_gap.png", dpi=300)
    print("Saved fig1_small_n.png, fig2_large_n.png, fig3_greedy_gap.png")


if __name__ == "__main__":
    main()