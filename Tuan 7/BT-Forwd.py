# 8 Puzzle - Backtracking CSP + Forward Checking Search
# 0 là ô trống

START = (1, 2, 3,
         4, 0, 6,
         7, 5, 8)

GOAL = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)

ACTIONS = ["U", "D", "L", "R"]

ACTION_NAME = {
    "U": "Lên",
    "D": "Xuống",
    "L": "Trái",
    "R": "Phải"
}


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


def action_between(state, next_state):
    for action in ACTIONS:
        if move(state, action) == next_state:
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


def build_exact_layers(start, max_depth):
    """
    layers[i] = tập trạng thái có thể đạt được từ start sau đúng i bước.
    Không dùng global visited để giữ đúng mô hình CSP theo từng độ sâu.
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
    D(Si) = states đi được từ start sau i bước
            giao với states có thể đi về goal trong depth - i bước.
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


def select_unassigned_variable(assignment, depth):
    for i in range(depth + 1):
        if i not in assignment:
            return i

    return None


def order_domain_values(var, domains, goal):
    return sorted(domains[var], key=lambda state: (manhattan(state, goal), state))


def is_consistent(var, value, assignment):
    # Không lặp trạng thái trên đường đi.
    if value in assignment.values():
        return False

    # Ràng buộc Adjacent(Si-1, Si).
    if var - 1 in assignment:
        previous_state = assignment[var - 1]

        if value not in neighbors(previous_state):
            return False

    # Ràng buộc Adjacent(Si, Si+1), nếu biến sau đã được gán.
    if var + 1 in assignment:
        next_state = assignment[var + 1]

        if next_state not in neighbors(value):
            return False

    return True


def forward_check_domains(var, assignment, domains, depth):
    """
    Forward Checking: sau khi gán Svar, lọc trước miền của S(var+1).
    Nếu S(var+1) không còn giá trị hợp lệ thì cắt nhánh sớm.
    """
    next_var = var + 1

    if next_var > depth or next_var in assignment:
        return domains

    filtered_domain = {
        value
        for value in domains[next_var]
        if is_consistent(next_var, value, assignment)
    }

    if len(filtered_domain) == 0:
        return None

    new_domains = domains.copy()
    new_domains[next_var] = filtered_domain

    return new_domains


def recursive_forward_check(assignment, domains, depth, goal):
    if len(assignment) == depth + 1:
        return assignment.copy()

    var = select_unassigned_variable(assignment, depth)

    for value in order_domain_values(var, domains, goal):
        if is_consistent(var, value, assignment):
            assignment[var] = value

            checked_domains = forward_check_domains(var, assignment, domains, depth)

            if checked_domains is not None:
                result = recursive_forward_check(
                    assignment,
                    checked_domains,
                    depth,
                    goal
                )

                if result is not None:
                    return result

            del assignment[var]

    return None


def forward_checking_search(start, goal, max_depth=40):
    if start == goal:
        return []

    if not is_solvable(start, goal):
        return None

    max_depth = max(0, max_depth)
    start_layers = build_exact_layers(start, max_depth)
    goal_layers = build_exact_layers(goal, max_depth)

    # Tăng dần độ sâu: mỗi depth tạo một CSP S0, S1, ..., Sd.
    for depth in range(1, max_depth + 1):
        domains = build_domains(start, goal, depth, start_layers, goal_layers)

        if any(len(domains[i]) == 0 for i in range(depth + 1)):
            continue

        assignment = {
            0: start
        }

        result = recursive_forward_check(assignment, domains, depth, goal)

        if result is not None:
            path = []

            for i in range(depth + 1):
                path.append(result[i])

            if path[-1] == goal:
                solution = []

                for i in range(1, len(path)):
                    action = action_between(path[i - 1], path[i])
                    solution.append((action, path[i]))

                return solution

    return None


def print_solution(start, solution):
    print("Bước 0: Trạng thái ban đầu")
    print_board(start)

    for step, (action, state) in enumerate(solution, start=1):
        print(f"Bước {step}: Di chuyển {ACTION_NAME[action]} ({action})")
        print_board(state)

    print("Đường đi:")
    print(" -> ".join(action for action, _ in solution))
    print(f"Tổng số bước: {len(solution)}")


if __name__ == "__main__":
    solution = forward_checking_search(START, GOAL, max_depth=40)

    if solution is None:
        print("Không tìm thấy lời giải.")
        print("Có thể trạng thái không giải được hoặc max_depth quá nhỏ.")
    else:
        print_solution(START, solution)
