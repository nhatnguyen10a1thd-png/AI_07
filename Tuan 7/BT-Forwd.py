# 8 Puzzle - Forward Checking Search
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


def get_legal_actions(state, visited):
    legal = []

    for action in ACTIONS:
        next_state = move(state, action)

        if next_state is not None and next_state not in visited:
            legal.append(action)

    return legal


def forward_checking(state, visited):
    """
    Kiểm tra trước miền giá trị của bước tiếp theo.
    Nếu không còn hành động hợp lệ thì xem như thất bại.
    """
    next_domain = get_legal_actions(state, visited)

    if len(next_domain) == 0:
        return None

    return next_domain


def is_solvable(start, goal):
    def inversions(state):
        arr = [x for x in state if x != 0]
        count = 0

        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if arr[i] > arr[j]:
                    count += 1

        return count

    return inversions(start) % 2 == inversions(goal) % 2


def forward_check(assignment, state, goal, visited, depth_limit):
    # assignment complete: đã tới trạng thái đích
    if state == goal:
        return assignment.copy()

    # hết độ sâu thì thất bại
    if len(assignment) >= depth_limit:
        return None

    # SELECT-UNASSIGNED-VARIABLE:
    # ở đây biến tiếp theo chính là bước di chuyển tiếp theo
    domain = get_legal_actions(state, visited)

    # ORDER-DOMAIN-VALUES
    for action in domain:
        next_state = move(state, action)

        # consistent with assignment
        if next_state is not None and next_state not in visited:
            assignment.append((action, next_state))
            visited.add(next_state)

            # FORWARD-CHECKING
            # Nếu chưa tới goal thì kiểm tra bước sau còn nước đi không
            if next_state == goal:
                return assignment.copy()

            removed = forward_checking(next_state, visited)

            if removed is not None:
                result = forward_check(
                    assignment,
                    next_state,
                    goal,
                    visited,
                    depth_limit
                )

                if result is not None:
                    return result

            # restore removed values + remove {var = value}
            visited.remove(next_state)
            assignment.pop()

    return None


def forward_checking_search(start, goal, max_depth=40):
    if start == goal:
        return []

    if not is_solvable(start, goal):
        return None

    # Tăng dần độ sâu để tìm lời giải ngắn hơn
    for depth_limit in range(max_depth + 1):
        assignment = []
        visited = {start}

        result = forward_check(
            assignment,
            start,
            goal,
            visited,
            depth_limit
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
    solution = forward_checking_search(START, GOAL, max_depth=40)

    if solution is None:
        print("Không tìm thấy lời giải.")
        print("Có thể trạng thái không giải được hoặc max_depth quá nhỏ.")
    else:
        print_solution(START, solution)