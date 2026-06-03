import copy
import heapq
import random
import tkinter as tk
from tkinter import ttk


class Node:
    """Nút trong cây tìm kiếm, dùng chung cho mọi thuật toán."""
    def __init__(self, state=None, parent=None, action=None, path_cost=0, depth=0):
        """Lưu trạng thái, nút cha, hành động, chi phí đường đi và độ sâu."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = depth


class Problem:
    """Mô tả bài toán 8-puzzle: trạng thái đầu, đích, và hàm chuyển trạng thái."""
    def __init__(self, initial, goal):
        """Lưu bảng trạng thái ban đầu và trạng thái đích."""
        self.initial = initial
        self.goal = goal

    def find_zero(self, board):
        """Tìm vị trí ô trống (0) và trả về (hàng, cột)."""
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    return i, j

    def actions(self, state):
        """Liệt kê các bước đi hợp lệ của ô trống ở trạng thái hiện tại."""
        i, j = self.find_zero(state)
        moves = []
        # Kiểm tra biên để không đi ra ngoài bảng 3x3.
        if j > 0:
            moves.append("Trai")
        if j < 2:
            moves.append("Phai")
        if i > 0:
            moves.append("Len")
        if i < 2:
            moves.append("Xuong")
        # Xáo trộn để tránh thiên lệch thứ tự cố định.
        random.shuffle(moves)
        return moves

    def result(self, state, action):
        """Trả về bảng mới sau khi áp dụng một hành động."""
        i, j = self.find_zero(state)
        # Tính vị trí mới của ô trống theo hành động.
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
        # Sao chép bảng và hoán đổi ô trống với ô mục tiêu.
        new_state = copy.deepcopy(state)
        new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]
        return new_state

    def goal_test(self, state):
        """Kiểm tra xem trạng thái có phải đích hay không."""
        return state == self.goal


def state_to_tuple(state):
    """Chuyển bảng list sang tuple để dùng làm khóa trong set/dict."""
    return tuple(tuple(row) for row in state)


def child_node(problem, node, action):
    """Tạo nút con bằng cách áp dụng hành động lên trạng thái của nút cha."""
    next_state = problem.result(node.state, action)
    return Node(state=next_state, parent=node, action=action, path_cost=node.path_cost + 1, depth=node.depth + 1)


def solution(node):
    """Dò ngược từ nút đích để lấy danh sách hành động và trạng thái."""
    actions, states = [], []
    while node:
        states.append(node.state)
        if node.action:
            actions.append(node.action)
        node = node.parent
    # Đảo ngược vì đang truy vết từ đích về đầu.
    return actions[::-1], states[::-1]


def manhattan_distance(state, goal):
    """Heuristic: tổng khoảng cách Manhattan của mỗi ô tới vị trí đích."""
    goal_pos = {goal[i][j]: (i, j) for i in range(3) for j in range(3)}
    return sum(abs(i - goal_pos[state[i][j]][0]) + abs(j - goal_pos[state[i][j]][1]) 
               for i in range(3) for j in range(3) if state[i][j] != 0)


def BFS(problem):
    """Tìm kiếm theo chiều rộng (BFS) kèm ghi log các bước duyệt."""
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "Start", node.state)]
    # steps: (số_bước, hành động, trạng thái) cho mọi lần mở rộng.
    steps = [(0, "Start", node.state)]
    # frontier là hàng đợi FIFO (dùng list pop(0)).
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
                # Ghi log mọi trạng thái con mới (chưa gặp).
                steps.append((step_num, action, child.state))
                step_num += 1
                if problem.goal_test(child.state):
                    # Trả về đường đi lời giải và toàn bộ log duyệt.
                    actions, states = solution(child)
                    return actions, states, steps
                frontier.append(child)
                frontier_state.add(child_tuple)
    return None, None, steps


def DFS(problem):
    """Tìm kiếm theo chiều sâu (DFS) kèm ghi log các bước duyệt."""
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "Start", node.state)]
    steps = [(0, "Start", node.state)]
    # frontier là ngăn xếp LIFO.
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
    """Uniform-Cost Search (ưu tiên theo Manhattan) kèm ghi log."""
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "Start", node.state)]
    steps = [(0, "Start", node.state)]
    frontier, explored = [], set()
    # Min-heap theo (ưu tiên, tránh trùng khóa, node).
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
    """DLS đệ quy dùng cho IDS. Ghi log mọi mở rộng hợp lệ."""
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
        # Ghi nhận mỗi lần mở rộng, dùng step_num dạng tham chiếu.
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
    """Iterative Deepening Search kèm ghi log toàn bộ duyệt."""
    start = Node(problem.initial)
    if problem.goal_test(start.state):
        return [], [start.state], [(0, "Start", start.state)]
    steps = [(0, "Start", start.state)]
    # Dùng biến đếm dạng list để cập nhật trong đệ quy.
    step_num = [1]
    for depth in range(max_depth + 1):
        result = depth_limited_search(problem, start, depth, {state_to_tuple(start.state)}, steps, step_num)
        if result != "cutoff" and result:
            actions, states = solution(result)
            return actions, states, steps
    return None, None, steps


def format_state_table(state):
    """Đổi bảng thành chuỗi nhiều dòng để hiển thị trong log."""
    return "\n".join("  ".join(" " if v == 0 else str(v) for v in row) for row in state)


class UI:
    """Giao diện Tkinter để mô phỏng và phát lại log."""
    def __init__(self, root, initial, goal):
        """Khởi tạo trạng thái và dựng toàn bộ giao diện."""
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
        """Tạo các widget và bố cục giao diện."""
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
            values=["BFS", "DFS", "UCS", "IDS"],
            state="readonly",
            width=12,
        )
        self.algo_box.grid(row=0, column=1, padx=8)
        self.algo_box.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        tk.Label(ctrl, text="Max depth:", bg="white").grid(row=0, column=2, sticky="w")
        self.depth_var = tk.StringVar(value="30")
        tk.Spinbox(ctrl, from_=1, to=100, textvariable=self.depth_var, width=6).grid(row=0, column=3, padx=8)
        tk.Button(ctrl, text="Run", command=self.run_algorithm, bg="#2563eb", fg="white", width=12).grid(row=0, column=4, sticky="e")

        tk.Label(ctrl, text="Speed (ms):", bg="white").grid(row=1, column=0, sticky="w", pady=(6, 0))
        tk.Scale(
            ctrl,
            from_=100,
            to=1500,
            orient="horizontal",
            length=200,
            variable=self.speed_var,
            bg="white",
            highlightthickness=0,
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
        """Gọi thuật toán đã chọn và trả về (actions, states, steps)."""
        p = Problem(self.initial, self.goal)
        if self.algo_var.get() == "BFS":
            return BFS(p)
        if self.algo_var.get() == "DFS":
            return DFS(p)
        if self.algo_var.get() == "UCS":
            return UCS(p)
        try:
            return IDS(p, int(self.depth_var.get()))
        except:
            return IDS(p, 30)

    def run_algorithm(self):
        """Chạy thuật toán và cập nhật log/bảng theo các bước duyệt."""
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
        """Reset giao diện khi người dùng đổi thuật toán."""
        self.auto_running = False
        self.init_empty()

    def init_empty(self):
        """Trạng thái ban đầu: hiển thị bảng start và dòng chờ lệnh."""
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

    def rebuild_log(self):
        """Dựng lại log từ self.states/self.step_actions (ít khi dùng)."""
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log_ranges = []
        for i, state in enumerate(self.states):
            start = self.log.index(tk.END)
            self.log.insert(tk.END, f"[Step {i}] {self.step_actions[i]}\n", ("header",))
            self.log.insert(tk.END, format_state_table(state) + "\n\n")
            self.log_ranges.append((start, self.log.index(tk.END)))
        self.summary.config(text=f"Total steps: {len(self.states)}")
        self.log.config(state="disabled")
        self.highlight_log()

    def display_steps(self, steps):
        """Đổ toàn bộ bước duyệt vào khung log."""
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
        """Cập nhật bảng, nhãn và trạng thái theo chỉ số hiện tại."""
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
        """Tô sáng bước hiện tại trong log."""
        if not self.log_ranges:
            return
        self.log.config(state="normal")
        self.log.tag_remove("active", "1.0", tk.END)
        s, e = self.log_ranges[self.index]
        self.log.tag_add("active", s, e)
        self.log.see(s)
        self.log.config(state="disabled")

    def on_click(self, e):
        """Nhảy tới bước được bấm trong log."""
        if not self.log_ranges:
            return
        idx = self.log.index(f"@{e.x},{e.y}")
        for i, (s, e) in enumerate(self.log_ranges):
            if self.log.compare(idx, ">=", s) and self.log.compare(idx, "<", e):
                self.index = i
                self.update()
                break

    def next(self):
        """Chuyển đến bước kế tiếp."""
        if not self.has_run:
            return
        if self.index < len(self.states) - 1:
            self.index += 1
            self.update()

    def prev(self):
        """Quay lại bước trước đó."""
        if not self.has_run:
            return
        if self.index > 0:
            self.index -= 1
            self.update()

    def reset(self):
        """Đưa playback về bước đầu."""
        self.auto_running = False
        self.index = 0
        self.update()

    def toggle(self):
        """Bật/tắt chế độ chạy tự động."""
        if not self.has_run or len(self.states) <= 1:
            return
        self.auto_running = not self.auto_running
        if self.auto_running:
            self.auto_play()

    def auto_play(self):
        """Tự động chuyển bước theo tốc độ của thanh trượt."""
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
