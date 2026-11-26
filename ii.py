from i import load_data, display

def merge_by_finish(A, p, q, r):
    # Create temporary copies of the left subarray A[p..q] and right subarray A[q+1..r]
    L = A[p : q + 1]
    R = A[q + 1 : r + 1]

    i = 0  # pointer for left subarray L
    j = 0  # pointer for right subarray R
    k = p  # pointer for main array A

    # 1. Main comparison loop: runs while BOTH subarrays still have unmerged elements.
    #    Picks whichever Request finishes earlier (<= keeps original order on ties).
    while i < len(L) and j < len(R):
        if L[i].finish <= R[j].finish:
            A[k] = L[i]
            i += 1
        else:
            A[k] = R[j]
            j += 1
        k += 1

    # 2. Cleanup loop for L: if R ran out of elements first, copy the remaining
    #    Requests from L directly into A (they are already sorted).
    while i < len(L):
        A[k] = L[i]
        i += 1
        k += 1

    # 3. Cleanup loop for R: if L ran out of elements first, copy the remaining
    #    Requests from R directly into A (they are already sorted).
    while j < len(R):
        A[k] = R[j]
        j += 1
        k += 1


def merge_sort_by_finish(A, p, r):
    if p < r:
        q = (p + r) // 2
        merge_sort_by_finish(A, p, q)
        merge_sort_by_finish(A, q + 1, r)
        merge_by_finish(A, p, q, r)

#The whole predecessor thing
def find_predecessor(A, i):
    """
    Given A sorted by .finish ascending, finds the largest index j in [0, i - 1]
    such that A[j].finish <= A[i].start.
    Returns -1 if no compatible predecessor exists.
    """
    low = 0
    high = i - 1
    pred = -1

    while low <= high:
        mid = (low + high) // 2
        if A[mid].finish <= A[i].start:
            pred = mid       # mid is compatible; record it and search right for a later one
            low = mid + 1
        else:
            high = mid - 1   # mid finishes too late; search left for an earlier one

    return pred


def compute_predecessors(requests):
    """
    Sorts a copy of requests by finish time and returns (sorted_requests, P),
    where P[i] is the predecessor index of sorted_requests[i].
    """
    sorted_reqs = list(requests)
    if len(sorted_reqs) > 1:
        merge_sort_by_finish(sorted_reqs, 0, len(sorted_reqs) - 1)

    n = len(sorted_reqs)
    P = [-1] * n
    for i in range(n):
        P[i] = find_predecessor(sorted_reqs, i)

    return sorted_reqs, P

#ii.
if __name__ == "__main__":
    requests = []
    load_data(requests)

    sorted, p = compute_predecessors(requests)
    print("This is the sorted array" , display(sorted))
    print("This is the predecessor index ", p)