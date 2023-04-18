from itertools import chain, combinations
from collections import Counter

def counter_to_list(data):
    if type(data) == Counter:
        data = list(data.items())
    return [val for val, cnt in data for i in range(cnt)]

def max_values_dict(data):
    max_value = max(data.values())
    return [k for k,v in data.items() if v == max_value], max_value

def merge_list(data):
    return list(itertools.chain(*data))

def get_all_combos(data): # accepts a counter.
    combos = [{}]
    for key in data:
        if data[key] == 0:
            for c in combos:
                c[key] = 0
        else:
            new_combos = []
            for c in combos:
                for i in range(data[key]+1):
                    nc = c.copy()
                    nc[key] = i
                    new_combos.append(nc)
            combos = new_combos
    return combos

def unique_combinations(data, size):
    data = counter_to_list(data)
    combos = list(combinations(data, size))
    return set(combos)

a = Counter({"a":3, "b":4, "c":2, "d":0})
for i in unique_combinations(a, 5):
    print(i)

player_colors = ["blue", "red", "green", "purple"]
