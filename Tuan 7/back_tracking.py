# 8 Puzzle - Backtracking Search
# 0 là ô trống

START = (1, 2, 3,
         4, 0, 6,
         7, 5, 8)

GOAL = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)

# Thứ tự thử hành động
ACTION_ORDER = ["U", "D", "L", "R"]

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

    # Nếu đi ra ngoài bảng thì không hợp lệ
    if not (0 <= nr < 3 and 0 <= nc < 3):
        return None

    new_zero = nr * 3 + nc
    new_state = list(state)

    # Đổi chỗ ô trống với ô cần di chuyển
    new_state[zero], new_state[new_zero] = new_state[new_zero], new_state[zero]

    return tuple(new_state)


def inversion_parity_relative(state, goal):
    """
    Kiểm tra tính giải được tương đối với goal.
    Với bảng 3x3, start giải được nếu số nghịch thế là chẵn.
    """
    goal_order = {}
    index = 0

    for tile in goal:
        if tile != 0:
            goal_order[tile] = index
            index += 1

    arr = []
    for tile in state:
        if tile != 0:
            arr.append(goal_order[tile])

    inv = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1

    return inv % 2


def is_solvable(start, goal):
    return inversion_parity_relative(start, goal) == 0


def recursive_backtracking(state, goal, depth_limit, path, visited):
    # Nếu tới đích thì trả về đường đi
    if state == goal:
        return path.copy()

    # Giới hạn độ sâu để tránh chạy quá lâu
    if len(path) >= depth_limit:
        return None

    # Thử từng hành động giống Order-Domain-Values trong mã giả
    for action in ACTION_ORDER:
        next_state = move(state, action)

        # Kiểm tra hành động hợp lệ và không lặp trạng thái
        if next_state is not None and next_state not in visited:
            visited.add(next_state)
            path.append((action, next_state))

            result = recursive_backtracking(
                next_state,
                goal,
                depth_limit,
                path,
                visited
            )

            if result is not None:
                return result

            # Quay lui
            path.pop()
            visited.remove(next_state)

    return None


def backtracking_search(start, goal, max_depth=40):
    if start == goal:
        return []

    if not is_solvable(start, goal):
        return None

    # Iterative deepening: tăng dần giới hạn độ sâu
    for depth_limit in range(max_depth + 1):
        visited = {start}
        path = []

        result = recursive_backtracking(
            start,
            goal,
            depth_limit,
            path,
            visited
        )

        if result is not None:
            return result

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
    solution = backtracking_search(START, GOAL, max_depth=40)

    if solution is None:
        print("Không tìm thấy lời giải.")
        print("Có thể trạng thái không giải được hoặc max_depth quá nhỏ.")
    else:
        print_solution(START, solution)