import copy
import random
import math


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


def h(state, goal):
    """
    Ham heuristic h(state) = manhattan_distance(state, goal).
    Gia tri cang THAP thi cang GAN dich.
    """
    return manhattan_distance(state, goal)


# --------------- Ham phu tro ---------------

def print_state(state):
    for row in state:
        print(row)
    print("---")


# --------------- Thuat toan Simulated Annealing ---------------

def Simulated_Annealing(problem, T0=500.0, Tmin=0.01, alpha=0.9995, max_steps=100000):
    """
    Thuat toan Simulated Annealing (Lam nguoi mo phong) cho bai toan 8-puzzle.

    Ma gia:
    -------
    function SimulatedAnnealing(start, goal):
      current_state = start
      T = T0
      while T > Tmin:
          if current_state == goal: return current_state
          next_state = RandomNeighbor(current_state)
          delta = h(next_state) - h(current_state)
          if delta < 0:
              current = next
          else:
              p = exp(-delta / T)
              if Random(0, 1) < p:
                  current_state = next_state
          T = alpha * T
      return current_state

    Tham so:
    --------
    T0        : Nhiet do ban dau (default=100.0)
    Tmin      : Nhiet do dung (default=0.01)
    alpha     : He so lam nguoi (0 < alpha < 1, default=0.995)
    max_steps : So buoc toi da de tranh lap vo han (default=50000)
    """

    current_node = Node(state=problem.initial)
    current_h = h(current_node.state, problem.goal)

    T = T0
    step = 0
    path = [current_node]

    print(f"[Simulated Annealing] Trang thai ban dau: h = {current_h}")
    print(f"[Simulated Annealing] T0={T0}, Tmin={Tmin}, alpha={alpha}")

    while T > Tmin and step < max_steps:

        # Kiem tra trang thai dich
        if problem.goal_test(current_node.state):
            print(f"[Simulated Annealing] Da tim thay loi giai sau {step} buoc!")
            return path_to_solution(path), True

        step += 1

        # Chon ngau nhien 1 trang thai lan can
        actions = problem.actions(current_node.state)
        if not actions:
            break
        action = random.choice(actions)
        next_state = problem.result(current_node.state, action)
        next_h = h(next_state, problem.goal)

        # Tinh delta = h(next) - h(current)
        # delta < 0 => next tot hon (Manhattan nho hon) => chap nhan luon
        # delta >= 0 => next kem hon => chap nhan voi xac suat exp(-delta / T)
        delta = next_h - current_h

        if delta < 0:
            # Chuyen sang trang thai tot hon
            next_node = Node(state=next_state, parent=current_node, action=action)
            current_node = next_node
            current_h = next_h
            path.append(current_node)
            print(f"  Buoc {step:>5}: {action:<6} | "
                  f"h: {current_h + abs(delta)} -> {current_h} | "
                  f"Delta={delta:+d} | T={T:.4f} | [CHAP NHAN - Tot hon]")
        else:
            # Chap nhan trang thai kem hon voi xac suat p
            p = math.exp(-delta / T)
            r = random.random()
            if r < p:
                next_node = Node(state=next_state, parent=current_node, action=action)
                current_node = next_node
                current_h = next_h
                path.append(current_node)
                print(f"  Buoc {step:>5}: {action:<6} | "
                      f"h: {current_h - delta} -> {current_h} | "
                      f"Delta={delta:+d} | T={T:.4f} | p={p:.4f} | [CHAP NHAN - Ngau nhien]")
            else:
                print(f"  Buoc {step:>5}: {action:<6} | "
                      f"h: {current_h} -> {next_h} | "
                      f"Delta={delta:+d} | T={T:.4f} | p={p:.4f} | [TU CHOI]")

        # Lam nguoi nhiet do
        T = alpha * T

    # Kiem tra lan cuoi sau khi vong lap ket thuc
    if problem.goal_test(current_node.state):
        print(f"[Simulated Annealing] Da tim thay loi giai sau {step} buoc!")
        return path_to_solution(path), True

    print(f"[Simulated Annealing] Khong tim duoc loi giai. "
          f"(Buoc = {step}, T cuoi = {T:.6f}, h cuoi = {current_h})")
    return path_to_solution(path), False


def path_to_solution(path):
    """Chuyen danh sach Node thanh (actions, states)"""
    actions = []
    states = []
    for node in path:
        states.append(node.state)
        if node.action is not None:
            actions.append(node.action)
    return actions, states


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
    print("  GIAI 8-PUZZLE BANG SIMULATED ANNEALING")
    print("=" * 55)
    print("\nTrang thai ban dau:")
    print_state(initial)
    print("Trang thai dich:")
    print_state(goal)

    (actions, states), found = Simulated_Annealing(
        problem,
        T0=500.0,
        Tmin=0.01,
        alpha=0.9995,
        max_steps=100000
    )

    if not found:
        print(f"\nKhong tim duoc loi giai!")
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
