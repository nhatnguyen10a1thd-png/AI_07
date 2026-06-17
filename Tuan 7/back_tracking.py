# ============================================================
# 8-Puzzle solved by CSP Backtracking Search
# Mô hình chuẩn:
#   Biến: S0, S1, ..., Sd
#   Miền: D(Si) = tập trạng thái có thể xuất hiện tại bước i
#   Ràng buộc:
#       S0 = START
#       Sd = GOAL
#       Adjacent(Si, Si+1)
#       Không lặp trạng thái
# ============================================================

START = (1, 2, 3,
         0, 4, 6,
         7, 5, 8)

GOAL = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)

MAX_DEPTH = 30

ACTIONS = ["U", "D", "L", "R"]

ACTION_NAME = {
    "U": "Lên",
    "D": "Xuống",
    "L": "Trái",
    "R": "Phải"
}


# ============================================================
# CÁC HÀM CƠ BẢN CỦA 8-PUZZLE
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
        nxt = move(state, action)
        if nxt is not None:
            result.append(nxt)

    return result


def action_between(s1, s2):
    for action in ACTIONS:
        if move(s1, action) == s2:
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
# TẠO MIỀN GIÁ TRỊ CHO CSP
# ============================================================

def build_exact_layers(start, max_depth):
    """
    layers[i] = tập trạng thái có thể đạt được từ start sau đúng i bước.
    Không dùng global visited để không làm mất các trạng thái có thể xuất hiện
    ở độ sâu khác.
    """
    layers = []
    current = {start}
    layers.append(current)

    for _ in range(max_depth):
        next_layer = set()

        for state in current:
            for nxt in neighbors(state):
                next_layer.add(nxt)

        layers.append(next_layer)
        current = next_layer

    return layers


def build_domains(start, goal, depth, start_layers, goal_layers):
    """
    Tạo miền D(Si).

    D(S0) = {start}
    D(Sd) = {goal}

    Với biến trung gian Si:
    D(Si) = trạng thái có thể đi từ START sau i bước
            giao với
            trạng thái có thể đi về GOAL trong depth - i bước
    """

    domains = {}

    for i in range(depth + 1):
        if i == 0 and i == depth:
            # Trường hợp depth = 0
            if start == goal:
                domains[i] = {start}
            else:
                domains[i] = set()

        elif i == 0:
            domains[i] = {start}

        elif i == depth:
            domains[i] = {goal}

        else:
            domains[i] = start_layers[i] & goal_layers[depth - i]

    return domains


# ============================================================
# BACKTRACKING SEARCH CHUẨN CSP
# ============================================================

def select_unassigned_variable(assignment, depth):
    """
    SELECT-UNASSIGNED-VARIABLE
    Chọn biến chưa gán tiếp theo theo thứ tự thời gian: S0, S1, ..., Sd.
    """
    for i in range(depth + 1):
        if i not in assignment:
            return i

    return None


def order_domain_values(var, domains, goal):
    """
    ORDER-DOMAIN-VALUES
    Sắp xếp miền theo Manhattan để ưu tiên trạng thái gần goal hơn.
    Đây chỉ là heuristic phụ, không làm sai bản chất Backtracking CSP.
    """
    return sorted(domains[var], key=lambda state: manhattan(state, goal))


def is_consistent(var, value, assignment):
    """
    Kiểm tra ràng buộc CSP.

    Ràng buộc chính:
    1. Không lặp trạng thái.
    2. Nếu S(var-1) đã gán thì S(var-1) phải kề S(var).
    3. Nếu S(var+1) đã gán thì S(var) phải kề S(var+1).
    """

    # Không cho lặp trạng thái
    if value in assignment.values():
        return False

    # Kiểm tra với biến đứng trước
    if var - 1 in assignment:
        prev_state = assignment[var - 1]

        if value not in neighbors(prev_state):
            return False

    # Kiểm tra với biến đứng sau, nếu đã gán
    if var + 1 in assignment:
        next_state = assignment[var + 1]

        if next_state not in neighbors(value):
            return False

    return True


def recursive_backtracking(assignment, domains, depth, goal):
    """
    BACKTRACKING-SEARCH chuẩn CSP.

    assignment:
        dict lưu phép gán hiện tại.
        Ví dụ:
        assignment[0] = START
        assignment[1] = trạng thái sau bước 1
        assignment[2] = trạng thái sau bước 2
    """

    # Nếu đã gán đủ S0 -> Sd thì trả về nghiệm
    if len(assignment) == depth + 1:
        return assignment.copy()

    var = select_unassigned_variable(assignment, depth)

    for value in order_domain_values(var, domains, goal):
        if is_consistent(var, value, assignment):
            assignment[var] = value

            result = recursive_backtracking(assignment, domains, depth, goal)

            if result is not None:
                return result

            # Quay lui
            del assignment[var]

    return None
def backtracking_csp_8_puzzle(start, goal, max_depth):
    """
    Thử CSP với độ sâu tăng dần:
    d = 1, 2, ..., max_depth

    Mỗi d tạo ra một CSP:
        Biến: S0, S1, ..., Sd
        Ràng buộc: Adjacent(Si, Si+1)
    """

    if not is_solvable(start, goal):
        return None

    # Chỉ trả về 0 bước nếu START thật sự bằng GOAL
    if start == goal:
        return [start]

    start_layers = build_exact_layers(start, max_depth)
    goal_layers = build_exact_layers(goal, max_depth)

    # Sửa chỗ này: bắt đầu từ depth = 1, không bắt đầu từ 0
    for depth in range(1, max_depth + 1):
        domains = build_domains(start, goal, depth, start_layers, goal_layers)

        # Nếu có miền rỗng thì CSP ở depth này thất bại
        if any(len(domains[i]) == 0 for i in range(depth + 1)):
            continue

        # Gán trước S0 = START
        assignment = {
            0: start
        }

        result = recursive_backtracking(assignment, domains, depth, goal)

        if result is not None:
            path = []

            for i in range(depth + 1):
                path.append(result[i])

            # Kiểm tra an toàn: trạng thái cuối phải là GOAL
            if path[-1] == goal:
                return path

    return None


# ============================================================
# IN KẾT QUẢ
# ============================================================

def print_solution(path):
    print("Bước 0: Trạng thái ban đầu")
    print_board(path[0])

    actions = []

    for i in range(1, len(path)):
        action = action_between(path[i - 1], path[i])
        actions.append(action)

        print(f"Bước {i}: Di chuyển {ACTION_NAME[action]} ({action})")
        print_board(path[i])

    print("Đường đi:")
    print(" -> ".join(actions))
    print(f"Tổng số bước: {len(actions)}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    path = backtracking_csp_8_puzzle(START, GOAL, MAX_DEPTH)

    if path is None:
        print("Không tìm thấy lời giải.")
        print("Có thể initial không giải được hoặc MAX_DEPTH quá nhỏ.")
    else:
        print_solution(path)