# ============================================================
# 8-Puzzle solved by CSP Min-Conflicts
# Mo hinh:
#   Bien: S0, S1, ..., Sd
#   Mien:
#       D(S0) = {START}
#       D(Sd) = {GOAL}
#       D(Si) = states di duoc tu START sau i buoc
#               giao voi states co the di ve GOAL trong d - i buoc
#   Rang buoc:
#       S0 = START
#       Sd = GOAL
#       Adjacent(Si, Si+1)
#       Khong lap trang thai
#
# Min-Conflicts tao mot phep gan day du, sau do sua dan cac bien
# dang gay xung dot bang gia tri lam tong xung dot nho nhat.
# ============================================================

import random


START = (1, 2, 3,
         4, 0, 6,
         7, 5, 8)

GOAL = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)

MAX_DEPTH = 30
MAX_STEPS = 20000
MAX_RESTARTS = 80

ACTIONS = ["U", "D", "L", "R"]

ACTION_NAME = {
    "U": "Len",
    "D": "Xuong",
    "L": "Trai",
    "R": "Phai"
}

_NEIGHBOR_CACHE = {}


# ============================================================
# CAC HAM CO BAN CUA 8-PUZZLE
# ============================================================

def print_board(state):
    for i in range(0, 9, 3):
        row = state[i:i + 3]
        print(" ".join("_" if x == 0 else str(x) for x in row))
    print()


def move(state, action):
    zero = state.index(0)
    r, c = divmod(zero, 3)

    if action == "U":
        nr, nc = r - 1, c
    elif action == "D":
        nr, nc = r + 1, c
    elif action == "L":
        nr, nc = r, c - 1
    elif action == "R":
        nr, nc = r, c + 1
    else:
        return None

    if not (0 <= nr < 3 and 0 <= nc < 3):
        return None

    new_zero = nr * 3 + nc
    new_state = list(state)

    new_state[zero], new_state[new_zero] = new_state[new_zero], new_state[zero]

    return tuple(new_state)


def neighbors(state):
    result = []

    for action in ACTIONS:
        next_state = move(state, action)

        if next_state is not None:
            result.append(next_state)

    return result


def neighbor_set(state):
    if state not in _NEIGHBOR_CACHE:
        _NEIGHBOR_CACHE[state] = set(neighbors(state))

    return _NEIGHBOR_CACHE[state]


def adjacent(state1, state2):
    return state2 in neighbor_set(state1)


def action_between(state1, state2):
    for action in ACTIONS:
        if move(state1, action) == state2:
            return action

    return None


def manhattan(state, goal):
    goal_pos = {}

    for i, tile in enumerate(goal):
        goal_pos[tile] = divmod(i, 3)

    total = 0

    for i, tile in enumerate(state):
        if tile == 0:
            continue

        r1, c1 = divmod(i, 3)
        r2, c2 = goal_pos[tile]
        total += abs(r1 - r2) + abs(c1 - c2)

    return total


def is_solvable(start, goal):
    goal_order = {}
    index = 0

    for tile in goal:
        if tile != 0:
            goal_order[tile] = index
            index += 1

    arr = []

    for tile in start:
        if tile != 0:
            arr.append(goal_order[tile])

    inv = 0

    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1

    return inv % 2 == 0


# ============================================================
# TAO MIEN GIA TRI CHO CSP
# ============================================================

def build_exact_layers(start, max_depth):
    """
    layers[i] = tap trang thai co the dat duoc tu start sau dung i buoc.
    Khong dung global visited de giu dung mo hinh CSP theo tung do sau.
    """
    layers = []
    current = {start}
    layers.append(current)

    for _ in range(max_depth):
        next_layer = set()

        for state in current:
            for next_state in neighbors(state):
                next_layer.add(next_state)

        layers.append(next_layer)
        current = next_layer

    return layers


def build_domains(start, goal, depth, start_layers, goal_layers):
    domains = {}

    for i in range(depth + 1):
        if i == 0 and i == depth:
            domains[i] = {start} if start == goal else set()
        elif i == 0:
            domains[i] = {start}
        elif i == depth:
            domains[i] = {goal}
        else:
            domains[i] = start_layers[i] & goal_layers[depth - i]

    return domains


# ============================================================
# HAM DO XUNG DOT
# ============================================================

def edge_conflict_count(assignment, var, value):
    conflicts = 0

    if var - 1 in assignment and not adjacent(assignment[var - 1], value):
        conflicts += 1

    if var + 1 in assignment and not adjacent(value, assignment[var + 1]):
        conflicts += 1

    return conflicts


def duplicate_conflict_count(assignment, var, value):
    conflicts = 0

    for other_var, other_value in assignment.items():
        if other_var != var and other_value == value:
            conflicts += 1

    return conflicts


def variable_conflict_count(assignment, var):
    value = assignment[var]
    return (
        edge_conflict_count(assignment, var, value)
        + duplicate_conflict_count(assignment, var, value)
    )


