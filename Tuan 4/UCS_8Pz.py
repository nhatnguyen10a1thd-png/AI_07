import heapq
import copy
import random
import tkinter as tk
from tkinter import ttk


class Node:
    def __init__(self, state=None, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost


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
    """Tính Manhattan Distance từ state đến goal"""
    distance = 0
    
    # Tạo từ điển chứa vị trí mục tiêu của từng tile
    goal_pos = {}
    for i in range(3):
        for j in range(3):
            goal_pos[goal[i][j]] = (i, j)
    
    # Tính tổng khoảng cách Manhattan
    for i in range(3):
        for j in range(3):
            tile = state[i][j]
            if tile != 0:  # Bỏ qua ô trống
                goal_i, goal_j = goal_pos[tile]
                distance += abs(i - goal_i) + abs(j - goal_j)
    
    return distance


def child_node(problem, node, action):
    next_state = problem.result(node.state, action)

    return Node(
        state=next_state,
        parent=node,
        action=action,
        path_cost=node.path_cost + 1
    )


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


def UCS(problem):
    """Uniform Cost Search với priority là Manhattan Distance"""
    node = Node(problem.initial)

    if problem.goal_test(node.state):
        return [], [node.state]

    frontier = []
    # Priority = Manhattan Distance (càng nhỏ = priority cao = được xử lý trước)
    priority = manhattan_distance(node.state, problem.goal)
    heapq.heappush(frontier, (priority, id(node), node))

    explored = set()
    frontier_state = {state_to_tuple(node.state)}

    while frontier:
        _, _, node = heapq.heappop(frontier)
        frontier_state.discard(state_to_tuple(node.state))

        explored.add(state_to_tuple(node.state))

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_tuple = state_to_tuple(child.state)

            if child_tuple not in explored and child_tuple not in frontier_state:
                if problem.goal_test(child.state):
                    return solution(child)

                priority = manhattan_distance(child.state, problem.goal)
                heapq.heappush(frontier, (priority, id(child), child))
                frontier_state.add(child_tuple)

    return None, None


class PuzzleUI:
    def __init__(self, root, actions, states):
        self.root = root
        self.actions = actions
        self.states = states
        self.index = 0
        self.auto_running = False

        self.root.title("8 Puzzle UCS Agent Visualizer")
        self.root.geometry("950x600")
        self.root.configure(bg="#111827")

        self.create_layout()
        self.update_board()

    def create_layout(self):
        title = tk.Label(
            self.root,
            text="8 PUZZLE UCS AGENT",
            font=("Segoe UI", 24, "bold"),
            fg="#38bdf8",
            bg="#111827"
        )
        title.pack(pady=15)

        main_frame = tk.Frame(self.root, bg="#111827")
        main_frame.pack(fill="both", expand=True, padx=25, pady=10)

        left_frame = tk.Frame(main_frame, bg="#1f2937", bd=0)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        right_frame = tk.Frame(main_frame, bg="#0f172a", bd=0)
        right_frame.pack(side="right", fill="y")

        self.status_label = tk.Label(
            left_frame,
            text="",
            font=("Segoe UI", 14, "bold"),
            fg="#facc15",
            bg="#1f2937"
        )
        self.status_label.pack(pady=15)

        self.board_frame = tk.Frame(left_frame, bg="#1f2937")
        self.board_frame.pack(pady=20)

        self.cells = []

        for i in range(3):
            row = []
            for j in range(3):
                cell = tk.Label(
                    self.board_frame,
                    text="",
                    width=5,
                    height=2,
                    font=("Segoe UI", 30, "bold"),
                    bg="#334155",
                    fg="white",
                    relief="flat"
                )
                cell.grid(row=i, column=j, padx=8, pady=8)
                row.append(cell)
            self.cells.append(row)

        info_frame = tk.Frame(left_frame, bg="#1f2937")
        info_frame.pack(pady=20)

        self.step_label = tk.Label(
            info_frame,
            text="",
            font=("Segoe UI", 13),
            fg="#e5e7eb",
            bg="#1f2937"
        )
        self.step_label.pack()

        self.action_label = tk.Label(
            info_frame,
            text="",
            font=("Segoe UI", 13, "bold"),
            fg="#22c55e",
            bg="#1f2937"
        )
        self.action_label.pack(pady=5)

        btn_frame = tk.Frame(left_frame, bg="#1f2937")
        btn_frame.pack(pady=15)

        self.btn_prev = tk.Button(
            btn_frame,
            text="◀ Prev",
            command=self.prev_step,
            font=("Segoe UI", 11, "bold"),
            bg="#475569",
            fg="white",
            width=10
        )
        self.btn_prev.grid(row=0, column=0, padx=8)

        self.btn_next = tk.Button(
            btn_frame,
            text="Next ▶",
            command=self.next_step,
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            width=10
        )
        self.btn_next.grid(row=0, column=1, padx=8)

        self.btn_auto = tk.Button(
            btn_frame,
            text="Auto Play",
            command=self.auto_play,
            font=("Segoe UI", 11, "bold"),
            bg="#16a34a",
            fg="white",
            width=10
        )
        self.btn_auto.grid(row=0, column=2, padx=8)

        self.btn_reset = tk.Button(
            btn_frame,
            text="Reset",
            command=self.reset,
            font=("Segoe UI", 11, "bold"),
            bg="#dc2626",
            fg="white",
            width=10
        )
        self.btn_reset.grid(row=0, column=3, padx=8)

        timeline_title = tk.Label(
            right_frame,
            text="UCS SOLUTION PATH",
            font=("Segoe UI", 15, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        )
        timeline_title.pack(pady=15)

        self.summary_label = tk.Label(
            right_frame,
            text=f"Tổng số bước: {len(self.actions)}",
            font=("Segoe UI", 12, "bold"),
            fg="#facc15",
            bg="#0f172a"
        )
        self.summary_label.pack(pady=5)

        self.listbox = tk.Listbox(
            right_frame,
            width=28,
            height=22,
            font=("Consolas", 11),
            bg="#020617",
            fg="#e5e7eb",
            selectbackground="#2563eb",
            relief="flat"
        )
        self.listbox.pack(padx=15, pady=15)

        self.listbox.insert(tk.END, "Start")

        for i, action in enumerate(self.actions, start=1):
            self.listbox.insert(tk.END, f"Bước {i}: {action}")

    def update_board(self):
        state = self.states[self.index]

        for i in range(3):
            for j in range(3):
                value = state[i][j]

                if value == 0:
                    self.cells[i][j].config(
                        text="",
                        bg="#020617",
                        fg="#020617"
                    )
                else:
                    self.cells[i][j].config(
                        text=str(value),
                        bg="#334155",
                        fg="white"
                    )

        self.step_label.config(
            text=f"Bước hiện tại: {self.index} / {len(self.states) - 1}"
        )

        if self.index == 0:
            self.action_label.config(text="Trạng thái ban đầu")
            self.status_label.config(text="Agent đang đứng tại điểm xuất phát")
        else:
            self.action_label.config(text=f"Hành động: {self.actions[self.index - 1]}")
            self.status_label.config(text="Agent đang lần theo lời giải UCS")

        if self.index == len(self.states) - 1:
            self.status_label.config(text="ĐÃ ĐẠT TRẠNG THÁI ĐÍCH")

        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.index)
        self.listbox.activate(self.index)

    def next_step(self):
        if self.index < len(self.states) - 1:
            self.index += 1
            self.update_board()

    def prev_step(self):
        if self.index > 0:
            self.index -= 1
            self.update_board()

    def reset(self):
        self.auto_running = False
        self.index = 0
        self.update_board()

    def auto_play(self):
        self.auto_running = True
        self.run_auto()

    def run_auto(self):
        if self.auto_running and self.index < len(self.states) - 1:
            self.index += 1
            self.update_board()
            self.root.after(700, self.run_auto)
        else:
            self.auto_running = False


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

    actions, states = UCS(problem)

    if actions is None:
        print("Không tìm thấy lời giải")
    else:
        root = tk.Tk()
        app = PuzzleUI(root, actions, states)
        root.mainloop()