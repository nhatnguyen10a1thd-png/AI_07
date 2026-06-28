import copy
import heapq
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
                steps.append((step_num, action, child.state))
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
                steps.append((step_num, action, child.state))
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
        return [], [node.state], [(0, "Start", node.state)]
    steps = [(0, "Start", node.state)]
    frontier, explored = [], set()
    heapq.heappush(frontier, (manhattan_distance(node.state, problem.goal), id(node), node))
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
                steps.append((step_num, action, child.state))
                step_num += 1
                if problem.goal_test(child.state):
                    actions, states = solution(child)
                    return actions, states, steps
                heapq.heappush(frontier, (manhattan_distance(child.state, problem.goal), id(child), child))
                frontier_state.add(child_tuple)
    return None, None, steps


def depth_limited_search(problem, node, limit, path_set, steps, step_num):
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
        steps.append((step_num[0], action, child.state))
        step_num[0] += 1
        result = depth_limited_search(problem, child, limit - 1, path_set, steps, step_num)
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
        result = depth_limited_search(problem, start, depth, {state_to_tuple(start.state)}, steps, step_num)
        if result != "cutoff" and result:
            actions, states = solution(result)
            return actions, states, steps
    return None, None, steps


def GBFS(problem):
    """
    Greedy Best-First Search (Tìm kiếm tham lam)
    Chỉ dùng h(n) = Manhattan Distance để chọn nút mở rộng.
    
    Flow theo slide:
    1. Khởi tạo FRONTIER = {Start}, tính h(Start)
    2. Khởi tạo REACHED = {}
    3. TRONG KHI (FRONTIER không rỗng):
       a. Chọn trạng thái n từ FRONTIER có h(n) nhỏ nhất
       b. NẾU n == Goal: Trả về "Thành công"
       c. Loại bỏ n khỏi FRONTIER, thêm n vào REACHED
       d. Với mỗi trạng thái m kề với n:
          i.  NẾU m chưa có trong FRONTIER và REACHED → thêm m vào FRONTIER
          ii. NẾU m đã có → Bỏ qua
    4. Trả về "Thất bại"
    """
    start_node = Node(problem.initial)
    steps = [(0, "Start", start_node.state)]
    step_num = 1

    # Bước 1: Khởi tạo FRONTIER = {Start}, tính h(Start)
    frontier = []
    h_start = manhattan_distance(start_node.state, problem.goal)
    heapq.heappush(frontier, (h_start, id(start_node), start_node))
    frontier_state = {state_to_tuple(start_node.state)}

    # Bước 2: Khởi tạo REACHED = {}
    reached = set()

    # Bước 3: TRONG KHI (FRONTIER không rỗng)
    while frontier:
        # a. Chọn trạng thái n từ FRONTIER có h(n) nhỏ nhất
        _, _, node = heapq.heappop(frontier)
        node_key = state_to_tuple(node.state)
        frontier_state.discard(node_key)

        # b. NẾU n == Goal
        if problem.goal_test(node.state):
            actions, states = solution(node)
            return actions, states, steps

        # c. Loại bỏ n khỏi FRONTIER, thêm n vào REACHED
        reached.add(node_key)

        # d. Với mỗi trạng thái m kề với n
        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_key = state_to_tuple(child.state)

            # i. NẾU m chưa có trong cả FRONTIER và REACHED
            if child_key not in frontier_state and child_key not in reached:
                steps.append((step_num, action, child.state))
                step_num += 1
                # Tính h(m) và thêm m vào FRONTIER
                h_child = manhattan_distance(child.state, problem.goal)
                heapq.heappush(frontier, (h_child, id(child), child))
                frontier_state.add(child_key)
            # ii. NẾU m đã có trong FRONTIER hoặc REACHED: Bỏ qua m

    # Bước 4: Trả về "Thất bại"
    return None, None, steps


