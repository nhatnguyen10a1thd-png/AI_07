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


# --------------- Heuristic ---------------

def manhattan_distance(state, goal):
    """Tính khoảng cách Manhattan từ state đến goal"""
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


# --------------- Hàm phụ trợ ---------------

def state_to_tuple(state):
    return tuple(tuple(row) for row in state)


def solution(node):
    """Truy vết lời giải từ node đích về node gốc"""
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


def print_state(state):
    for row in state:
        print(row)
    print("---")


# --------------- Thuật toán IDA* ---------------

FOUND = "FOUND"


def search(node, g, threshold, problem):
    """
    Hàm tìm kiếm DFS giới hạn theo ngưỡng (threshold).
    - g: chi phí thực tế từ gốc đến node hiện tại (số bước đã đi)
    - f = g + h(n), trong đó h(n) = manhattan_distance
    - Nếu f > threshold: cắt nhánh, trả về f (giá trị nhỏ nhất vượt ngưỡng)
    - Nếu đến đích: trả về FOUND
    """
    h = manhattan_distance(node.state, problem.goal)
    f = g + h

    if f > threshold:
        return f  # Trả về giá trị f nhỏ nhất vượt ngưỡng

    if problem.goal_test(node.state):
        return FOUND

    min_threshold = float("inf")

    for action in problem.actions(node.state):
        next_state = problem.result(node.state, action)
        child = Node(state=next_state, parent=node, action=action)

        result = search(child, g + 1, threshold, problem)

        if result == FOUND:
            return FOUND

        if result < min_threshold:
            min_threshold = result

    return min_threshold


def IDA_star(problem):
    """
    Thuật toán IDA* (Iterative Deepening A*).

    Ý tưởng:
    - Bắt đầu với ngưỡng threshold = h(start)
    - Thực hiện DFS giới hạn theo threshold
    - Nếu không tìm thấy lời giải, tăng threshold lên giá trị f nhỏ nhất
      vượt ngưỡng cũ trong lần lặp trước
    - Lặp lại cho đến khi tìm được lời giải hoặc không còn nhánh để mở rộng

    Ưu điểm so với A*:
    - Tiết kiệm bộ nhớ: O(d) thay vì O(b^d) (d = độ sâu, b = nhánh)
    - Vẫn đảm bảo tìm được lời giải tối ưu nếu heuristic admissible
    """
    start_node = Node(problem.initial)
    threshold = manhattan_distance(start_node.state, problem.goal)

    print(f"[IDA*] Ngưỡng ban đầu: {threshold}")
    iteration = 0

    while True:
        iteration += 1
        result = search(start_node, 0, threshold, problem)

        if result == FOUND:
            print(f"[IDA*] Tìm thấy lời giải sau {iteration} vòng lặp")
            # Truy vết lời giải: tìm lại đường đi bằng DFS giới hạn
            actions, states = trace_solution(start_node, 0, threshold, problem)
            return actions, states

        if result == float("inf"):
            print("[IDA*] Không tìm thấy lời giải!")
            return None, None

        print(f"[IDA*] Vòng {iteration}: ngưỡng {threshold} -> {result}")
        threshold = result


def trace_solution(node, g, threshold, problem):
    """
    Sau khi biết threshold cuối cùng dẫn đến lời giải,
    chạy lại DFS để truy vết đường đi hoàn chỉnh.
    """
    h = manhattan_distance(node.state, problem.goal)
    f = g + h

    if f > threshold:
        return None, None

    if problem.goal_test(node.state):
        return solution(node)

    for action in problem.actions(node.state):
        next_state = problem.result(node.state, action)
        child = Node(state=next_state, parent=node, action=action)

        actions, states = trace_solution(child, g + 1, threshold, problem)
        if actions is not None:
            return actions, states

    return None, None


# --------------- Chương trình chính ---------------

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

    print("=" * 40)
    print("  GIẢI 8-PUZZLE BẰNG THUẬT TOÁN IDA*")
    print("=" * 40)
    print("\nTrạng thái ban đầu:")
    print_state(initial)
    print("Trạng thái đích:")
    print_state(goal)

    actions, states = IDA_star(problem)

    if actions is None:
        print("\nKhông tìm thấy lời giải!")
    else:
        print(f"\nTổng số bước: {len(actions)}")
        print("Chuỗi hành động:", " -> ".join(actions))
        print("\nCác trạng thái:")
        for idx, state in enumerate(states):
            if idx == 0:
                print(f"Bước {idx} (Ban đầu):")
            else:
                print(f"Bước {idx} ({actions[idx - 1]}):")
            print_state(state)