def total_conflicts(assignment, depth):
    conflicts = 0

    for i in range(depth):
        if not adjacent(assignment[i], assignment[i + 1]):
            conflicts += 1

    seen = {}
    for var, value in assignment.items():
        seen.setdefault(value, []).append(var)

    for vars_with_same_value in seen.values():
        n = len(vars_with_same_value)
        if n > 1:
            conflicts += n * (n - 1) // 2

    return conflicts


def conflicted_variables(assignment, depth):
    result = []

    for var in range(1, depth):
        if variable_conflict_count(assignment, var) > 0:
            result.append(var)

    return result


def value_conflict_score(assignment, var, value):
    old_value = assignment[var]
    assignment[var] = value

    score = variable_conflict_count(assignment, var)

    if var - 1 in assignment:
        score += variable_conflict_count(assignment, var - 1)

    if var + 1 in assignment:
        score += variable_conflict_count(assignment, var + 1)

    assignment[var] = old_value
    return score


# ============================================================
# MIN-CONFLICTS
# ============================================================

def create_random_assignment(domains, depth, goal):
    assignment = {
        0: next(iter(domains[0])),
        depth: next(iter(domains[depth]))
    }

    for var in range(1, depth):
        values = list(domains[var])

        if not values:
            return None

        # Uu tien mot gia tri gan goal hon, nhung van co ngau nhien.
        values.sort(key=lambda state: (manhattan(state, goal), random.random()))
        sample_size = min(10, len(values))
        assignment[var] = random.choice(values[:sample_size])

    return assignment


def min_conflicts_for_depth(domains, depth, goal, max_steps, max_restarts):
    if depth == 0:
        if next(iter(domains[0])) == goal:
            return {
                0: goal
            }
        return None

    for _ in range(max_restarts):
        assignment = create_random_assignment(domains, depth, goal)

        if assignment is None:
            continue

        if depth <= 1:
            return assignment.copy() if total_conflicts(assignment, depth) == 0 else None

        for _ in range(max_steps):
            if total_conflicts(assignment, depth) == 0:
                return assignment.copy()

            conflicted = conflicted_variables(assignment, depth)

            if not conflicted:
                # Chi con xung dot lien quan endpoint; doi bien ke endpoint.
                candidates = []
                if not adjacent(assignment[0], assignment[1]):
                    candidates.append(1)
                if not adjacent(assignment[depth - 1], assignment[depth]):
                    candidates.append(depth - 1)
                conflicted = candidates

            if not conflicted:
                return assignment.copy()

            var = random.choice(conflicted)
            values = list(domains[var])

            if not values:
                break

            scored_values = []
            for value in values:
                score = value_conflict_score(assignment, var, value)
                tie_breaker = manhattan(value, goal)
                scored_values.append((score, tie_breaker, random.random(), value))

            min_score = min(item[0] for item in scored_values)
            best_values = [
                value
                for score, _, _, value in scored_values
                if score == min_score
            ]
            assignment[var] = random.choice(best_values)

    return None


def min_conflicts_8_puzzle(start, goal, max_depth=30,
                           max_steps=20000, max_restarts=80):
    """
    Thu depth tang dan. Moi depth tao mot CSP day du, sau do dung
    Min-Conflicts de sua cac bien dang vi pham rang buoc.
    """
    if not is_solvable(start, goal):
        return None

    if start == goal:
        return [start]

    max_depth = max(0, max_depth)
    start_layers = build_exact_layers(start, max_depth)
    goal_layers = build_exact_layers(goal, max_depth)

    for depth in range(1, max_depth + 1):
        domains = build_domains(start, goal, depth, start_layers, goal_layers)

        if any(len(domains[i]) == 0 for i in range(depth + 1)):
            continue

        result = min_conflicts_for_depth(
            domains,
            depth,
            goal,
            max_steps,
            max_restarts
        )

        if result is not None:
            path = []

            for i in range(depth + 1):
                path.append(result[i])

            if path[-1] == goal and total_conflicts(result, depth) == 0:
                return path

    return None


# ============================================================
# IN KET QUA
# ============================================================

def print_solution(path):
    print("Buoc 0: Trang thai ban dau")
    print_board(path[0])

    actions = []

    for i in range(1, len(path)):
        action = action_between(path[i - 1], path[i])
        actions.append(action)

        print(f"Buoc {i}: Di chuyen {ACTION_NAME[action]} ({action})")
        print_board(path[i])

    print("Duong di:")
    print(" -> ".join(actions))
    print(f"Tong so buoc: {len(actions)}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    path = min_conflicts_8_puzzle(
        START,
        GOAL,
        max_depth=MAX_DEPTH,
        max_steps=MAX_STEPS,
        max_restarts=MAX_RESTARTS
    )

    if path is None:
        print("Khong tim thay loi giai.")
        print("Co the min-conflicts chua hoi tu hoac MAX_DEPTH qua nho.")
    else:
        print_solution(path)