def A_Star(problem):
    """
    A* Search
    f(n) = g(n) + h(n)
    g(n) = chi phí đường đi từ Start đến n (path_cost)
    h(n) = Manhattan Distance (heuristic)
    """
    start_node = Node(problem.initial)
    steps = [(0, "Start", start_node.state)]
    step_num = 1

    frontier = []
    h_start = manhattan_distance(start_node.state, problem.goal)
    g_start = 0  # chi phí đường đi ban đầu = 0
    f_start = g_start + h_start
    heapq.heappush(frontier, (f_start, id(start_node), start_node))
    frontier_state = {state_to_tuple(start_node.state)}

    # g_score lưu chi phí g(n) tốt nhất đã biết cho mỗi trạng thái
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
            g_new = child.path_cost  # g(n) = chi phí đường đi thực tế

            if child_key in reached:
                # Nếu đã duyệt và chi phí mới không tốt hơn → bỏ qua
                if g_new >= g_score.get(child_key, float("inf")):
                    continue
                # Chi phí mới tốt hơn → mở lại
                reached.discard(child_key)

            if child_key in frontier_state:
                # Nếu đã trong FRONTIER và chi phí mới tốt hơn → cập nhật
                if g_new < g_score.get(child_key, float("inf")):
                    g_score[child_key] = g_new
                    h_new = manhattan_distance(child.state, problem.goal)
                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, id(child), child))
                    steps.append((step_num, action, child.state))
                    step_num += 1
                continue

            # Trạng thái mới hoàn toàn
            g_score[child_key] = g_new
            h_new = manhattan_distance(child.state, problem.goal)
            f_new = g_new + h_new
            heapq.heappush(frontier, (f_new, id(child), child))
            frontier_state.add(child_key)
            steps.append((step_num, action, child.state))
            step_num += 1

    return None, None, steps


# ============================================================
#  THUẬT TOÁN IDA* (Iterative Deepening A*)
# ============================================================

_FOUND = "FOUND"


def _ida_search(node, g, threshold, problem, steps, step_num):
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
        return f

    if problem.goal_test(node.state):
        return _FOUND

    min_threshold = float("inf")

    for action in problem.actions(node.state):
        next_state = problem.result(node.state, action)
        child = Node(state=next_state, parent=node, action=action,
                     path_cost=node.path_cost + 1, depth=node.depth + 1)

        steps.append((step_num[0], action, child.state))
        step_num[0] += 1

        result = _ida_search(child, g + 1, threshold, problem, steps, step_num)

        if result == _FOUND:
            return _FOUND

        if result < min_threshold:
            min_threshold = result

    return min_threshold


def IDA_Star(problem):
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

    steps = [(0, "Start", start_node.state)]
    step_num = [1]

    while True:
        result = _ida_search(start_node, 0, threshold, problem, steps, step_num)

        if result == _FOUND:
            # Truy vết lời giải từ DFS
            actions, states = _ida_trace(start_node, 0, threshold, problem)
            return actions, states, steps

        if result == float("inf"):
            return None, None, steps

        threshold = result


