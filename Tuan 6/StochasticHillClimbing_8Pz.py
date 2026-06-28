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


# --------------- Heuristic / Gia tri danh gia ---------------

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


def value(state, goal):
    """
    Gia tri danh gia cua trang thai.
    Value = -manhattan_distance  =>  Value cang CAO thi cang GAN dich.
    """
    return -manhattan_distance(state, goal)


# --------------- Ham phu tro ---------------

def print_state(state):
    for row in state:
        print(row)
    print("---")


# --------------- Thuat toan Stochastic Hill Climbing ---------------

def Stochastic_Hill_Climbing(problem):
    """
    Thuat toan Stochastic Hill Climbing (Leo doi ngau nhien).

    Ma gia:
    -------
    function Stochastic_Hill_Climbing(Start):
      1. Current_State = Start
      2. TRONG KHI (dung):
         a. Neu Current_State == Goal: tra ve Current_State
         b. Sinh tat ca trang thai lan can cua Current_State
         c. Better_Neighbors = {Neighbor | Value(Neighbor) > Value(Current_State)}
         d. Neu Better_Neighbors rong: tra ve Current_State (cuc dai cuc bo)
         e. Next_State = chon ngau nhien 1 trang thai trong Better_Neighbors
         f. Current_State = Next_State
    """

    current_node = Node(state=problem.initial)
    current_value = value(current_node.state, problem.goal)

    step = 0
    path = [current_node]

    print(f"[Stochastic Hill Climbing] Gia tri ban dau: {current_value} "
          f"(Manhattan = {-current_value})")

    while True:
        if problem.goal_test(current_node.state):
            print(f"[Stochastic Hill Climbing] Da tim thay loi giai sau {step} buoc!")
            break

        step += 1
        better_neighbors = []

        for action in problem.actions(current_node.state):
            next_state = problem.result(current_node.state, action)
            next_value = value(next_state, problem.goal)
            if next_value > current_value:
                better_neighbors.append((next_value, action, next_state))

        if not better_neighbors:
            print(f"[Stochastic Hill Climbing] Bi ket tai cuc dai cuc bo! "
                  f"(Buoc {step}, Value = {current_value})")
            break

        next_value, action, next_state = random.choice(better_neighbors)
        next_node = Node(state=next_state, parent=current_node, action=action)
        current_node = next_node
        current_value = next_value
        path.append(current_node)

        print(f"  Buoc {step}: {action} -> "
              f"Value = {current_value} "
              f"(Manhattan = {-current_value})")

    actions = []
    states = []
    for node in path:
        states.append(node.state)
        if node.action is not None:
            actions.append(node.action)

    return actions, states, problem.goal_test(current_node.state)


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

    print("=" * 50)
    print("  GIAI 8-PUZZLE BANG STOCHASTIC HILL CLIMBING")
    print("=" * 50)
    print("\nTrang thai ban dau:")
    print_state(initial)
    print("Trang thai dich:")
    print_state(goal)

    actions, states, found = Stochastic_Hill_Climbing(problem)

    if not found:
        print(f"\nKhong tim duoc loi giai (bi ket tai cuc dai cuc bo)!")
        print("Trang thai cuoi cung dat duoc:")
        print_state(states[-1])
        print(f"So buoc da di: {len(actions)}")
        print(f"Khoang cach Manhattan con lai: "
              f"{manhattan_distance(states[-1], goal)}")
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
