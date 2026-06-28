import copy
import heapq
import math
import random
import tkinter as tk
from tkinter import ttk


class Node:
    """Nút trong cây tìm kiếm, dùng chung cho mọi thuật toán."""
    def __init__(self, state=None, parent=None, action=None, path_cost=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = depth


class Problem:
    """Mô tả bài toán 8-puzzle: trạng thái đầu, đích, và hàm chuyển trạng thái."""
    def __init__(self, initial, goal):
        self.initial = initial
        self.goal = goal

    def find_zero(self, board):
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    return i, j

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


def child_node(problem, node, action):
    next_state = problem.result(node.state, action)
    return Node(state=next_state, parent=node, action=action, path_cost=node.path_cost + 1, depth=node.depth + 1)


def solution(node):
    actions, states = [], []
    while node:
        states.append(node.state)
        if node.action:
            actions.append(node.action)
        node = node.parent
    return actions[::-1], states[::-1]


def manhattan_distance(state, goal):
    """Heuristic: tổng khoảng cách Manhattan của mỗi ô tới vị trí đích."""
    goal_pos = {goal[i][j]: (i, j) for i in range(3) for j in range(3)}
    return sum(abs(i - goal_pos[state[i][j]][0]) + abs(j - goal_pos[state[i][j]][1])
               for i in range(3) for j in range(3) if state[i][j] != 0)


# ============================================================
#  CÁC THUẬT TOÁN TÌM KIẾM
# ============================================================

def BFS(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "Start", node.state)]
    steps = [(0, "Start", node.state)]
    frontier, explored = [node], set()
    frontier_state = {state_to_tuple(node.state)}
    step_num = 1
    while frontier:
        node = frontier.pop(0)
        frontier_state.discard(state_to_tuple(node.state))
        explored.add(state_to_tuple(node.state))
        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_tuple = state_to_tuple(child.state)
            if child_tuple not in explored and child_tuple not in frontier_state:
                steps.append((step_num, f"{action} (depth={child.depth})", child.state))
                step_num += 1
                if problem.goal_test(child.state):
                    actions, states = solution(child)
                    return actions, states, steps
                frontier.append(child)
                frontier_state.add(child_tuple)
    return None, None, steps


def DFS(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "Start", node.state)]
    steps = [(0, "Start", node.state)]
    frontier, explored = [node], set()
    frontier_state = {state_to_tuple(node.state)}
    step_num = 1
    while frontier:
        node = frontier.pop()
        frontier_state.discard(state_to_tuple(node.state))
        explored.add(state_to_tuple(node.state))
        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_tuple = state_to_tuple(child.state)
            if child_tuple not in explored and child_tuple not in frontier_state:
                steps.append((step_num, f"{action} (depth={child.depth})", child.state))
                step_num += 1
                if problem.goal_test(child.state):
                    actions, states = solution(child)
                    return actions, states, steps
                frontier.append(child)
                frontier_state.add(child_tuple)
    return None, None, steps


def UCS(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "Start → g=0", node.state)]
    steps = [(0, "Start → g=0", node.state)]
    frontier, explored = [], set()
    heapq.heappush(frontier, (node.path_cost, id(node), node))
    frontier_state = {state_to_tuple(node.state)}
    step_num = 1
    while frontier:
        _, _, node = heapq.heappop(frontier)
        frontier_state.discard(state_to_tuple(node.state))
        explored.add(state_to_tuple(node.state))
        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_tuple = state_to_tuple(child.state)
            if child_tuple not in explored and child_tuple not in frontier_state:
                steps.append((step_num, f"{action} → g={child.path_cost}", child.state))
                step_num += 1
                if problem.goal_test(child.state):
                    actions, states = solution(child)
                    return actions, states, steps
                heapq.heappush(frontier, (child.path_cost, id(child), child))
                frontier_state.add(child_tuple)
    return None, None, steps


def depth_limited_search(problem, node, limit, path_set, steps, step_num, current_depth_limit):
    if problem.goal_test(node.state):
        return node
    if limit == 0:
        return "cutoff"
    cutoff = False
    for action in problem.actions(node.state):
        child = child_node(problem, node, action)
        if state_to_tuple(child.state) in path_set:
            continue
        path_set.add(state_to_tuple(child.state))
        steps.append((step_num[0], f"{action} (depth={child.depth}, limit={current_depth_limit})", child.state))
        step_num[0] += 1
        result = depth_limited_search(problem, child, limit - 1, path_set, steps, step_num, current_depth_limit)
        if result == "cutoff":
            cutoff = True
        elif result:
            return result
        path_set.remove(state_to_tuple(child.state))
    return "cutoff" if cutoff else None


def IDS(problem, max_depth):
    start = Node(problem.initial)
    if problem.goal_test(start.state):
        return [], [start.state], [(0, "Start", start.state)]
    steps = [(0, "Start", start.state)]
    step_num = [1]
    for depth in range(max_depth + 1):
        steps.append((step_num[0], f"=== Giới hạn độ sâu = {depth} ===", start.state))
        step_num[0] += 1
        result = depth_limited_search(problem, start, depth, {state_to_tuple(start.state)}, steps, step_num, depth)
        if result != "cutoff" and result:
            actions, states = solution(result)
            return actions, states, steps
    return None, None, steps


