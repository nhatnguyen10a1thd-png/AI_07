import copy


class Problem:
    def __init__(self, initial, goal):
        self.initial = initial
        self.goal = goal

    def find_zero(self, board):
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    return i, j
        return None

    def actions(self, state):
        i, j = self.find_zero(state)
        moves = []

        if j > 0:
            moves.append("Trai")
        if j < 2:
            moves.append("Phai")
        if i > 0:
            moves.append("Len")
        if i < 2:
            moves.append("Xuong")

        return moves

    def result(self, state, action):
        i, j = self.find_zero(state)

        if action == "Trai":
            ni, nj = i, j - 1
        elif action == "Phai":
            ni, nj = i, j + 1
        elif action == "Len":
            ni, nj = i - 1, j
        elif action == "Xuong":
            ni, nj = i + 1, j
        else:
            return None

        new_state = copy.deepcopy(state)
        new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]

        return new_state

    def results(self, state, action):
        """
        Tra ve tat ca ket qua co the xay ra khi thuc hien action.

        Trong 8-puzzle thong thuong, moi action chi tao ra mot ket qua.
        Ham van tra ve danh sach de AND_SEARCH co the xu ly nut AND.
        """
        next_state = self.result(state, action)

        if next_state is None:
            return []

        return [next_state]

    def goal_test(self, state):
        return state == self.goal


# --------------- Ham phu tro ---------------

def state_to_tuple(state):
    return tuple(tuple(row) for row in state)


def manhattan_distance(state, goal):
    """Tinh khoang cach Manhattan tu state den goal"""
    distance = 0
    goal_pos = {}

    for i in range(3):
        for j in range(3):
            goal_pos[goal[i][j]] = (i, j)

    for i in range(3):
        for j in range(3):
            tile = state[i][j]
            if tile != 0:
                goal_i, goal_j = goal_pos[tile]
                distance += abs(i - goal_i) + abs(j - goal_j)

    return distance


def is_solvable(initial, goal):
    """Kiem tra 8-puzzle co the di tu initial den goal hay khong"""
    goal_order = {}
    position = 0

    for row in goal:
        for tile in row:
            if tile != 0:
                goal_order[tile] = position
                position += 1

    sequence = []
    for row in initial:
        for tile in row:
            if tile != 0:
                sequence.append(goal_order[tile])

    inversions = 0
    for i in range(len(sequence)):
        for j in range(i + 1, len(sequence)):
            if sequence[i] > sequence[j]:
                inversions += 1

    return inversions % 2 == 0


def extract_solution(problem, plan):
    """Lay chuoi hanh dong va trang thai tu ke hoach AND-OR"""
    actions = []
    states = [copy.deepcopy(problem.initial)]

    current_state = copy.deepcopy(problem.initial)
    current_plan = plan

    while isinstance(current_plan, dict) and "action" in current_plan:
        action = current_plan["action"]
        next_state = problem.results(current_state, action)[0]

        actions.append(action)
        states.append(next_state)

        next_key = state_to_tuple(next_state)
        current_state = next_state
        current_plan = current_plan["plans"][next_key]

    return actions, states


def print_state(state):
    for row in state:
        print(row)
    print("---")


# --------------- Thuat toan AND-OR Graph Search ---------------

def AND_OR_GRAPH_SEARCH(problem, max_depth=31):
    """
    Thuat toan AND-OR Graph Search.

    Ma gia:
    -------
    function AND_OR_GRAPH_SEARCH(problem):
        return OR_SEARCH(problem.initial_state, problem, [])

    Trong do:
    - OR_SEARCH chon mot action co the dan den loi giai.
    - AND_SEARCH yeu cau tat ca ket qua cua action deu phai co loi giai.
    - path duoc dung de tranh lap.
    """
    if not is_solvable(problem.initial, problem.goal):
        return None

    return OR_SEARCH(problem.initial, problem, [], max_depth)


def OR_SEARCH(state, problem, path, depth_remaining):
    """
    Tai nut OR, chi can tim mot action thanh cong.
    Tra ve ke hoach dang:

        {
            "action": action,
            "plans": ke_hoach_cho_tung_ket_qua
        }
    """
    if problem.goal_test(state):
        return []

    if state in path or depth_remaining == 0:
        return None

    actions = problem.actions(state)

    # Uu tien hanh dong dua trang thai den gan dich hon
    actions.sort(
        key=lambda action: manhattan_distance(
            problem.result(state, action),
            problem.goal
        )
    )

    for action in actions:
        result_states = problem.results(state, action)

        plan = AND_SEARCH(
            result_states,
            problem,
            path + [state],
            depth_remaining - 1
        )

        if plan is not None:
            return {
                "action": action,
                "plans": plan
            }

    return None


def AND_SEARCH(states, problem, path, depth_remaining):
    """
    Tai nut AND, tat ca state ket qua deu phai tim duoc ke hoach.
    """
    plans = {}

    for state in states:
        plan_s = OR_SEARCH(state, problem, path, depth_remaining)

        if plan_s is None:
            return None

        plans[state_to_tuple(state)] = plan_s

    return plans


# --------------- Chuong trinh chinh ---------------

if __name__ == "__main__":
    initial = [
        [2, 8, 3],
        [1, 6, 4],
        [7, 0, 5]
    ]

    goal = [
        [1, 2, 3],
        [8, 0, 4],
        [7, 6, 5]
    ]

    problem = Problem(initial, goal)

    print("=" * 55)
    print("  GIAI 8-PUZZLE BANG AND-OR GRAPH SEARCH")
    print("=" * 55)
    print("\nTrang thai ban dau:")
    print_state(initial)
    print("Trang thai dich:")
    print_state(goal)

    plan = AND_OR_GRAPH_SEARCH(problem)

    if plan is None:
        print("\nKhong tim thay ke hoach!")
    else:
        actions, states = extract_solution(problem, plan)

        print(f"\nTong so buoc: {len(actions)}")
        print("Chuoi hanh dong:", " -> ".join(actions))
        print("\nCac trang thai:")

        for idx, state in enumerate(states):
            if idx == 0:
                print(f"Buoc {idx} (Ban dau):")
            else:
                print(f"Buoc {idx} ({actions[idx - 1]}):")
            print_state(state)
