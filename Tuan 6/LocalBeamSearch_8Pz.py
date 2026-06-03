import copy
import random


class Node:
    def __init__(self, state=None, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action


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
        random.shuffle(moves)
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

    def goal_test(self, state):
        return state == self.goal


def state_to_tuple(state):
    return tuple(tuple(row) for row in state)


def manhattan_distance(state, goal):
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


def value(state, goal):
    return -manhattan_distance(state, goal)


def print_state(state):
    for row in state:
        print(row)
    print("---")


def random_state_from(problem, steps=20):
    current = copy.deepcopy(problem.initial)
    for _ in range(steps):
        action = random.choice(problem.actions(current))
        current = problem.result(current, action)
    return current


def solution(node):
    actions = []
    states = []
    while node is not None:
        states.append(node.state)
        if node.action is not None:
            actions.append(node.action)
        node = node.parent
    actions.reverse()
    states.reverse()
    return actions, states


def Local_Beam_Search(problem, k=2, max_iters=200, random_steps=20):
    """
    Local Beam Search (k) cho 8-puzzle.
    - Khởi tạo k trạng thái ngẫu nhiên từ Start.
    - Sinh tất cả lân cận, kiểm tra đích.
    - Chọn k trạng thái tốt nhất theo Value (=-Manhattan).
    """

    if k <= 0:
        return None, None, False

    current_nodes = []
    seen = set()
    while len(current_nodes) < k:
        state = random_state_from(problem, random_steps)
        key = state_to_tuple(state)
        if key in seen:
            continue
        seen.add(key)
        current_nodes.append(Node(state=state))

    for _ in range(max_iters):
        neighbors = []

        for node in current_nodes:
            if problem.goal_test(node.state):
                actions, states = solution(node)
                return actions, states, True

            for action in problem.actions(node.state):
                next_state = problem.result(node.state, action)
                child = Node(state=next_state, parent=node, action=action)
                neighbors.append(child)

        for child in neighbors:
            if problem.goal_test(child.state):
                actions, states = solution(child)
                return actions, states, True

        if not neighbors:
            break

        best_by_state = {}
        for child in neighbors:
            key = state_to_tuple(child.state)
            if key not in best_by_state:
                best_by_state[key] = child
            else:
                if value(child.state, problem.goal) > value(best_by_state[key].state, problem.goal):
                    best_by_state[key] = child

        ranked = sorted(
            best_by_state.values(),
            key=lambda n: value(n.state, problem.goal),
            reverse=True,
        )
        current_nodes = ranked[:k]

        if not current_nodes:
            break

    return None, None, False


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

    actions, states, found = Local_Beam_Search(problem, k=3, max_iters=300, random_steps=25)

    print("=" * 55)
    print("  8-PUZZLE LOCAL BEAM SEARCH")
    print("=" * 55)
    print(f"Beam width (k): 3")

    if not found:
        print("\nKhong tim duoc loi giai.")
    else:
        print(f"\nTong so buoc: {len(actions)}")
        print("Chuoi hanh dong:", " -> ".join(actions))
        print("\nCac trang thai:")
        for idx, state in enumerate(states):
            if idx == 0:
                print(f"Buoc {idx} (Ban dau):")
            else:
                print(f"Buoc {idx} ({actions[idx - 1]}):")
            print_state(state)