def GBFS(problem):
    """
    Greedy Best-First Search (Tìm kiếm tham lam)
    Chỉ dùng h(n) = Manhattan Distance để chọn nút mở rộng.
    """
    start_node = Node(problem.initial)
    h_start = manhattan_distance(start_node.state, problem.goal)
    steps = [(0, f"Start → h={h_start}", start_node.state)]
    step_num = 1

    frontier = []
    heapq.heappush(frontier, (h_start, id(start_node), start_node))
    frontier_state = {state_to_tuple(start_node.state)}
    reached = set()

    while frontier:
        _, _, node = heapq.heappop(frontier)
        node_key = state_to_tuple(node.state)
        frontier_state.discard(node_key)

        if problem.goal_test(node.state):
            actions, states = solution(node)
            return actions, states, steps

        reached.add(node_key)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_key = state_to_tuple(child.state)

            if child_key not in frontier_state and child_key not in reached:
                h_child = manhattan_distance(child.state, problem.goal)
                steps.append((step_num, f"{action} → h={h_child}", child.state))
                step_num += 1
                heapq.heappush(frontier, (h_child, id(child), child))
                frontier_state.add(child_key)

    return None, None, steps


def A_Star(problem):
    """
    A* Search
    f(n) = g(n) + h(n)
    """
    start_node = Node(problem.initial)
    h_start = manhattan_distance(start_node.state, problem.goal)
    g_start = 0
    f_start = g_start + h_start
    steps = [(0, f"Start → f={f_start} (g={g_start}, h={h_start})", start_node.state)]
    step_num = 1

    frontier = []
    heapq.heappush(frontier, (f_start, id(start_node), start_node))
    frontier_state = {state_to_tuple(start_node.state)}
    g_score = {state_to_tuple(start_node.state): g_start}
    reached = set()

    while frontier:
        _, _, node = heapq.heappop(frontier)
        node_key = state_to_tuple(node.state)
        frontier_state.discard(node_key)

        if problem.goal_test(node.state):
            actions, states = solution(node)
            return actions, states, steps

        reached.add(node_key)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_key = state_to_tuple(child.state)
            g_new = child.path_cost

            if child_key in reached:
                if g_new >= g_score.get(child_key, float("inf")):
                    continue
                reached.discard(child_key)

            if child_key in frontier_state:
                if g_new < g_score.get(child_key, float("inf")):
                    g_score[child_key] = g_new
                    h_new = manhattan_distance(child.state, problem.goal)
                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, id(child), child))
                    steps.append((step_num, f"{action} → f={f_new} (g={g_new}, h={h_new})", child.state))
                    step_num += 1
                continue

            g_score[child_key] = g_new
            h_new = manhattan_distance(child.state, problem.goal)
            f_new = g_new + h_new
            heapq.heappush(frontier, (f_new, id(child), child))
            frontier_state.add(child_key)
            steps.append((step_num, f"{action} → f={f_new} (g={g_new}, h={h_new})", child.state))
            step_num += 1

    return None, None, steps


# ============================================================
#  THUẬT TOÁN IDA* (Iterative Deepening A*)
# ============================================================

_FOUND = "FOUND"


def _ida_search(node, g, threshold, problem, steps, step_num):
    h = manhattan_distance(node.state, problem.goal)
    f = g + h

    if f > threshold:
        return f

    if problem.goal_test(node.state):
        return _FOUND

    min_threshold = float("inf")

    for action in problem.actions(node.state):
        next_state = problem.result(node.state, action)
        child = Node(state=next_state, parent=node, action=action,
                     path_cost=node.path_cost + 1, depth=node.depth + 1)

        h_child = manhattan_distance(child.state, problem.goal)
        f_child = (g + 1) + h_child
        steps.append((step_num[0], f"{action} → f={f_child} (g={g+1}, h={h_child}) threshold={threshold}", child.state))
        step_num[0] += 1

        result = _ida_search(child, g + 1, threshold, problem, steps, step_num)

        if result == _FOUND:
            return _FOUND

        if result < min_threshold:
            min_threshold = result

    return min_threshold


def IDA_Star(problem):
    """Thuật toán IDA* (Iterative Deepening A*)."""
    start_node = Node(problem.initial)
    threshold = manhattan_distance(start_node.state, problem.goal)

    steps = [(0, f"Start → h={threshold}, threshold={threshold}", start_node.state)]
    step_num = [1]

    while True:
        result = _ida_search(start_node, 0, threshold, problem, steps, step_num)

        if result == _FOUND:
            actions, states = _ida_trace(start_node, 0, threshold, problem)
            return actions, states, steps

        if result == float("inf"):
            return None, None, steps

        threshold = result


def _ida_trace(node, g, threshold, problem):
    h = manhattan_distance(node.state, problem.goal)
    f = g + h

    if f > threshold:
        return None, None

    if problem.goal_test(node.state):
        return solution(node)

    for action in problem.actions(node.state):
        next_state = problem.result(node.state, action)
        child = Node(state=next_state, parent=node, action=action,
                     path_cost=node.path_cost + 1, depth=node.depth + 1)

        actions, states = _ida_trace(child, g + 1, threshold, problem)
        if actions is not None:
            return actions, states

    return None, None


# ============================================================
#  THUẬT TOÁN SIMPLE HILL CLIMBING
# ============================================================

