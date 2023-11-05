from itertools import combinations

def unique_combinations(elements):
    all_combinations = set()
    for r in range(1, len(elements) + 1):
        for combo in combinations(elements, r):
            all_combinations.add(frozenset(combo))
    return [set(combo) for combo in all_combinations
            if len(combo)!=len(elements)]

if __name__=="__main__":
    my_list = list(range(3))
    combinations = unique_combinations(my_list)
    for combo in combinations:
        print(combo)
