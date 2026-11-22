from i import Request, exhaustive_search
from iv import earliest_finish_greedy


def run_counterexample():
    # Minimal 2-request counterexample where Earliest-Finish Greedy fails:
    # R1 finishes early (minute 120) with low value (10), blocking R2 (value 100).
    requests = [
        Request(id="R1", start=60, finish=120, value=10),
        Request(id="R2", start=90, finish=300, value=100),
    ]

    greedy_val, greedy_sched = earliest_finish_greedy(requests)
    opt_val, opt_sched = exhaustive_search(requests)

    print(f"Greedy Value : {greedy_val} -> {[r.id for r in greedy_sched]}")
    print(f"Optimal Value: {opt_val} -> {[r.id for r in opt_sched]}")


if __name__ == "__main__":
    run_counterexample()