def Simple_Hill_Climbing(problem):
    """
    Thuật toán Simple Hill Climbing (Leo đồi đơn giản).

    Mã giả:
    -------
    function Simple_Hill_Climbing(Start):
      1. Khởi tạo trạng thái hiện tại Current_State = Start.
      2. TRONG KHI (đúng):
         a. Sinh lần lượt các trạng thái lân cận của Current_State.
         b. Với mỗi trạng thái lân cận Next_State:
            i.  Tính giá trị đánh giá của Next_State.
            ii. NẾU Value(Next_State) > Value(Current_State):
                Current_State = Next_State. Chuyển sang lần lặp tiếp theo.
         c. NẾU không tồn tại trạng thái lân cận nào tốt hơn: Dừng.
      3. TRẢ VỀ Current_State.
    """
    current_node = Node(problem.initial)
    current_value = -manhattan_distance(current_node.state, problem.goal)

    steps = [(0, f"Start → Value={current_value}", problem.initial)]
    step_num = 1
    path = [current_node]

    while True:
        if problem.goal_test(current_node.state):
            break

        found_better = False

        for action in problem.actions(current_node.state):
            next_state = problem.result(current_node.state, action)
            next_value = -manhattan_distance(next_state, problem.goal)

            if next_value > current_value:
                steps.append((step_num, f"✅ Chọn {action} → Value={next_value}", next_state))
                step_num += 1
                next_node = Node(state=next_state, parent=current_node, action=action,
                                 path_cost=current_node.path_cost + 1,
                                 depth=current_node.depth + 1)
                current_node = next_node
                current_value = next_value
                path.append(current_node)
                found_better = True
                break
            else:
                steps.append((step_num, f"Xét {action} → Value={next_value}", next_state))
                step_num += 1

        if not found_better:
            steps.append((step_num, f"❌ Kẹt cục bộ (Value={current_value})", current_node.state))
            step_num += 1
            break

    actions_list = []
    states_list = []
    for node in path:
        states_list.append(node.state)
        if node.action is not None:
            actions_list.append(node.action)

    if problem.goal_test(current_node.state):
        return actions_list, states_list, steps
    else:
        return None, None, steps


# ============================================================
#  THUẬT TOÁN STOCHASTIC HILL CLIMBING
# ============================================================

def Stochastic_Hill_Climbing(problem):
    """
    Thuật toán Stochastic Hill Climbing (Leo đồi ngẫu nhiên).

    Mã giả:
    -------
    function Stochastic_Hill_Climbing(Start):
      1. Current_State = Start
      2. TRONG KHI (đúng):
         a. Nếu Current_State == Goal: trả về Current_State
         b. Sinh tất cả trạng thái lân cận của Current_State
         c. Better_Neighbors = {Neighbor | Value(Neighbor) > Value(Current_State)}
         d. Nếu Better_Neighbors rỗng: dừng (cực đại cục bộ)
         e. Next_State = chọn ngẫu nhiên 1 trạng thái trong Better_Neighbors
         f. Current_State = Next_State
    """
    current_node = Node(problem.initial)
    current_value = -manhattan_distance(current_node.state, problem.goal)

    steps = [(0, f"Start → Value={current_value}", problem.initial)]
    step_num = 1
    path = [current_node]

    while True:
        if problem.goal_test(current_node.state):
            break

        better_neighbors = []
        for action in problem.actions(current_node.state):
            next_state = problem.result(current_node.state, action)
            next_value = -manhattan_distance(next_state, problem.goal)

            steps.append((step_num, f"Xét {action} → Value={next_value}", next_state))
            step_num += 1

            if next_value > current_value:
                better_neighbors.append((next_value, action, next_state))

        if not better_neighbors:
            steps.append((step_num, f"❌ Kẹt cục bộ (Value={current_value})", current_node.state))
            step_num += 1
            break

        next_value, action, next_state = random.choice(better_neighbors)
        steps.append((step_num, f"✅ Chọn ngẫu nhiên {action} → Value={next_value}", next_state))
        step_num += 1

        next_node = Node(state=next_state, parent=current_node, action=action,
                         path_cost=current_node.path_cost + 1,
                         depth=current_node.depth + 1)
        current_node = next_node
        current_value = next_value
        path.append(current_node)

    actions_list = []
    states_list = []
    for node in path:
        states_list.append(node.state)
        if node.action is not None:
            actions_list.append(node.action)

    if problem.goal_test(current_node.state):
        return actions_list, states_list, steps
    else:
        return None, None, steps


# ============================================================
#  THUẬT TOÁN RANDOM RESTART HILL CLIMBING
# ============================================================

def random_state_from(problem, steps_count=20):
    """Tạo trạng thái ngẫu nhiên bằng cách thực hiện steps_count bước ngẫu nhiên từ initial."""
    current = copy.deepcopy(problem.initial)
    for _ in range(steps_count):
        action = random.choice(problem.actions(current))
        current = problem.result(current, action)
    return current


def Random_Restart_Hill_Climbing(problem, max_restart=30, random_steps=20):
    """
    Random Restart Hill Climbing cho 8-puzzle.

    Mã giả:
    -------
    function Random_Restart_Hill_Climbing(Start, max_restart):
      1. LẶP restart = 1, 2, ..., max_restart:
         a. Tạo trạng thái ngẫu nhiên Random_State từ Start
         b. Current_State = Random_State
         c. TRONG KHI (đúng):
            i.   NẾU Current_State == Goal: TRẢ VỀ lời giải
            ii.  Sinh tất cả lân cận, lọc Better_Neighbors
            iii. NẾU không có lân cận tốt hơn: BREAK (cực đại cục bộ)
            iv.  Chọn lân cận tốt nhất (ties broken randomly)
            v.   Current_State = Best_Neighbor
      2. TRẢ VỀ "Không tìm được lời giải"
    """
    all_steps = []
    step_num = 0

    for restart in range(1, max_restart + 1):
        current_state = random_state_from(problem, random_steps)
        current_node = Node(state=current_state)
        current_value = -manhattan_distance(current_node.state, problem.goal)
        path = [current_node]

        all_steps.append((step_num, f"=== Restart {restart} === Value={current_value}", current_state))
        step_num += 1

        while True:
            if problem.goal_test(current_node.state):
                actions_list = []
                states_list = []
                for node in path:
                    states_list.append(node.state)
                    if node.action is not None:
                        actions_list.append(node.action)
                return actions_list, states_list, all_steps

            better_neighbors = []
            for action in problem.actions(current_node.state):
                next_state = problem.result(current_node.state, action)
                next_value = -manhattan_distance(next_state, problem.goal)

                all_steps.append((step_num, f"Xét {action} → Value={next_value}", next_state))
                step_num += 1

                if next_value > current_value:
                    better_neighbors.append((next_value, action, next_state))

            if not better_neighbors:
                all_steps.append((step_num, f"Kẹt cục bộ (Value={current_value})", current_node.state))
                step_num += 1
                break

            best_value = max(n[0] for n in better_neighbors)
            best_candidates = [n for n in better_neighbors if n[0] == best_value]
            next_value, action, next_state = random.choice(best_candidates)

            next_node = Node(state=next_state, parent=current_node, action=action)
            current_node = next_node
            current_value = next_value
            path.append(current_node)

            all_steps.append((step_num, f"Chọn {action} → Value={current_value}", current_node.state))
            step_num += 1

    return None, None, all_steps


