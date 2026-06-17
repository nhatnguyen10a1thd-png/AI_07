# ============================================================
# 8-Puzzle solved by CSP + AC-3
# Mo hinh:
#   Bien: S0, S1, ..., Sd
#   Mien: D(Si) la tap trang thai co the xuat hien tai buoc i
#   Rang buoc:
#       S0 = START
#       Sd = GOAL
#       Adjacent(Si, Si+1)
#       Khong lap trang thai khi trich nghiem
#
# Luu y:
#   AC-3 chi loc mien theo rang buoc cung. Sau do can backtracking tren
#   mien da loc de lay ra mot duong di cu the.
# ============================================================

from collections import deque


START = (1, 2, 3,
         4, 0, 6,
         7, 5, 8)

GOAL = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)

MAX_DEPTH = 30

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
    Khong dung global visited de khong lam mat trang thai co the xuat hien
    o nhieu do sau khac nhau.
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
    """
    D(S0) = {start}
    D(Sd) = {goal}
    D(Si) = states di duoc tu start sau i buoc
            giao voi states co the di ve goal trong depth - i buoc.
    """
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
# AC-3: ARC CONSISTENCY
# ============================================================

def related_variables(var, depth):
    result = []

    if var - 1 >= 0:
        result.append(var - 1)

    if var + 1 <= depth:
        result.append(var + 1)

    return result


def init_arcs(depth):
    arcs = deque()

    for i in range(depth):
        arcs.append((i, i + 1))
        arcs.append((i + 1, i))

    return arcs


def revise(domains, xi, xj):
    """
    Xoa khoi D(Xi) cac gia tri khong co gia tri ho tro trong D(Xj).

    Voi 8-puzzle, support cua x trong D(Si) la mot y trong D(Sj)
    sao cho x va y ke nhau bang dung mot nuoc di.
    """
    removed = set()

    for x in domains[xi]:
        has_support = any(adjacent(x, y) for y in domains[xj])

        if not has_support:
            removed.add(x)

    if not removed:
        return False

    domains[xi] = domains[xi] - removed

    return True


def AC3(domains, depth):
    """
    Tra ve True neu tat ca mien con khac rong sau khi lam arc consistency.
    Tra ve False neu co mien rong, tuc CSP o depth hien tai that bai.
    """
    arcs = init_arcs(depth)

    while arcs:
        xi, xj = arcs.popleft()

        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False

            for xk in related_variables(xi, depth):
                if xk != xj:
                    arcs.append((xk, xi))

    return True


# ============================================================
# TRICH NGHIEM SAU KHI AC-3 LOC MIEN
# ============================================================

def select_unassigned_variable(assignment, depth):
    for i in range(depth + 1):
        if i not in assignment:
            return i

    return None


def order_domain_values(var, domains, goal):
    return sorted(domains[var], key=lambda state: (manhattan(state, goal), state))


def is_consistent(var, value, assignment):
    if value in assignment.values():
        return False

    if var - 1 in assignment:
        previous_state = assignment[var - 1]

        if not adjacent(previous_state, value):
            return False

    if var + 1 in assignment:
        next_state = assignment[var + 1]

        if not adjacent(value, next_state):
            return False

    return True


def backtrack_on_ac3_domains(assignment, domains, depth, goal):
    """
    AC-3 khong truc tiep tao duong di. Ham nay tim phep gan day du
    tren cac mien da duoc AC-3 rut gon.
    """
    if len(assignment) == depth + 1:
        return assignment.copy()

    var = select_unassigned_variable(assignment, depth)

    for value in order_domain_values(var, domains, goal):
        if is_consistent(var, value, assignment):
            assignment[var] = value

            result = backtrack_on_ac3_domains(assignment, domains, depth, goal)

            if result is not None:
                return result

            del assignment[var]

    return None


def ac3_csp_8_puzzle(start, goal, max_depth):
    """
    Thu CSP voi do sau tang dan:
      1. Tao mien D(S0..Sd)
      2. Chay AC-3 de loc mien theo cung (Si, Si+1)
      3. Backtracking tren mien da loc de lay duong di cu the
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

        ac3_domains = {
            var: set(values)
            for var, values in domains.items()
        }

        if not AC3(ac3_domains, depth):
            continue

        assignment = {
            0: start
        }

        result = backtrack_on_ac3_domains(assignment, ac3_domains, depth, goal)

        if result is not None:
            path = []

            for i in range(depth + 1):
                path.append(result[i])

            if path[-1] == goal:
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
    path = ac3_csp_8_puzzle(START, GOAL, MAX_DEPTH)

    if path is None:
        print("Khong tim thay loi giai.")
        print("Co the initial khong giai duoc hoac MAX_DEPTH qua nho.")
    else:
        print_solution(path)
