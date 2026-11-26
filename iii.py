def activitySelector(n, v, p):  # With n the nuumber of events, v the table of values,
    # and p the table of predecessors

    # The DP table
    F = [0] * (n + 1)

    # Computing the optimal values
    for i in range(1, n + 1):
        F[i] = max(F[i - 1], v[i] + F[p[i]])

    # Traceback
    activitiesSelected = []
    i = n

    while i > 0:
        if v[i] + F[p[i]] >= F[i - 1]:
            activitiesSelected.insert(0, i)
            i = p[i]
        else:
            i = i - 1

    return F[n], activitiesSelected


# Selceting at most q activities (2D approach)
def selectAtMostQ(n, q, v, p):
    # Initialize DP table
    F = [[0] * (q + 1) for _ in range(n + 1)]

    # Computing the optimal values
    for k in range(1, q + 1):
        for j in range(1, n + 1):
            F[j][k] = max(F[j - 1][k], v[j] + F[p[j]][k - 1])

    # Traceback
    activitiesSelected = []
    j = n
    k = q

    while j > 0 and k > 0:
        if v[j] + F[p[j]][k - 1] >= F[j - 1][k]:
            activitiesSelected.insert(0, j)
            j = p[j]
            k = k - 1
        else:
            j = j - 1

    return F[n][q], activitiesSelected