# ============================================================
#  THUẬT TOÁN LOCAL BEAM SEARCH
# ============================================================

def Local_Beam_Search(problem, k=3, max_iters=300, random_steps=25):
    """
    Local Beam Search (k beams) cho 8-puzzle.

    Mã giả:
    -------
    function Local_Beam_Search(Start, k, max_iters):
      1. Khởi tạo k trạng thái ngẫu nhiên từ Start
      2. LẶP iteration = 1 → max_iters:
         a. Với mỗi beam i: kiểm tra đích, sinh lân cận
         b. Gom tất cả lân cận, chọn k trạng thái tốt nhất
         c. Cập nhật k beams
      3. TRẢ VỀ "Không tìm được lời giải"
    """
    if k <= 0:
        return None, None, []

    all_steps = []
    step_num = 0

    current_nodes = []
    seen = set()
    while len(current_nodes) < k:
        state = random_state_from(problem, random_steps)
        key = state_to_tuple(state)
        if key in seen:
            continue
        seen.add(key)
        current_nodes.append(Node(state=state))

    beam_states = [n.state for n in current_nodes]
    beam_values = [-manhattan_distance(n.state, problem.goal) for n in current_nodes]
    all_steps.append((step_num, "beam_group", {
        "label": "Khởi tạo k beams",
        "beams": beam_states,
        "values": beam_values,
        "iteration": 0,
    }))
    step_num += 1

    for iteration in range(1, max_iters + 1):
        neighbors = []

        for idx, node in enumerate(current_nodes):
            if problem.goal_test(node.state):
                actions, states = solution(node)
                return actions, states, all_steps

            for action in problem.actions(node.state):
                next_state = problem.result(node.state, action)
                child = Node(state=next_state, parent=node, action=action)
                neighbors.append(child)

        for child in neighbors:
            if problem.goal_test(child.state):
                actions, states = solution(child)
                return actions, states, all_steps

        if not neighbors:
            break

        best_by_state = {}
        for child in neighbors:
            key = state_to_tuple(child.state)
            if key not in best_by_state:
                best_by_state[key] = child
            else:
                if -manhattan_distance(child.state, problem.goal) > -manhattan_distance(best_by_state[key].state, problem.goal):
                    best_by_state[key] = child

        ranked = sorted(
            best_by_state.values(),
            key=lambda n: -manhattan_distance(n.state, problem.goal),
            reverse=True,
        )
        current_nodes = ranked[:k]

        if not current_nodes:
            break

        beam_states = [n.state for n in current_nodes]
        beam_values = [-manhattan_distance(n.state, problem.goal) for n in current_nodes]
        all_steps.append((step_num, "beam_group", {
            "label": f"Iteration {iteration}",
            "beams": beam_states,
            "values": beam_values,
            "iteration": iteration,
        }))
        step_num += 1

    return None, None, all_steps


# ============================================================
#  THUẬT TOÁN SIMULATED ANNEALING  
# ============================================================

def Simulated_Annealing(problem, T0=500.0, Tmin=0.01, alpha=0.9995, max_steps=100000):
    """
    Thuật toán Simulated Annealing (Làm nguội mô phỏng) cho bài toán 8-puzzle.

    Mã giả:
    -------
    function SimulatedAnnealing(start, goal):
      current_state = start
      T = T0
      while T > Tmin:
          if current_state == goal: return current_state
          next_state = RandomNeighbor(current_state)
          delta = h(next_state) - h(current_state)
          if delta < 0:
              current = next                          # Chấp nhận – tốt hơn
          else:
              p = exp(-delta / T)
              if Random(0, 1) < p:
                  current_state = next_state          # Chấp nhận – ngẫu nhiên
          T = alpha * T
      return current_state

    Tham số:
    --------
    T0        : Nhiệt độ ban đầu   (default=500.0)
    Tmin      : Nhiệt độ dừng      (default=0.01)
    alpha     : Hệ số làm nguội    (default=0.9995)
    max_steps : Số bước tối đa     (default=100000)

    Trả về: (actions, states, steps)  tương thích với UI v5
    """
    current_node = Node(state=problem.initial)
    current_h = manhattan_distance(current_node.state, problem.goal)

    T = T0
    step_num = 0
    path = [current_node]

    # Bước 0: trạng thái ban đầu
    steps = [(step_num, f"Start → h={current_h} | T={T:.2f}", problem.initial)]
    step_num += 1

    loop_count = 0

    while T > Tmin and loop_count < max_steps:

        # Kiểm tra đích
        if problem.goal_test(current_node.state):
            break

        loop_count += 1

        # Chọn ngẫu nhiên 1 trạng thái lân cận
        avail = problem.actions(current_node.state)
        if not avail:
            break
        action = random.choice(avail)
        next_state = problem.result(current_node.state, action)
        next_h = manhattan_distance(next_state, problem.goal)

        # delta = h(next) - h(current)
        delta = next_h - current_h

        if delta < 0:
            # Chấp nhận vì tốt hơn
            label = (f"✅ {action} | h: {current_h}→{next_h} | "
                     f"Δ={delta:+d} | T={T:.4f} | [Tốt hơn]")
            next_node = Node(state=next_state, parent=current_node, action=action)
            current_node = next_node
            current_h = next_h
            path.append(current_node)
            steps.append((step_num, label, next_state))
            step_num += 1
        else:
            # Chấp nhận có xác suất
            p = math.exp(-delta / T)
            r = random.random()
            if r < p:
                label = (f"🎲 {action} | h: {current_h}→{next_h} | "
                         f"Δ={delta:+d} | T={T:.4f} | p={p:.4f} | [Ngẫu nhiên]")
                next_node = Node(state=next_state, parent=current_node, action=action)
                current_node = next_node
                current_h = next_h
                path.append(current_node)
                steps.append((step_num, label, next_state))
                step_num += 1
            else:
                label = (f"❌ {action} | h: {current_h}→{next_h} | "
                         f"Δ={delta:+d} | T={T:.4f} | p={p:.4f} | [Từ chối]")
                steps.append((step_num, label, next_state))
                step_num += 1

        # Làm nguội nhiệt độ
        T = alpha * T

    # Kiểm tra lần cuối
    found = problem.goal_test(current_node.state)

    # Xây dựng actions_list và states_list từ path
    actions_list = []
    states_list = []
    for node in path:
        states_list.append(node.state)
        if node.action is not None:
            actions_list.append(node.action)

    if found:
        return actions_list, states_list, steps
    else:
        return None, None, steps