def _ida_trace(node, g, threshold, problem):
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
         Tính giá trị đánh giá của Current_State.
      2. TRONG KHI (đúng):
         a. Sinh lần lượt các trạng thái lân cận của Current_State.
         b. Với mỗi trạng thái lân cận Next_State:
            i.  Tính giá trị đánh giá của Next_State.
            ii. NẾU Value(Next_State) > Value(Current_State):
                Current_State = Next_State.
                Chuyển sang lần lặp tiếp theo.
         c. NẾU không tồn tại trạng thái lân cận nào tốt hơn:
            Dừng vì đã đạt cực đại cục bộ.
      3. TRẢ VỀ Current_State.

    Lưu ý:
    - Value(state) = -manhattan_distance(state, goal)
      (Value càng CAO thì càng GẦN đích)
    - Simple Hill Climbing KHÔNG đảm bảo tìm được lời giải tối ưu.
    - Có thể bị kẹt tại cực đại cục bộ (local maximum).
    """

    steps = [(0, "Start", problem.initial)]
    step_num = 1

    # Bước 1: Khởi tạo Current_State = Start
    current_node = Node(problem.initial)
    current_value = -manhattan_distance(current_node.state, problem.goal)

    path = [current_node]

    # Bước 2: TRONG KHI (đúng)
    while True:
        # Kiểm tra đã đạt đích chưa
        if problem.goal_test(current_node.state):
            break

        found_better = False

        # a. Sinh lần lượt các trạng thái lân cận
        for action in problem.actions(current_node.state):
            next_state = problem.result(current_node.state, action)
            next_value = -manhattan_distance(next_state, problem.goal)

            steps.append((step_num, action, next_state))
            step_num += 1

            # ii. NẾU Value(Next_State) > Value(Current_State)
            if next_value > current_value:
                next_node = Node(state=next_state, parent=current_node, action=action,
                                 path_cost=current_node.path_cost + 1,
                                 depth=current_node.depth + 1)
                current_node = next_node
                current_value = next_value
                path.append(current_node)
                found_better = True
                # Chuyển sang lần lặp tiếp theo
                break

        # c. NẾU không tồn tại trạng thái lân cận nào tốt hơn → Dừng
        if not found_better:
            break

    # Bước 3: TRẢ VỀ Current_State
    # Truy vết đường đi
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

    steps = [(0, "Start", problem.initial)]
    step_num = 1

    current_node = Node(problem.initial)
    current_value = -manhattan_distance(current_node.state, problem.goal)
    path = [current_node]

    while True:
        if problem.goal_test(current_node.state):
            break

        better_neighbors = []
        for action in problem.actions(current_node.state):
            next_state = problem.result(current_node.state, action)
            next_value = -manhattan_distance(next_state, problem.goal)

            steps.append((step_num, action, next_state))
            step_num += 1

            if next_value > current_value:
                better_neighbors.append((next_value, action, next_state))

        if not better_neighbors:
            break

        next_value, action, next_state = random.choice(better_neighbors)
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

        self.root.title("8-Puzzle Solver")
        self.root.geometry("1220x720")
        self.root.configure(bg="#f3f4f6")

        self.setup_ui()
        self.init_empty()

    def setup_ui(self):
        tk.Label(self.root, text="8-PUZZLE SIMULATOR", font=("Arial", 18, "bold"), bg="#f3f4f6").pack(pady=10)

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
            values=["BFS", "DFS", "UCS", "IDS", "GBFS", "A*", "IDA*", "Hill Climbing", "Stochastic Hill Climbing"],
            state="readonly",
            width=14,
        )
        self.algo_box.grid(row=0, column=1, padx=8)
        self.algo_box.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        tk.Label(ctrl, text="Max depth:", bg="white").grid(row=0, column=2, sticky="w")
        self.depth_var = tk.StringVar(value="30")
        tk.Spinbox(ctrl, from_=1, to=100, textvariable=self.depth_var, width=6).grid(row=0, column=3, padx=8)
        tk.Button(ctrl, text="Run", command=self.run_algorithm, bg="#2563eb", fg="white", width=12).grid(row=0, column=4, sticky="e")

        tk.Label(ctrl, text="Speed (ms):", bg="white").grid(row=1, column=0, sticky="w", pady=(6, 0))
        tk.Scale(
            ctrl, from_=100, to=1500, orient="horizontal", length=200,
            variable=self.speed_var, bg="white", highlightthickness=0,
        ).grid(row=1, column=1, columnspan=2, sticky="w", pady=(6, 0))

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
        for idx, (text, cmd, color) in enumerate([("Prev", self.prev, "#64748b"), ("Next", self.next, "#2563eb"),
                                                    ("Auto", self.toggle, "#16a34a"), ("Reset", self.reset, "#dc2626")]):
            tk.Button(btn, text=text, command=cmd, bg=color, fg="white", width=10).grid(row=0, column=idx, padx=4)

        tk.Label(right, text="LOG", font=("Arial", 13, "bold"), bg="white").pack(pady=8)
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

        self.log.tag_configure("header", foreground="#1f2937")
        self.log.tag_configure("active", background="#e5e7eb")
        self.log.bind("<ButtonRelease-1>", lambda e: self.on_click(e))

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
        # IDS
        try:
            return IDS(p, int(self.depth_var.get()))
        except:
            return IDS(p, 30)

    def run_algorithm(self):
        self.auto_running = False
        self.has_run = True
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

    def on_algorithm_change(self, _event):
        self.auto_running = False
        self.init_empty()

    def init_empty(self):
        self.has_run = False
        self.solved = False
        self.solution_len = 0
        self.states = [self.initial]
        self.step_actions = ["Start"]
        self.index = 0
        self.status.config(text="Chờ lệnh")
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, "[Start]\n", ("header",))
        self.log.insert(tk.END, format_state_table(self.initial) + "\n\n")
        self.log.insert(tk.END, "[Waiting for input]", ("header",))
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
