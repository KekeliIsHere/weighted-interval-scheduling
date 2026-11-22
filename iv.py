from i import Request
from ii import merge_sort_by_finish


def earliest_finish_greedy(requests):
    """
    Task (iv): Greedy heuristic that sorts requests by finish time ascending
    and iteratively selects each compatible request.
    """
    sorted_reqs = list(requests)
    n = len(sorted_reqs)
    if n == 0:
        return 0, []

    if n > 1:
        merge_sort_by_finish(sorted_reqs, 0, n - 1)

    selected = []
    total_value = 0
    last_finish = float("-inf")

    for req in sorted_reqs:
        if req.start >= last_finish:
            selected.append(req)
            total_value += req.value
            last_finish = req.finish

    return total_value, selected