# ============================================================
#  GIAO DIỆN
# ============================================================

def format_state_table(state):
    return "\n".join("  ".join(" " if v == 0 else str(v) for v in row) for row in state)


class UI:
    """Giao diện Tkinter để mô phỏng và phát lại log."""
    def __init__(self, root, initial, goal):
        self.root = root
        self.initial = initial
        self.goal = goal
        self.states = []
        self.step_actions = []
        self.index = 0
        self.auto_running = False
        self.log_ranges = []
        self.has_run = False
        self.solved = False
        self.solution_len = 0
        self.speed_var = tk.IntVar(value=650)
        # Cho Local Beam Search: lưu trạng thái nhóm beam
        self.beam_mode = False
        # Cho Random Restart và SA: đánh dấu thuật toán đặc biệt
        self.special_algo = None

        self.root.title("8-Puzzle v5 - Mô phỏng giải ô số")
        self.root.geometry("1220x720")
        self.root.configure(bg="#f3f4f6")

        self.setup_ui()
        self.init_empty()

    def setup_ui(self):
        tk.Label(self.root, text="MÔ PHỎNG 8-PUZZLE  [v5 + Simulated Annealing]",
                 font=("Arial", 18, "bold"), bg="#f3f4f6").pack(pady=10)

        main = tk.Frame(self.root, bg="#f3f4f6")
        main.pack(fill="both", expand=True, padx=20, pady=10)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(0, weight=1)

        left = tk.Frame(main, bg="white", relief="solid", bd=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        right = tk.Frame(main, bg="white", relief="solid", bd=1)
        right.grid(row=0, column=1, sticky="nsew")

        ctrl = tk.Frame(left, bg="white")
        ctrl.pack(fill="x", padx=10, pady=8)
        tk.Label(ctrl, text="Thuật toán:", bg="white").grid(row=0, column=0, sticky="w")

        self.algo_var = tk.StringVar(value="BFS")
        self.algo_box = ttk.Combobox(
            ctrl,
            textvariable=self.algo_var,
            values=[
                "BFS", "DFS", "UCS", "IDS", "GBFS", "A*", "IDA*",
                "Hill Climbing", "Stochastic Hill Climbing",
                "Random Restart HC", "Local Beam Search",
                "Simulated Annealing",          # ← MỚI
            ],
            state="readonly",
            width=22,
        )
        self.algo_box.grid(row=0, column=1, padx=8)
        self.algo_box.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        tk.Label(ctrl, text="Độ sâu tối đa:", bg="white").grid(row=0, column=2, sticky="w")
        self.depth_var = tk.StringVar(value="30")
        tk.Spinbox(ctrl, from_=1, to=100, textvariable=self.depth_var, width=6).grid(row=0, column=3, padx=8)
        tk.Button(ctrl, text="Chạy", command=self.run_algorithm,
                  bg="#2563eb", fg="white", width=12).grid(row=0, column=4, sticky="e")

        tk.Label(ctrl, text="Số lần restart:", bg="white").grid(row=0, column=5, sticky="w", padx=(8, 0))
        self.restart_var = tk.StringVar(value="50")
        tk.Spinbox(ctrl, from_=1, to=200, textvariable=self.restart_var, width=6).grid(row=0, column=6, padx=4)

        # ---- Hàng 2: Tốc độ + tham số SA ----
        tk.Label(ctrl, text="Tốc độ (ms):", bg="white").grid(row=1, column=0, sticky="w", pady=(6, 0))
        tk.Scale(
            ctrl, from_=100, to=1500, orient="horizontal", length=200,
            variable=self.speed_var, bg="white", highlightthickness=0,
        ).grid(row=1, column=1, columnspan=2, sticky="w", pady=(6, 0))

        tk.Label(ctrl, text="SA – T₀:", bg="white").grid(row=1, column=3, sticky="w", padx=(8, 0))
        self.sa_t0_var = tk.StringVar(value="500")
        tk.Entry(ctrl, textvariable=self.sa_t0_var, width=6).grid(row=1, column=4, padx=4)

        tk.Label(ctrl, text="α:", bg="white").grid(row=1, column=5, sticky="w")
        self.sa_alpha_var = tk.StringVar(value="0.9995")
        tk.Entry(ctrl, textvariable=self.sa_alpha_var, width=8).grid(row=1, column=6, padx=4)

        self.status = tk.Label(left, text="", font=("Arial", 11, "bold"), bg="white", fg="#1f2937")
        self.status.pack(pady=8)

        self.board_frame = tk.Frame(left, bg="white")
        self.board_frame.pack(pady=10)

        self.cells = [[tk.Label(self.board_frame, text="", width=5, height=2, font=("Arial", 24, "bold"),
                                bg="#e5e7eb", fg="#111827", relief="solid", bd=1)
                       for j in range(3)] for i in range(3)]
        for i in range(3):
            for j in range(3):
                self.cells[i][j].grid(row=i, column=j, padx=4, pady=4)

        info = tk.Frame(left, bg="white")
        info.pack(pady=8)
        self.step_label = tk.Label(info, text="", font=("Arial", 10), bg="white")
        self.step_label.pack()
        self.action_label = tk.Label(info, text="", font=("Arial", 10, "bold"), bg="white", fg="#1f2937")
        self.action_label.pack(pady=4)

        btn = tk.Frame(left, bg="white")
        btn.pack(pady=8)
        for idx, (text, cmd, color) in enumerate([
            ("Trước", self.prev, "#64748b"), ("Tiếp", self.next, "#2563eb"),
            ("Tự động", self.toggle, "#16a34a"), ("Đặt lại", self.reset, "#dc2626")
        ]):
            tk.Button(btn, text=text, command=cmd, bg=color, fg="white", width=10).grid(row=0, column=idx, padx=4)

        tk.Label(right, text="NHẬT KÝ", font=("Arial", 13, "bold"), bg="white").pack(pady=8)
        self.summary = tk.Label(right, text="", font=("Arial", 10, "bold"), bg="white")
        self.summary.pack(pady=4)

        log_f = tk.Frame(right, bg="white")
        log_f.pack(padx=8, pady=8, fill="both", expand=True)
        log_f.grid_rowconfigure(0, weight=1)
        log_f.grid_columnconfigure(0, weight=1)

        self.log = tk.Text(log_f, wrap="none", bg="white", fg="#111827", font=("Consolas", 9), relief="flat")
        self.log.grid(row=0, column=0, sticky="nsew")

        sy = ttk.Scrollbar(log_f, orient="vertical", command=self.log.yview)
        sx = ttk.Scrollbar(log_f, orient="horizontal", command=self.log.xview)
        self.log.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

        self.log.tag_configure("header",        foreground="#1f2937")
        self.log.tag_configure("active",        background="#e5e7eb")
        self.log.tag_configure("restart_header",foreground="#dc2626", font=("Consolas", 10, "bold"))
        self.log.tag_configure("beam_header",   foreground="#2563eb", font=("Consolas", 10, "bold"))
        self.log.tag_configure("sa_header",     foreground="#7c3aed", font=("Consolas", 10, "bold"))  # SA màu tím
        self.log.tag_configure("sa_accept",     foreground="#16a34a")   # xanh lá – chấp nhận tốt hơn
        self.log.tag_configure("sa_random",     foreground="#d97706")   # cam – chấp nhận ngẫu nhiên
        self.log.tag_configure("sa_reject",     foreground="#dc2626")   # đỏ – từ chối
        self.log.tag_configure("value_tag",     foreground="#16a34a")
        self.log.bind("<ButtonRelease-1>", lambda e: self.on_click(e))

    # ----------------------------------------------------------
    #  ĐIỀU PHỐI CHẠY THUẬT TOÁN
    # ----------------------------------------------------------

    def solve(self):
        p = Problem(self.initial, self.goal)
        algo = self.algo_var.get()
        if algo == "BFS":
            return BFS(p)
        if algo == "DFS":
            return DFS(p)
        if algo == "UCS":
            return UCS(p)
        if algo == "GBFS":
            return GBFS(p)
        if algo == "A*":
            return A_Star(p)
        if algo == "IDA*":
            return IDA_Star(p)
        if algo == "Hill Climbing":
            return Simple_Hill_Climbing(p)
        if algo == "Stochastic Hill Climbing":
            return Stochastic_Hill_Climbing(p)
        if algo == "Random Restart HC":
            return Random_Restart_Hill_Climbing(p, max_restart=50, random_steps=25)
        if algo == "Local Beam Search":
            return Local_Beam_Search(p, k=3, max_iters=300, random_steps=25)
        # IDS
        try:
            return IDS(p, int(self.depth_var.get()))
        except Exception:
            return IDS(p, 30)

    def run_algorithm(self):
        self.auto_running = False
        self.has_run = True
        algo = self.algo_var.get()

        if algo == "Local Beam Search":
            self._run_beam_search()
            return
        if algo == "Random Restart HC":
            self._run_random_restart()
            return
        if algo == "Simulated Annealing":
            self._run_simulated_annealing()
            return

        # Các thuật toán thông thường
        self.beam_mode = False
        self.special_algo = None
        actions, states, steps = self.solve()
        if not steps:
            steps = [(0, "Start", self.initial)]
        self.solved = bool(actions and states)
        self.solution_len = len(actions) if actions else 0
        self.states = [state for _, _, state in steps]
        self.step_actions = [action for _, action, _ in steps]
        self.index = 0
        self.display_steps(steps)
        self.update()

    # ----------------------------------------------------------
    #  SIMULATED ANNEALING – Runner & Display  (MỚI)
    # ----------------------------------------------------------

    def _run_simulated_annealing(self):
        """Chạy Simulated Annealing và hiển thị từng bước duyệt lên log."""
        self.beam_mode = False
        self.special_algo = "Simulated Annealing"

        p = Problem(self.initial, self.goal)

        try:
            t0 = float(self.sa_t0_var.get())
        except ValueError:
            t0 = 500.0
        try:
            alpha = float(self.sa_alpha_var.get())
        except ValueError:
            alpha = 0.9995

        actions, states_sol, all_steps = Simulated_Annealing(
            p, T0=t0, Tmin=0.01, alpha=alpha, max_steps=100000
        )

        self.solved = bool(actions and states_sol)
        self.solution_len = len(actions) if actions else 0

        # all_steps dạng (num, label, state)
        self.states = [state for _, _, state in all_steps]
        self.step_actions = [label for _, label, _ in all_steps]
        self.index = 0

        self._display_sa_steps(all_steps)
        self.update()

    def _display_sa_steps(self, all_steps):
        """Hiển thị log Simulated Annealing với màu sắc phân biệt từng loại bước."""
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log_ranges = []

        # Header
        self.log.insert(tk.END, "=" * 55 + "\n", ("sa_header",))
        self.log.insert(tk.END, "  SIMULATED ANNEALING – Nhật ký từng bước\n", ("sa_header",))
        self.log.insert(tk.END, "  ✅ Tốt hơn   🎲 Ngẫu nhiên   ❌ Từ chối\n", ("sa_header",))
        self.log.insert(tk.END, "=" * 55 + "\n\n", ("sa_header",))

        for num, label, state in all_steps:
            start = self.log.index(tk.END)

            # Chọn màu tag theo loại bước
            if "Tốt hơn" in label or label.startswith("Start"):
                tag = "sa_accept"
            elif "Ngẫu nhiên" in label:
                tag = "sa_random"
            elif "Từ chối" in label:
                tag = "sa_reject"
            else:
                tag = "header"

            self.log.insert(tk.END, f"[{num:>5}] {label}\n", (tag,))
            self.log.insert(tk.END, format_state_table(state) + "\n\n")

            self.log_ranges.append((start, self.log.index(tk.END)))

        # Tóm tắt
        if self.solved:
            summary = (f"Tổng duyệt: {len(all_steps)} bước → "
                       f"Lời giải: {self.solution_len} bước")
            self.summary.config(text=summary, fg="#16a34a")
        else:
            summary = f"Tổng duyệt: {len(all_steps)} bước → Không tìm được lời giải"
            self.summary.config(text=summary, fg="#dc2626")
            self.log.insert(tk.END, "\n❌ KHÔNG CÓ LỜI GIẢI\n", ("sa_reject",))

        self.log.config(state="disabled")

    # ----------------------------------------------------------
    #  LOCAL BEAM SEARCH – Runner & Display
    # ----------------------------------------------------------

    def _run_beam_search(self):
        self.beam_mode = True
        self.special_algo = "Local Beam Search"

        p = Problem(self.initial, self.goal)
        actions, states, all_steps = Local_Beam_Search(p, k=3, max_iters=300, random_steps=25)

        self.solved = bool(actions and states)
        self.solution_len = len(actions) if actions else 0

        self.states = []
        self.step_actions = []
        self._beam_data = []

        for num, action_type, data in all_steps:
            if action_type == "beam_group":
                self.states.append(data["beams"][0])
                self.step_actions.append(data["label"])
                self._beam_data.append(data)
            else:
                self.states.append(data if isinstance(data, list) else self.initial)
                self.step_actions.append(str(action_type))
                self._beam_data.append(None)

        if not self.states:
            self.states = [self.initial]
            self.step_actions = ["Start"]
            self._beam_data = [None]

        self.index = 0
        self._display_beam_steps(all_steps)
        self.update()

    def _display_beam_steps(self, all_steps):
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log_ranges = []

        for num, action_type, data in all_steps:
            if action_type != "beam_group":
                continue

            start = self.log.index(tk.END)

            label = data["label"]
            beams = data["beams"]
            values = data["values"]

            self.log.insert(tk.END, f"{'='*50}\n", ("beam_header",))
            self.log.insert(tk.END, f"  {label}\n", ("beam_header",))
            self.log.insert(tk.END, f"{'='*50}\n", ("beam_header",))

            for beam_idx in range(len(beams)):
                v = values[beam_idx]
                self.log.insert(tk.END, f"  Beam {beam_idx + 1}", ("header",))
                self.log.insert(tk.END, f"  (Value = {v})\n", ("value_tag",))
                for line in format_state_table(beams[beam_idx]).split("\n"):
                    self.log.insert(tk.END, f"    {line}\n")
                self.log.insert(tk.END, "\n")

            self.log_ranges.append((start, self.log.index(tk.END)))

        if self.solved:
            self.summary.config(text=f"Tổng iterations: {len(self.log_ranges)} → Lời giải: {self.solution_len} bước")
        else:
            self.summary.config(text=f"Tổng iterations: {len(self.log_ranges)} → Không có lời giải")
            self.log.insert(tk.END, "KHÔNG CÓ LỜI GIẢI\n", ("header",))
        self.log.config(state="disabled")

    # ----------------------------------------------------------
    #  RANDOM RESTART – Runner & Display
    # ----------------------------------------------------------

    def _run_random_restart(self):
        self.beam_mode = False
        self.special_algo = "Random Restart HC"

        p = Problem(self.initial, self.goal)
        try:
            max_r = int(self.restart_var.get())
        except ValueError:
            max_r = 50
        actions, states_sol, all_steps = Random_Restart_Hill_Climbing(p, max_restart=max_r, random_steps=25)

        self.solved = bool(actions and states_sol)
        self.solution_len = len(actions) if actions else 0

        self.states = [state for _, _, state in all_steps]
        self.step_actions = [label for _, label, _ in all_steps]
        self.index = 0
        self._display_restart_steps(all_steps)
        self.update()

    def _display_restart_steps(self, all_steps):
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log_ranges = []

        for num, label, state in all_steps:
            start = self.log.index(tk.END)

            if "=== Restart" in label:
                self.log.insert(tk.END, f"\n{'='*50}\n", ("restart_header",))
                self.log.insert(tk.END, f"  {label}\n", ("restart_header",))
                self.log.insert(tk.END, f"{'='*50}\n", ("restart_header",))
                self.log.insert(tk.END, format_state_table(state) + "\n\n")
            elif "Kẹt cục bộ" in label:
                self.log.insert(tk.END, f"[Bước {num}] ❌ {label}\n", ("header",))
                self.log.insert(tk.END, format_state_table(state) + "\n\n")
            elif "Chọn" in label:
                self.log.insert(tk.END, f"[Bước {num}] ✅ {label}\n", ("header",))
                self.log.insert(tk.END, format_state_table(state) + "\n\n")
            elif "Xét" in label:
                self.log.insert(tk.END, f"[Bước {num}] {label}\n", ("header",))
                self.log.insert(tk.END, format_state_table(state) + "\n\n")
            else:
                self.log.insert(tk.END, f"[Bước {num}] {label}\n", ("header",))
                self.log.insert(tk.END, format_state_table(state) + "\n\n")

            self.log_ranges.append((start, self.log.index(tk.END)))

        if self.solved:
            self.summary.config(text=f"Tổng duyệt: {len(all_steps)} bước → Lời giải: {self.solution_len} bước")
        else:
            self.summary.config(text=f"Tổng duyệt: {len(all_steps)} bước → Không có lời giải")
            self.log.insert(tk.END, "\nKHÔNG CÓ LỜI GIẢI\n", ("header",))
        self.log.config(state="disabled")

    # ----------------------------------------------------------
    #  HIỂN THỊ BÌNH THƯỜNG
    # ----------------------------------------------------------

    def on_algorithm_change(self, _event):
        self.auto_running = False
        self.init_empty()

    def init_empty(self):
        self.has_run = False
        self.solved = False
        self.solution_len = 0
        self.beam_mode = False
        self.special_algo = None
        self.states = [self.initial]
        self.step_actions = ["Bắt đầu"]
        self.index = 0
        self.status.config(text="Chờ lệnh")
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, "[Bắt đầu]\n", ("header",))
        self.log.insert(tk.END, format_state_table(self.initial) + "\n\n")
        self.log.insert(tk.END, "[Chờ chạy thuật toán]", ("header",))
        self.log.config(state="disabled")
        self.log_ranges = []
        self.summary.config(text="")
        for i in range(3):
            for j in range(3):
                v = self.initial[i][j]
                self.cells[i][j].config(text="" if v == 0 else str(v))
        self.step_label.config(text="Bước: 0/0")
        self.action_label.config(text="Trạng thái ban đầu")

    def display_steps(self, steps):
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log_ranges = []
        for num, action, state in steps:
            start = self.log.index(tk.END)
            self.log.insert(tk.END, f"[Bước {num}] {action}\n", ("header",))
            self.log.insert(tk.END, format_state_table(state) + "\n\n")
            self.log_ranges.append((start, self.log.index(tk.END)))
        if self.solved:
            self.summary.config(text=f"Tổng duyệt: {len(steps)} bước → Lời giải: {self.solution_len} bước")
        else:
            self.summary.config(text=f"Tổng duyệt: {len(steps)} bước → Không có lời giải")
            self.log.insert(tk.END, "KHÔNG CÓ LỜI GIẢI", ("header",))
        self.log.config(state="disabled")

    def update(self):
        s = self.states[self.index]
        for i in range(3):
            for j in range(3):
                v = s[i][j]
                self.cells[i][j].config(text="" if v == 0 else str(v), bg="#cbd5e1" if v == 0 else "#e5e7eb")
        self.step_label.config(text=f"Bước: {self.index}/{len(self.states)-1}")
        if not self.has_run:
            self.action_label.config(text="Trạng thái ban đầu")
            self.status.config(text="Chờ lệnh")
            return
        if self.index == 0:
            self.action_label.config(text="Trạng thái ban đầu")
        else:
            self.action_label.config(text=f"Hành động: {self.step_actions[self.index]}")
        if self.solved:
            self.status.config(text=f"Đang chạy {self.algo_var.get()}")
        else:
            self.status.config(text="Không có lời giải")
        if self.solved and self.index == len(self.states) - 1:
            self.status.config(text="ĐÃ ĐẠT TRẠNG THÁI ĐÍCH")
        self.highlight_log()

    def highlight_log(self):
        if not self.log_ranges:
            return
        self.log.config(state="normal")
        self.log.tag_remove("active", "1.0", tk.END)
        if self.index < len(self.log_ranges):
            s, e = self.log_ranges[self.index]
            self.log.tag_add("active", s, e)
            self.log.see(s)
        self.log.config(state="disabled")

    def on_click(self, e):
        if not self.log_ranges:
            return
        idx = self.log.index(f"@{e.x},{e.y}")
        for i, (s, e) in enumerate(self.log_ranges):
            if self.log.compare(idx, ">=", s) and self.log.compare(idx, "<", e):
                self.index = i
                self.update()
                break

    def next(self):
        if not self.has_run:
            return
        if self.index < len(self.states) - 1:
            self.index += 1
            self.update()

    def prev(self):
        if not self.has_run:
            return
        if self.index > 0:
            self.index -= 1
            self.update()

    def reset(self):
        self.auto_running = False
        self.index = 0
        self.update()

    def toggle(self):
        if not self.has_run or len(self.states) <= 1:
            return
        self.auto_running = not self.auto_running
        if self.auto_running:
            self.auto_play()

    def auto_play(self):
        if self.auto_running and self.index < len(self.states) - 1:
            self.index += 1
            self.update()
            self.root.after(self.speed_var.get(), self.auto_play)
        else:
            self.auto_running = False


if __name__ == "__main__":
    root = tk.Tk()
    initial = [
        [2, 8, 3],
        [1, 6, 4],
        [7, 0, 5],
    ]
    goal = [
        [1, 2, 3],
        [8, 0, 4],
        [7, 6, 5],
    ]
    app = UI(root, initial, goal)
    root.mainloop()
