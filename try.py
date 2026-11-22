import csv, itertools
#from datetime import datetime, time

class Request:
    id: int
    start: str
    finish: str
    value: int
    
    def __init__(self, id, start, finish, value):
        self.id = id
        self.start = start
        self.finish = finish
        #self.start: time = datetime.strptime(start, "%H:%M").time()
        #self.finish: time = datetime.strptime(finish, "%H:%M").time()
        self.value = int(value)

        if self.start > self.finish or self.start == self.finish:
            raise ValueError("Start must be < finish")
        if self.value <= 0:
            raise ValueError("Value must be positive")

    # not sure if i'd need this
    def __str__(self):
        return f"{self.id}"

    def compatible_with(self, other):
        return self.finish <= other.start or other.finish <= self.start

with open("data.csv", mode="r", newline="", encoding="utf-8") as file:
  reader = csv.reader(file)

  # skip the header row
  header = next(reader)

  requests = []

  # create request object and store in request array
  for id, date, fac, activity, requesting, start, finish, startm, finishm, value  in reader:
    new_request = Request(id, start, finish, value)
    requests.append(new_request)

# using brute force, find every possible combination of requests and compute best value
def exhaustive_search(requests, max):
    n = len(requests)
    best_value = 0
    best_subset = []

    # loop through all possible subsets
    for i in range(1 << n):
        subset = []

        # loop through all elements
        for j in range(n):
            # append only if jth bit is set
            if i & (1 << j):
                subset.append(requests[j])
        # subset = [requests[j] for j in range(n) if i >> j & 1]

        # if feasible and at most max, compare total value to current best_value
        if len(subset) <= max and is_feasible(subset):
            total = sum(r.value for r in subset)
            if total > best_value:
                best_value, best_subset = total, subset
    return best_value, best_subset


#is_feasible function: checks if every request is valid with every other request
def is_feasible(subset):
    for i in range(len(subset)):
        for j in range(i + 1, len(subset)):
            if not subset[i].compatible_with(subset[j]):
                return False
    return True

# for displaying objects nicely
def display(subset):
    display_subset = []
    for s in subset:
        display_subset.append(s.id)
    return display_subset

#i.
max = int(input("Whst is the max size of requests: "))
val, subset = exhaustive_search(requests, max)

print(val, subset)
print(val, display(subset))