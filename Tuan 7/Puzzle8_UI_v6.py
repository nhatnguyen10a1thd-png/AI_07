import copy
import heapq
import itertools
import math
import queue
import random
import threading
import tkinter as tk
from collections import deque
from tkinter import ttk


JOURNAL_LIMIT = 5000
_journal_context = threading.local()


class JournalRecorder(list):
    """Danh sách nhật ký có lọc, giới hạn và thống kê sự kiện đầy đủ."""
    SUMMARY_SKIP_MARKERS = (
        "sinh con bằng",
        "xét ",
        "chưa đạt",
        "đưa nút",
        "bỏ qua",
        "and_search. xét kết quả",
        "and_search. gọi or_search cho một",
    )

    def __init__(self, mode="Chi tiết", limit=JOURNAL_LIMIT):
        super().__init__()
        self.mode = mode
        self.limit = max(100, int(limit))
        self.total_count = 0
        self.filtered_count = 0
        self.truncated_count = 0

    def _keep_in_summary(self, label):
        text = str(label).lower()
        return not any(marker in text for marker in self.SUMMARY_SKIP_MARKERS)

    def record(self, label, state, entry_type=None, data=None):
        event_num = self.total_count
        self.total_count += 1

        if self.mode == "Tóm tắt" and not self._keep_in_summary(label):
            self.filtered_count += 1
            return
        if len(self) >= self.limit:
            self.truncated_count += 1
            return

        if entry_type == "beam_group":
            super().append((event_num, entry_type, copy.deepcopy(data)))
        else:
            super().append((event_num, label, copy.deepcopy(state)))


def new_journal():
    """Tạo nhật ký theo cấu hình của worker hiện tại."""
    mode = getattr(_journal_context, "mode", "Chi tiết")
    limit = getattr(_journal_context, "limit", JOURNAL_LIMIT)
    return JournalRecorder(mode=mode, limit=limit)


def journal_total(steps):
    return getattr(steps, "total_count", len(steps))


def journal_filtered(steps):
    return getattr(steps, "filtered_count", 0)


def journal_truncated(steps):
    return getattr(steps, "truncated_count", 0)


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
        self._validate_board(initial, "initial")
        self._validate_board(goal, "goal")
        if sorted(value for row in initial for value in row) != sorted(value for row in goal for value in row):
            raise ValueError("initial và goal phải chứa cùng một tập ô số")
        self.initial = copy.deepcopy(initial)
        self.goal = copy.deepcopy(goal)

    @staticmethod
    def _validate_board(board, name):
        if not isinstance(board, (list, tuple)) or len(board) != 3:
            raise ValueError(f"{name} phải là bảng 3x3")
        if any(not isinstance(row, (list, tuple)) or len(row) != 3 for row in board):
            raise ValueError(f"{name} phải là bảng 3x3")
        values = [value for row in board for value in row]
        if sorted(values) != list(range(9)):
            raise ValueError(f"{name} phải chứa đúng các số từ 0 đến 8, không trùng lặp")

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
        if not (0 <= ni < 3 and 0 <= nj < 3):
            return None
        new_state = copy.deepcopy(state)
        new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]
        return new_state

    def results(self, state, action):
        """
        Trả về tất cả kết quả có thể xảy ra của một hành động.

        8-puzzle chuẩn là môi trường xác định nên mỗi hành động chỉ có
        một kết quả. Hàm vẫn trả về danh sách để dùng cho AND-OR Search.
        """
        next_state = self.result(state, action)
        return [next_state] if next_state is not None else []

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


def is_solvable(initial, goal):
    """Kiểm tra initial và goal có cùng parity hay không."""
    goal_order = {
        tile: position
        for position, tile in enumerate(
            value for row in goal for value in row if value != 0
        )
    }
    sequence = [
        goal_order[tile]
        for row in initial
        for tile in row
        if tile != 0
    ]
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return inversions % 2 == 0


def parity_failure(problem, steps):
    """Trả về kết quả thất bại sớm nếu initial và goal khác parity."""
    if is_solvable(problem.initial, problem.goal):
        return None
    add_step(steps, "Dừng: initial và goal khác parity nên bài toán vô nghiệm", problem.initial)
    return None, None, steps


def add_step(steps, label, state):
    """Thêm một dòng nhật ký theo đúng thứ tự thực thi mã giả."""
    if isinstance(steps, JournalRecorder):
        steps.record(label, state)
    elif len(steps) < JOURNAL_LIMIT:
        steps.append((len(steps), label, copy.deepcopy(state)))


def add_beam_group(steps, data):
    """Thêm một mốc Local Beam Search mà vẫn giữ thống kê JournalRecorder."""
    if isinstance(steps, JournalRecorder):
        steps.record(data.get("label", "Cập nhật beams"), None, "beam_group", data)
    elif len(steps) < JOURNAL_LIMIT:
        steps.append((len(steps), "beam_group", copy.deepcopy(data)))


# ============================================================
#  CÁC THUẬT TOÁN TÌM KIẾM
# ============================================================

def BFS(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "B1. Khởi tạo: initial đồng thời là goal → trả về", node.state)]
    steps = new_journal()
    add_step(steps, "B1. Khởi tạo frontier = Queue([initial]), explored = ∅", node.state)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    frontier, explored = deque([node]), set()
    frontier_state = {state_to_tuple(node.state)}
    while frontier:
        node = frontier.popleft()
        frontier_state.discard(state_to_tuple(node.state))
        add_step(steps, f"B2. Lấy đầu Queue: depth={node.depth}; frontier còn {len(frontier)} nút", node.state)
        add_step(steps, "B3. Kiểm tra goal: chưa đạt → tiếp tục mở rộng", node.state)
        explored.add(state_to_tuple(node.state))
        add_step(steps, f"B4. Đưa nút hiện tại vào explored; explored có {len(explored)} trạng thái", node.state)
        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_tuple = state_to_tuple(child.state)
            if child_tuple not in explored and child_tuple not in frontier_state:
                add_step(steps, f"B5. Sinh con bằng {action}; chưa gặp → thêm cuối Queue", child.state)
                if problem.goal_test(child.state):
                    add_step(steps, "B6. Kiểm tra nút con: đạt goal → truy vết và trả về lời giải", child.state)
                    actions, states = solution(child)
                    return actions, states, steps
                frontier.append(child)
                frontier_state.add(child_tuple)
            else:
                source = "explored" if child_tuple in explored else "frontier"
                add_step(steps, f"B5. Sinh con bằng {action}; đã có trong {source} → bỏ qua", child.state)
    add_step(steps, "B7. Frontier rỗng → không tìm thấy lời giải", problem.initial)
    return None, None, steps


def DFS(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "B1. Khởi tạo: initial đồng thời là goal → trả về", node.state)]
    steps = new_journal()
    add_step(steps, "B1. Khởi tạo frontier = Stack([initial]), explored = ∅", node.state)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    frontier, explored = [node], set()
    frontier_state = {state_to_tuple(node.state)}
    while frontier:
        node = frontier.pop()
        frontier_state.discard(state_to_tuple(node.state))
        add_step(steps, f"B2. Lấy đỉnh Stack: depth={node.depth}; frontier còn {len(frontier)} nút", node.state)
        add_step(steps, "B3. Kiểm tra goal: chưa đạt → tiếp tục mở rộng", node.state)
        explored.add(state_to_tuple(node.state))
        add_step(steps, f"B4. Đưa nút hiện tại vào explored; explored có {len(explored)} trạng thái", node.state)
        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_tuple = state_to_tuple(child.state)
            if child_tuple not in explored and child_tuple not in frontier_state:
                add_step(steps, f"B5. Sinh con bằng {action}; chưa gặp → đẩy lên Stack", child.state)
                if problem.goal_test(child.state):
                    add_step(steps, "B6. Kiểm tra nút con: đạt goal → truy vết và trả về lời giải", child.state)
                    actions, states = solution(child)
                    return actions, states, steps
                frontier.append(child)
                frontier_state.add(child_tuple)
            else:
                source = "explored" if child_tuple in explored else "frontier"
                add_step(steps, f"B5. Sinh con bằng {action}; đã có trong {source} → bỏ qua", child.state)
    add_step(steps, "B7. Frontier rỗng → không tìm thấy lời giải", problem.initial)
    return None, None, steps


def UCS(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return [], [node.state], [(0, "B1. Khởi tạo: initial đồng thời là goal, g=0 → trả về", node.state)]
    steps = new_journal()
    add_step(steps, "B1. Khởi tạo frontier = PriorityQueue(initial, g=0), explored = ∅", node.state)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    frontier, explored = [], set()
    counter = itertools.count()
    heapq.heappush(frontier, (node.path_cost, next(counter), node))
    best_cost = {state_to_tuple(node.state): 0}
    while frontier:
        cost, _, node = heapq.heappop(frontier)
        node_key = state_to_tuple(node.state)
        if cost != best_cost.get(node_key) or node_key in explored:
            add_step(steps, f"B2. Lấy nút g={cost}, nhưng đây là bản ghi cũ/đã mở rộng → bỏ qua", node.state)
            continue
        add_step(steps, f"B2. Lấy nút có g nhỏ nhất: g={cost}", node.state)
        if problem.goal_test(node.state):
            add_step(steps, "B3. Kiểm tra goal: đạt → truy vết và trả về lời giải tối ưu", node.state)
            actions, states = solution(node)
            return actions, states, steps
        add_step(steps, "B3. Kiểm tra goal: chưa đạt → tiếp tục mở rộng", node.state)
        explored.add(node_key)
        add_step(steps, f"B4. Đưa nút hiện tại vào explored; explored có {len(explored)} trạng thái", node.state)
        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_tuple = state_to_tuple(child.state)
            if child_tuple not in explored and child.path_cost < best_cost.get(child_tuple, float("inf")):
                best_cost[child_tuple] = child.path_cost
                add_step(steps, f"B5. Sinh con bằng {action}; cập nhật g={child.path_cost} và thêm vào PriorityQueue", child.state)
                heapq.heappush(frontier, (child.path_cost, next(counter), child))
            else:
                add_step(steps, f"B5. Sinh con bằng {action}; không cải thiện chi phí/đã explored → bỏ qua", child.state)
    add_step(steps, "B6. Frontier rỗng → không tìm thấy lời giải", problem.initial)
    return None, None, steps


def depth_limited_search(problem, node, limit, path_set, steps, step_num, current_depth_limit):
    if problem.goal_test(node.state):
        add_step(steps, f"DLS. Kiểm tra goal tại depth={node.depth}: đạt → trả về nút", node.state)
        return node
    if limit == 0:
        add_step(steps, f"DLS. depth={node.depth}: hết giới hạn → cutoff", node.state)
        return "cutoff"
    cutoff = False
    for action in problem.actions(node.state):
        child = child_node(problem, node, action)
        if state_to_tuple(child.state) in path_set:
            add_step(steps, f"DLS. Sinh con bằng {action}; nằm trên đường hiện tại → bỏ qua chu trình", child.state)
            continue
        path_set.add(state_to_tuple(child.state))
        add_step(steps, f"DLS. Đi {action} tới depth={child.depth}; giới hạn vòng hiện tại={current_depth_limit}", child.state)
        result = depth_limited_search(problem, child, limit - 1, path_set, steps, step_num, current_depth_limit)
        if result == "cutoff":
            cutoff = True
        elif result:
            return result
        path_set.remove(state_to_tuple(child.state))
        add_step(steps, f"DLS. Quay lui khỏi nhánh {action}", node.state)
    return "cutoff" if cutoff else None


def IDS(problem, max_depth):
    start = Node(problem.initial)
    if problem.goal_test(start.state):
        return [], [start.state], [(0, "B1. initial đồng thời là goal → trả về", start.state)]
    steps = new_journal()
    add_step(steps, "B1. Khởi tạo giới hạn độ sâu từ 0", start.state)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    step_num = [1]
    for depth in range(max(0, max_depth) + 1):
        add_step(steps, f"B2. Bắt đầu Depth-Limited Search với limit={depth}", start.state)
        result = depth_limited_search(problem, start, depth, {state_to_tuple(start.state)}, steps, step_num, depth)
        if result != "cutoff" and result:
            add_step(steps, f"B3. DLS limit={depth} tìm thấy goal → trả về lời giải", result.state)
            actions, states = solution(result)
            return actions, states, steps
        add_step(steps, f"B3. DLS limit={depth} chưa tìm thấy → tăng giới hạn", start.state)
    add_step(steps, f"B4. Đã đạt max_depth={max_depth} → không tìm thấy lời giải", start.state)
    return None, None, steps


def GBFS(problem):
    """
    Greedy Best-First Search (Tìm kiếm tham lam)
    Chỉ dùng h(n) = Manhattan Distance để chọn nút mở rộng.
    """
    start_node = Node(problem.initial)
    h_start = manhattan_distance(start_node.state, problem.goal)
    steps = new_journal()
    add_step(steps, f"B1. Khởi tạo frontier = PriorityQueue(initial, h={h_start}), reached = ∅", start_node.state)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    frontier = []
    counter = itertools.count()
    heapq.heappush(frontier, (h_start, next(counter), start_node))
    frontier_state = {state_to_tuple(start_node.state)}
    reached = set()

    while frontier:
        h_node, _, node = heapq.heappop(frontier)
        node_key = state_to_tuple(node.state)
        frontier_state.discard(node_key)
        add_step(steps, f"B2. Lấy nút có h nhỏ nhất: h={h_node}", node.state)

        if problem.goal_test(node.state):
            add_step(steps, "B3. Kiểm tra goal: đạt → truy vết và trả về lời giải", node.state)
            actions, states = solution(node)
            return actions, states, steps

        add_step(steps, "B3. Kiểm tra goal: chưa đạt → tiếp tục mở rộng", node.state)
        reached.add(node_key)
        add_step(steps, f"B4. Đưa nút vào reached; reached có {len(reached)} trạng thái", node.state)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_key = state_to_tuple(child.state)

            if child_key not in frontier_state and child_key not in reached:
                h_child = manhattan_distance(child.state, problem.goal)
                add_step(steps, f"B5. Sinh con bằng {action}; h={h_child} → thêm vào PriorityQueue", child.state)
                heapq.heappush(frontier, (h_child, next(counter), child))
                frontier_state.add(child_key)
            else:
                add_step(steps, f"B5. Sinh con bằng {action}; đã có trong frontier/reached → bỏ qua", child.state)

    add_step(steps, "B6. Frontier rỗng → không tìm thấy lời giải", problem.initial)
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
    steps = new_journal()
    add_step(steps, f"B1. Khởi tạo frontier với initial: f={f_start} = g={g_start} + h={h_start}", start_node.state)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    frontier = []
    counter = itertools.count()
    heapq.heappush(frontier, (f_start, next(counter), start_node))
    g_score = {state_to_tuple(start_node.state): g_start}
    reached = set()

    while frontier:
        f_node, _, node = heapq.heappop(frontier)
        node_key = state_to_tuple(node.state)
        if node.path_cost != g_score.get(node_key) or node_key in reached:
            add_step(steps, f"B2. Lấy nút f={f_node}, nhưng đây là bản ghi cũ/đã mở rộng → bỏ qua", node.state)
            continue
        add_step(steps, f"B2. Lấy nút có f nhỏ nhất: f={f_node}, g={node.path_cost}", node.state)

        if problem.goal_test(node.state):
            add_step(steps, "B3. Kiểm tra goal: đạt → truy vết và trả về lời giải", node.state)
            actions, states = solution(node)
            return actions, states, steps

        add_step(steps, "B3. Kiểm tra goal: chưa đạt → tiếp tục mở rộng", node.state)
        reached.add(node_key)
        add_step(steps, f"B4. Đưa nút vào reached; reached có {len(reached)} trạng thái", node.state)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_key = state_to_tuple(child.state)
            g_new = child.path_cost

            if g_new >= g_score.get(child_key, float("inf")):
                add_step(steps, f"B5. Sinh con bằng {action}; g={g_new} không tốt hơn → bỏ qua", child.state)
                continue

            g_score[child_key] = g_new
            reached.discard(child_key)
            h_new = manhattan_distance(child.state, problem.goal)
            f_new = g_new + h_new
            heapq.heappush(frontier, (f_new, next(counter), child))
            add_step(steps, f"B5. Sinh con bằng {action}; cập nhật f={f_new} = g={g_new} + h={h_new}", child.state)

    add_step(steps, "B6. Frontier rỗng → không tìm thấy lời giải", problem.initial)
    return None, None, steps


# ============================================================
#  THUẬT TOÁN IDA* (Iterative Deepening A*)
# ============================================================

def _ida_search(node, g, threshold, problem, steps, step_num, path_set):
    h = manhattan_distance(node.state, problem.goal)
    f = g + h

    if f > threshold:
        add_step(steps, f"IDA*. f={f} > threshold={threshold} → cắt nhánh, trả về {f}", node.state)
        return f

    if problem.goal_test(node.state):
        add_step(steps, f"IDA*. f={f} ≤ threshold và đạt goal → trả về nút", node.state)
        return node

    add_step(steps, f"IDA*. Mở rộng nút f={f} ≤ threshold={threshold}", node.state)
    min_threshold = float("inf")

    for action in problem.actions(node.state):
        next_state = problem.result(node.state, action)
        next_key = state_to_tuple(next_state)
        if next_key in path_set:
            add_step(steps, f"IDA*. Sinh con bằng {action}; nằm trên đường hiện tại → bỏ qua chu trình", next_state)
            continue
        child = Node(state=next_state, parent=node, action=action,
                     path_cost=node.path_cost + 1, depth=node.depth + 1)

        h_child = manhattan_distance(child.state, problem.goal)
        f_child = (g + 1) + h_child
        add_step(steps, f"IDA*. Đi {action}: f={f_child} = g={g+1} + h={h_child}", child.state)

        path_set.add(next_key)
        result = _ida_search(child, g + 1, threshold, problem, steps, step_num, path_set)
        path_set.remove(next_key)

        if isinstance(result, Node):
            return result

        if result < min_threshold:
            min_threshold = result
            add_step(steps, f"IDA*. Cập nhật threshold kế tiếp tạm thời = {min_threshold}", node.state)

    return min_threshold


def IDA_Star(problem):
    """Thuật toán IDA* (Iterative Deepening A*)."""
    start_node = Node(problem.initial)
    threshold = manhattan_distance(start_node.state, problem.goal)

    steps = new_journal()
    add_step(steps, f"B1. Khởi tạo threshold = h(initial) = {threshold}", start_node.state)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    step_num = [1]

    while True:
        add_step(steps, f"B2. Bắt đầu DFS giới hạn theo f với threshold={threshold}", start_node.state)
        result = _ida_search(
            start_node,
            0,
            threshold,
            problem,
            steps,
            step_num,
            {state_to_tuple(start_node.state)},
        )

        if isinstance(result, Node):
            add_step(steps, "B3. Tìm thấy goal → truy vết và trả về lời giải", result.state)
            actions, states = solution(result)
            return actions, states, steps

        if result == float("inf"):
            add_step(steps, "B3. Không còn threshold kế tiếp → không tìm thấy lời giải", start_node.state)
            return None, None, steps

        add_step(steps, f"B3. Chưa tìm thấy → tăng threshold từ {threshold} lên {result}", start_node.state)
        threshold = result

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

    steps = new_journal()
    add_step(steps, f"B1. Gán Current_State = initial; Value(Current)={current_value}", problem.initial)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    step_num = 1
    path = [current_node]

    while True:
        if problem.goal_test(current_node.state):
            add_step(steps, "B2. Kiểm tra Current_State: đạt goal → trả về", current_node.state)
            break

        add_step(steps, f"B2. Current chưa đạt goal; bắt đầu xét lần lượt các lân cận, Value={current_value}", current_node.state)
        found_better = False

        for action in problem.actions(current_node.state):
            next_state = problem.result(current_node.state, action)
            next_value = -manhattan_distance(next_state, problem.goal)

            if next_value > current_value:
                add_step(steps, f"B3. Xét {action}: Value={next_value} > {current_value} → chọn làm Current mới", next_state)
                next_node = Node(state=next_state, parent=current_node, action=action,
                                 path_cost=current_node.path_cost + 1,
                                 depth=current_node.depth + 1)
                current_node = next_node
                current_value = next_value
                path.append(current_node)
                found_better = True
                break
            else:
                add_step(steps, f"B3. Xét {action}: Value={next_value} không tốt hơn {current_value} → bỏ qua", next_state)

        if not found_better:
            add_step(steps, f"B4. Không có lân cận tốt hơn → dừng tại cực đại cục bộ, Value={current_value}", current_node.state)
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

    steps = new_journal()
    add_step(steps, f"B1. Gán Current_State = initial; Value(Current)={current_value}", problem.initial)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    step_num = 1
    path = [current_node]

    while True:
        if problem.goal_test(current_node.state):
            add_step(steps, "B2. Kiểm tra Current_State: đạt goal → trả về", current_node.state)
            break

        add_step(steps, f"B2. Current chưa đạt goal; tạo Better_Neighbors, Value={current_value}", current_node.state)
        better_neighbors = []
        for action in problem.actions(current_node.state):
            next_state = problem.result(current_node.state, action)
            next_value = -manhattan_distance(next_state, problem.goal)

            if next_value > current_value:
                better_neighbors.append((next_value, action, next_state))
                add_step(steps, f"B3. Xét {action}: Value={next_value} > {current_value} → thêm vào Better_Neighbors", next_state)
            else:
                add_step(steps, f"B3. Xét {action}: Value={next_value} không tốt hơn → bỏ qua", next_state)

        if not better_neighbors:
            add_step(steps, f"B4. Better_Neighbors rỗng → dừng tại cực đại cục bộ, Value={current_value}", current_node.state)
            break

        next_value, action, next_state = random.choice(better_neighbors)
        add_step(steps, f"B5. Chọn ngẫu nhiên {action} từ {len(better_neighbors)} lân cận tốt hơn → Value={next_value}", next_state)

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

def random_node_from(problem, steps_count=20):
    """Tạo nút ngẫu nhiên nhưng vẫn giữ chuỗi cha hợp lệ bắt đầu từ initial."""
    current = Node(copy.deepcopy(problem.initial))
    for _ in range(max(0, steps_count)):
        action = random.choice(problem.actions(current.state))
        current = child_node(problem, current, action)
    return current


def random_state_from(problem, steps_count=20):
    """Tương thích ngược: trả về trạng thái cuối của một bước đi ngẫu nhiên."""
    return random_node_from(problem, steps_count).state


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
    all_steps = new_journal()
    step_num = 0
    if problem.goal_test(problem.initial):
        return [], [problem.initial], [(0, "Start", problem.initial)]
    failure = parity_failure(problem, all_steps)
    if failure:
        return failure
    if max_restart <= 0:
        add_step(all_steps, "Dừng: số lần restart phải lớn hơn 0", problem.initial)
        return None, None, all_steps

    for restart in range(1, max_restart + 1):
        current_node = random_node_from(problem, random_steps)
        current_state = current_node.state
        current_value = -manhattan_distance(current_node.state, problem.goal)

        add_step(all_steps, f"B1. Restart {restart}/{max_restart}: tạo Random_State bằng {random_steps} bước; Value={current_value}", current_state)

        while True:
            if problem.goal_test(current_node.state):
                add_step(all_steps, "B2. Current_State đạt goal → trả về lời giải", current_node.state)
                actions_list, states_list = solution(current_node)
                return actions_list, states_list, all_steps

            add_step(all_steps, f"B2. Current chưa đạt goal; sinh Better_Neighbors, Value={current_value}", current_node.state)
            better_neighbors = []
            for action in problem.actions(current_node.state):
                next_state = problem.result(current_node.state, action)
                next_value = -manhattan_distance(next_state, problem.goal)

                if next_value > current_value:
                    better_neighbors.append((next_value, action, next_state))
                    add_step(all_steps, f"B3. Xét {action}: Value={next_value} tốt hơn → thêm vào Better_Neighbors", next_state)
                else:
                    add_step(all_steps, f"B3. Xét {action}: Value={next_value} không tốt hơn → bỏ qua", next_state)

            if not better_neighbors:
                add_step(all_steps, f"B4. Better_Neighbors rỗng → kẹt cục bộ; chuyển sang restart kế tiếp", current_node.state)
                break

            best_value = max(n[0] for n in better_neighbors)
            best_candidates = [n for n in better_neighbors if n[0] == best_value]
            next_value, action, next_state = random.choice(best_candidates)

            next_node = Node(
                state=next_state,
                parent=current_node,
                action=action,
                path_cost=current_node.path_cost + 1,
                depth=current_node.depth + 1,
            )
            current_node = next_node
            current_value = next_value

            add_step(all_steps, f"B5. Chọn ngẫu nhiên trong các lân cận tốt nhất: {action} → Value={current_value}", current_node.state)

    add_step(all_steps, f"B6. Đã dùng hết {max_restart} lần restart → không tìm thấy lời giải", problem.initial)
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
        return None, None, [(0, "Không chạy: k phải lớn hơn 0", problem.initial)]

    all_steps = new_journal()
    step_num = 0
    if problem.goal_test(problem.initial):
        return [], [problem.initial], [(0, "Start", problem.initial)]
    failure = parity_failure(problem, all_steps)
    if failure:
        return failure

    current_nodes = []
    seen = set()
    max_attempts = max(100, k * 50)
    attempts = 0
    while len(current_nodes) < k and attempts < max_attempts:
        attempts += 1
        node = random_node_from(problem, random_steps)
        key = state_to_tuple(node.state)
        if key in seen:
            continue
        seen.add(key)
        current_nodes.append(node)

    beam_states = [n.state for n in current_nodes]
    beam_values = [-manhattan_distance(n.state, problem.goal) for n in current_nodes]
    add_beam_group(all_steps, {
        "label": f"B1. Khởi tạo {len(current_nodes)} beam ngẫu nhiên và tính Value",
        "beams": beam_states,
        "values": beam_values,
        "iteration": 0,
    })
    step_num += 1

    for iteration in range(1, max_iters + 1):
        neighbors = []

        for idx, node in enumerate(current_nodes):
            add_step(
                all_steps,
                f"B2. Iteration {iteration}: kiểm tra Beam {idx + 1}/{len(current_nodes)}",
                node.state,
            )
            if problem.goal_test(node.state):
                actions, states = solution(node)
                add_beam_group(all_steps, {
                    "label": "B3. Beam hiện tại đạt goal → trả về lời giải",
                    "beams": [node.state],
                    "values": [0],
                    "iteration": iteration,
                })
                return actions, states, all_steps

            for action in problem.actions(node.state):
                next_state = problem.result(node.state, action)
                child = Node(
                    state=next_state,
                    parent=node,
                    action=action,
                    path_cost=node.path_cost + 1,
                    depth=node.depth + 1,
                )
                neighbors.append(child)
                add_step(
                    all_steps,
                    f"B3. Sinh lân cận của Beam {idx + 1} bằng {action}; Value={-manhattan_distance(next_state, problem.goal)}",
                    next_state,
                )

        for child in neighbors:
            if problem.goal_test(child.state):
                actions, states = solution(child)
                add_beam_group(all_steps, {
                    "label": "B4. Một lân cận đạt goal → trả về lời giải",
                    "beams": [child.state],
                    "values": [0],
                    "iteration": iteration,
                })
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
        add_beam_group(all_steps, {
            "label": f"B4. Iteration {iteration}: xếp hạng và giữ {len(current_nodes)} trạng thái tốt nhất",
            "beams": beam_states,
            "values": beam_values,
            "iteration": iteration,
        })
        step_num += 1

    add_step(all_steps, f"B5. Đạt max_iters={max_iters} → không tìm thấy lời giải", problem.initial)
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

    Trả về: (actions, states, steps) tương thích với UI v6
    """
    current_node = Node(state=problem.initial)
    current_h = manhattan_distance(current_node.state, problem.goal)

    T = T0
    step_num = 0
    path = [current_node]

    # Bước 0: trạng thái ban đầu
    steps = new_journal()
    add_step(steps, f"B1. Gán Current_State=initial, h={current_h}; T=T0={T:.2f}", problem.initial)
    failure = parity_failure(problem, steps)
    if failure:
        return failure
    step_num += 1

    loop_count = 0

    while T > Tmin and loop_count < max_steps:

        # Kiểm tra đích
        if problem.goal_test(current_node.state):
            add_step(steps, "B2. Current_State đạt goal → dừng và trả về đường đi", current_node.state)
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
            label = (f"B3-B4. Chọn {action}; Δ={delta:+d}<0, "
                     f"h: {current_h}→{next_h}, T={T:.4f} → chấp nhận vì tốt hơn")
            next_node = Node(state=next_state, parent=current_node, action=action)
            current_node = next_node
            current_h = next_h
            path.append(current_node)
            add_step(steps, label, next_state)
        else:
            # Chấp nhận có xác suất
            p = math.exp(-delta / T)
            r = random.random()
            if r < p:
                label = (f"B3-B4. Chọn {action}; Δ={delta:+d}≥0, "
                         f"p={p:.4f}, r={r:.4f}<p, T={T:.4f} → chấp nhận ngẫu nhiên")
                next_node = Node(state=next_state, parent=current_node, action=action)
                current_node = next_node
                current_h = next_h
                path.append(current_node)
                add_step(steps, label, next_state)
            else:
                label = (f"B3-B4. Chọn {action}; Δ={delta:+d}≥0, "
                         f"p={p:.4f}, r={r:.4f}≥p, T={T:.4f} → từ chối, giữ Current")
                add_step(steps, label, next_state)

        # Làm nguội nhiệt độ
        T = alpha * T

    # Kiểm tra lần cuối
    found = problem.goal_test(current_node.state)
    if not found:
        add_step(steps, f"B5. Điều kiện dừng: T={T:.6f} hoặc đạt max_steps → không tìm thấy goal", current_node.state)

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
#  THUẬT TOÁN AND-OR GRAPH SEARCH
# ============================================================

def _or_search(state, problem, path, depth_remaining, steps, step_num):
    """
    Nút OR: chọn một hành động sao cho AND_SEARCH của hành động đó thành công.
    """
    if problem.goal_test(state):
        add_step(steps, "OR_SEARCH. Trạng thái đạt goal → trả về kế hoạch rỗng", state)
        return []

    state_key = state_to_tuple(state)
    if state_key in path:
        add_step(steps, "OR_SEARCH. Trạng thái đã nằm trên path → thất bại để tránh chu trình", state)
        return None
    if depth_remaining <= 0:
        add_step(steps, "OR_SEARCH. Hết giới hạn độ sâu → thất bại", state)
        return None

    add_step(steps, f"OR_SEARCH. Mở rộng OR-node, depth_remaining={depth_remaining}", state)
    actions = problem.actions(state)
    actions.sort(
        key=lambda action: manhattan_distance(
            problem.result(state, action),
            problem.goal
        )
    )

    for action in actions:
        result_states = problem.results(state, action)
        add_step(steps, f"OR_SEARCH. Thử hành động {action}; chuyển sang AND_SEARCH cho {len(result_states)} kết quả", state)

        for index, result_state in enumerate(result_states, start=1):
            h_value = manhattan_distance(result_state, problem.goal)
            label = (
                f"AND_SEARCH. Xét kết quả {index}/{len(result_states)} của {action} "
                f"(depth={depth_remaining - 1}, h={h_value})"
            )
            add_step(steps, label, result_state)

        plan = _and_search(
            result_states,
            problem,
            path | {state_key},
            depth_remaining - 1,
            steps,
            step_num
        )

        if plan is not None:
            add_step(steps, f"OR_SEARCH. AND_SEARCH của {action} thành công → chọn hành động này", state)
            return {
                "action": action,
                "plans": plan
            }

        add_step(steps, f"OR_SEARCH. AND_SEARCH của {action} thất bại → thử hành động tiếp theo", state)
    add_step(steps, "OR_SEARCH. Mọi hành động đều thất bại → trả về failure", state)
    return None


def _and_search(states, problem, path, depth_remaining, steps, step_num):
    """
    Nút AND: tất cả trạng thái kết quả đều phải có kế hoạch thành công.
    """
    plans = {}

    for state in states:
        add_step(steps, "AND_SEARCH. Gọi OR_SEARCH cho một trạng thái kết quả", state)
        plan_s = _or_search(
            state,
            problem,
            path,
            depth_remaining,
            steps,
            step_num
        )

        if plan_s is None:
            add_step(steps, "AND_SEARCH. Có một kết quả thất bại → toàn bộ hành động thất bại", state)
            return None

        plans[state_to_tuple(state)] = plan_s

    if states:
        add_step(steps, "AND_SEARCH. Mọi trạng thái kết quả đều có kế hoạch → thành công", states[-1])
    return plans


def _extract_and_or_solution(problem, plan):
    """Lấy một đường đi thực thi từ kế hoạch AND-OR của 8-puzzle."""
    actions = []
    states = [copy.deepcopy(problem.initial)]
    current_state = copy.deepcopy(problem.initial)
    current_plan = plan

    while isinstance(current_plan, dict) and "action" in current_plan:
        action = current_plan["action"]
        next_state = problem.results(current_state, action)[0]

        actions.append(action)
        states.append(next_state)

        current_state = next_state
        current_plan = current_plan["plans"][state_to_tuple(next_state)]

    return actions, states


def AND_OR_Graph_Search(problem, max_depth=30):
    """
    AND-OR Graph Search cho 8-puzzle.

    - OR_SEARCH chọn một hành động có thể dẫn tới mục tiêu.
    - AND_SEARCH yêu cầu mọi kết quả của hành động đều có kế hoạch.
    - path tránh chu trình; max_depth giới hạn độ sâu tìm kiếm.

    Trả về: (actions, states, steps) tương thích với UI v6.
    """
    steps = new_journal()
    add_step(steps, "B1. Gọi OR_SEARCH(initial, path=∅)", problem.initial)
    step_num = [1]

    if problem.goal_test(problem.initial):
        add_step(steps, "B2. Initial đạt goal → trả về kế hoạch rỗng", problem.initial)
        return [], [problem.initial], steps

    if not is_solvable(problem.initial, problem.goal):
        add_step(steps, "Dừng: initial và goal khác parity nên bài toán vô nghiệm", problem.initial)
        return None, None, steps

    plan = _or_search(
        problem.initial,
        problem,
        set(),
        max_depth,
        steps,
        step_num
    )

    if plan is None:
        add_step(steps, "B3. OR_SEARCH thất bại → không tìm thấy kế hoạch", problem.initial)
        return None, None, steps

    actions, states = _extract_and_or_solution(problem, plan)
    add_step(steps, "B3. OR_SEARCH thành công → trích xuất một đường thực thi từ kế hoạch", states[-1])
    return actions, states, steps


# ============================================================
#  GIAO DIỆN
# ============================================================

def format_state_table(state):
    return "\n".join("  ".join(" " if v == 0 else str(v) for v in row) for row in state)


class UI:
    """Giao diện Tkinter để mô phỏng và phát lại log."""
    DISPLAY_LIMIT = 5000

    def __init__(self, root, initial, goal):
        self.root = root
        self.initial = initial
        self.goal = goal
        self.states = []
        self.step_actions = []
        self.index = 0
        self.auto_running = False
        self.log_ranges = []
        self.log_states = []
        self.current_log_steps = []
        self.current_log_algo = None
        self.has_run = False
        self.solved = False
        self.solution_len = 0
        self.explored_count = 0
        self.log_total_count = 0
        self.journal_filtered_count = 0
        self.journal_truncated_count = 0
        self.current_journal_mode = "Chi tiết"
        self.speed_var = tk.IntVar(value=650)
        self.journal_mode_var = tk.StringVar(value="Chi tiết")
        self.journal_limit_var = tk.StringVar(value=str(JOURNAL_LIMIT))
        self.show_log_states_var = tk.BooleanVar(value=True)
        self.result_queue = queue.Queue()
        self.running = False
        self.run_token = 0
        # Cho Local Beam Search: lưu trạng thái nhóm beam
        self.beam_mode = False
        # Cho Random Restart và SA: đánh dấu thuật toán đặc biệt
        self.special_algo = None

        self.root.title("8-Puzzle v6 - Mô phỏng giải ô số")
        self.root.geometry("1220x720")
        self.root.configure(bg="#f3f4f6")

        self.setup_ui()
        self._update_parameter_controls()
        self.init_empty()
        self.root.after(50, self._poll_results)

    def setup_ui(self):
        tk.Label(self.root, text="MÔ PHỎNG 8-PUZZLE ",
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
                "Simulated Annealing", "AND-OR Graph Search",
            ],
            state="readonly",
            width=22,
        )
        self.algo_box.grid(row=0, column=1, padx=8)
        self.algo_box.bind("<<ComboboxSelected>>", self.on_algorithm_change)

        self.depth_label = tk.Label(ctrl, text="Độ sâu tối đa (IDS):", bg="white")
        self.depth_label.grid(row=0, column=2, sticky="w")
        self.depth_var = tk.StringVar(value="30")
        self.depth_spinbox = tk.Spinbox(
            ctrl, from_=1, to=100, textvariable=self.depth_var, width=6
        )
        self.depth_spinbox.grid(row=0, column=3, padx=8)
        self.run_button = tk.Button(
            ctrl, text="Chạy", command=self.run_algorithm,
            bg="#2563eb", fg="white", width=12
        )
        self.run_button.grid(row=0, column=4, sticky="e")

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

        tk.Label(ctrl, text="Nhật ký:", bg="white").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Combobox(
            ctrl,
            textvariable=self.journal_mode_var,
            values=["Chi tiết", "Tóm tắt"],
            state="readonly",
            width=12,
        ).grid(row=2, column=1, sticky="w", padx=8, pady=(6, 0))
        tk.Label(ctrl, text="Giới hạn lưu:", bg="white").grid(row=2, column=2, sticky="w", pady=(6, 0))
        tk.Spinbox(
            ctrl, from_=100, to=20000, increment=100,
            textvariable=self.journal_limit_var, width=7,
        ).grid(row=2, column=3, sticky="w", padx=8, pady=(6, 0))
        tk.Checkbutton(
            ctrl,
            text="Hiện bảng trong nhật ký",
            variable=self.show_log_states_var,
            command=self._refresh_log_display,
            bg="white",
            activebackground="white",
        ).grid(row=2, column=4, columnspan=3, sticky="w", pady=(6, 0))

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

    def solve(self, algo=None, params=None):
        params = params or {}
        p = Problem(self.initial, self.goal)
        algo = algo or self.algo_var.get()
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
            return Random_Restart_Hill_Climbing(
                p, max_restart=params.get("max_restart", 50), random_steps=25
            )
        if algo == "Local Beam Search":
            return Local_Beam_Search(p, k=3, max_iters=300, random_steps=25)
        if algo == "Simulated Annealing":
            return Simulated_Annealing(
                p,
                T0=params.get("t0", 500.0),
                Tmin=0.01,
                alpha=params.get("alpha", 0.9995),
                max_steps=100000,
            )
        if algo == "AND-OR Graph Search":
            # Giới hạn nội bộ để chống đệ quy vô hạn; không phải tham số UI.
            return AND_OR_Graph_Search(p, 30)
        return IDS(p, params.get("max_depth", 30))

    def run_algorithm(self):
        if self.running:
            return

        self.auto_running = False
        algo = self.algo_var.get()
        max_depth = 30
        if algo == "IDS":
            try:
                max_depth = max(0, int(self.depth_var.get()))
            except ValueError:
                max_depth = 30
        try:
            max_restart = max(1, int(self.restart_var.get()))
        except ValueError:
            max_restart = 50
        try:
            t0 = float(self.sa_t0_var.get())
            if t0 <= 0:
                raise ValueError
        except ValueError:
            t0 = 500.0
        try:
            alpha = float(self.sa_alpha_var.get())
            if not 0 < alpha < 1:
                raise ValueError
        except ValueError:
            alpha = 0.9995
        try:
            journal_limit = max(100, min(20000, int(self.journal_limit_var.get())))
        except ValueError:
            journal_limit = JOURNAL_LIMIT

        params = {
            "max_depth": max_depth,
            "max_restart": max_restart,
            "t0": t0,
            "alpha": alpha,
            "journal_mode": self.journal_mode_var.get(),
            "journal_limit": journal_limit,
        }
        self.running = True
        self.has_run = False
        self.run_token += 1
        token = self.run_token
        self.run_button.config(state="disabled", text="Đang chạy...")
        self.status.config(text=f"Đang tính {algo}...")
        threading.Thread(
            target=self._solve_worker,
            args=(token, algo, params),
            daemon=True,
        ).start()

    def _solve_worker(self, token, algo, params):
        try:
            _journal_context.mode = params.get("journal_mode", "Chi tiết")
            _journal_context.limit = params.get("journal_limit", JOURNAL_LIMIT)
            result = self.solve(algo, params)
            self.result_queue.put(("ok", token, algo, result))
        except Exception as exc:
            self.result_queue.put(("error", token, algo, exc))
        finally:
            _journal_context.mode = "Chi tiết"
            _journal_context.limit = JOURNAL_LIMIT

    def _poll_results(self):
        try:
            while True:
                kind, token, algo, payload = self.result_queue.get_nowait()
                if token != self.run_token:
                    continue
                self.running = False
                self.run_button.config(state="normal", text="Chạy")
                if kind == "error":
                    self._show_error(payload)
                else:
                    self._apply_result(algo, payload)
        except queue.Empty:
            pass
        self.root.after(50, self._poll_results)

    def _show_error(self, error):
        self.has_run = False
        self.status.config(text="Thuật toán gặp lỗi")
        self.summary.config(text=str(error), fg="#dc2626")

    def _apply_result(self, algo, result):
        actions, solution_states, all_steps = result
        if not all_steps:
            all_steps = [(0, "Start", self.initial)]

        self.has_run = True
        self.solved = bool(solution_states and solution_states[-1] == self.goal)
        self.solution_len = len(actions) if actions is not None else 0
        self.explored_count = journal_total(all_steps)
        self.journal_filtered_count = journal_filtered(all_steps)
        self.journal_truncated_count = journal_truncated(all_steps)
        self.current_journal_mode = getattr(all_steps, "mode", self.journal_mode_var.get())
        self.beam_mode = algo == "Local Beam Search"
        self.special_algo = algo if algo in {
            "Local Beam Search", "Random Restart HC", "Simulated Annealing"
        } else None
        self.log_total_count = len(all_steps)
        visible_steps = all_steps[:self.DISPLAY_LIMIT]
        self.current_log_steps = visible_steps
        self.current_log_algo = algo

        if self.solved:
            self.states = solution_states
            self.step_actions = ["Start"] + actions
        else:
            self.states = [self._log_entry_state(entry) for entry in visible_steps] or [self.initial]
            self.step_actions = [self._log_entry_label(entry) for entry in visible_steps] or ["Start"]

        self.display_algorithm_log(algo, visible_steps)
        self.index = 0
        self.update()

    def _refresh_log_display(self):
        if self.has_run and self.current_log_algo and self.current_log_steps:
            self.display_algorithm_log(self.current_log_algo, self.current_log_steps)
            self.highlight_log()

    def _log_entry_state(self, entry):
        _, entry_type, data = entry
        if entry_type == "beam_group":
            beams = data.get("beams", [])
            return beams[0] if beams else self.initial
        return data if isinstance(data, list) else self.initial

    def _log_entry_label(self, entry):
        _, entry_type, data = entry
        if entry_type == "beam_group":
            return data.get("label", "Cập nhật beams")
        return str(entry_type)

    def display_algorithm_log(self, algo, steps):
        """Hiển thị đúng nhật ký thực thi mã giả, độc lập với đường phát lại lời giải."""
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log_ranges = []
        self.log_states = []

        self.log.insert(tk.END, "=" * 62 + "\n", ("beam_header",))
        self.log.insert(tk.END, f"  NHẬT KÝ CHẠY TAY MÃ GIẢ: {algo}\n", ("beam_header",))
        self.log.insert(
            tk.END,
            f"  Chế độ: {self.current_journal_mode} | "
            f"Tổng sự kiện: {self.explored_count} | Đã lưu: {self.log_total_count}\n",
            ("beam_header",),
        )
        self.log.insert(tk.END, "=" * 62 + "\n\n", ("beam_header",))

        for num, entry_type, data in steps:
            start = self.log.index(tk.END)
            state = self._log_entry_state((num, entry_type, data))

            if entry_type == "beam_group":
                self.log.insert(tk.END, f"[Bước {num}] {data['label']}\n", ("beam_header",))
                for beam_idx, beam in enumerate(data.get("beams", [])):
                    value = data.get("values", [None] * len(data.get("beams", [])))[beam_idx]
                    self.log.insert(tk.END, f"  Beam {beam_idx + 1} (Value={value})\n", ("value_tag",))
                    if self.show_log_states_var.get():
                        for line in format_state_table(beam).splitlines():
                            self.log.insert(tk.END, f"    {line}\n")
                    self.log.insert(tk.END, "\n")
            else:
                label = str(entry_type)
                tag = "header"
                if any(word in label.lower() for word in ("đạt goal", "thành công", "chấp nhận", "trả về lời giải")):
                    tag = "sa_accept"
                elif any(word in label.lower() for word in ("bỏ qua", "thất bại", "từ chối", "không tìm thấy", "vô nghiệm")):
                    tag = "sa_reject"
                self.log.insert(tk.END, f"[Bước {num}] {label}\n", (tag,))
                if self.show_log_states_var.get():
                    self.log.insert(tk.END, format_state_table(state) + "\n\n")
                else:
                    self.log.insert(tk.END, "\n")

            self.log_ranges.append((start, self.log.index(tk.END)))
            self.log_states.append(state)

        if self.solved:
            self.summary.config(
                text=f"Sự kiện: {self.explored_count} | Lưu: {self.log_total_count} → Lời giải: {self.solution_len} nước đi",
                fg="#16a34a",
            )
        else:
            self.summary.config(
                text=f"Sự kiện: {self.explored_count} | Lưu: {self.log_total_count} → Không tìm thấy lời giải",
                fg="#dc2626",
            )
        self._append_truncation_notice(len(steps))
        self.log.config(state="disabled")

    def _prepare_beam_trace(self, all_steps):
        self.states = []
        self.step_actions = []
        self._beam_data = []
        for _, action_type, data in all_steps:
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

    # ----------------------------------------------------------
    #  SIMULATED ANNEALING – Runner & Display
    # ----------------------------------------------------------

    def _run_simulated_annealing(self):
        """Giữ tương thích với mã cũ; việc chạy thực tế được đưa sang worker."""
        self.run_algorithm()

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
            summary = (f"Tổng duyệt: {self.explored_count} bước → "
                       f"Lời giải: {self.solution_len} bước")
            self.summary.config(text=summary, fg="#16a34a")
        else:
            summary = f"Tổng duyệt: {self.explored_count} bước → Không tìm thấy lời giải"
            self.summary.config(text=summary, fg="#dc2626")
            self.log.insert(tk.END, "\n❌ KHÔNG TÌM THẤY LỜI GIẢI\n", ("sa_reject",))
        self._append_truncation_notice(len(all_steps))

        self.log.config(state="disabled")

    # ----------------------------------------------------------
    #  LOCAL BEAM SEARCH – Runner & Display
    # ----------------------------------------------------------

    def _run_beam_search(self):
        """Giữ tương thích với mã cũ; việc chạy thực tế được đưa sang worker."""
        self.run_algorithm()

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
            self.summary.config(
                text=f"Tổng iterations: {self.explored_count} → Lời giải: {self.solution_len} bước",
                fg="#16a34a",
            )
        else:
            self.summary.config(
                text=f"Tổng iterations: {self.explored_count} → Không tìm thấy lời giải",
                fg="#dc2626",
            )
            self.log.insert(tk.END, "KHÔNG TÌM THẤY LỜI GIẢI\n", ("header",))
        self._append_truncation_notice(len(all_steps))
        self.log.config(state="disabled")

    # ----------------------------------------------------------
    #  RANDOM RESTART – Runner & Display
    # ----------------------------------------------------------

    def _run_random_restart(self):
        """Giữ tương thích với mã cũ; việc chạy thực tế được đưa sang worker."""
        self.run_algorithm()

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
            self.summary.config(
                text=f"Tổng duyệt: {self.explored_count} bước → Lời giải: {self.solution_len} bước",
                fg="#16a34a",
            )
        else:
            self.summary.config(
                text=f"Tổng duyệt: {self.explored_count} bước → Không tìm thấy lời giải",
                fg="#dc2626",
            )
            self.log.insert(tk.END, "\nKHÔNG TÌM THẤY LỜI GIẢI\n", ("header",))
        self._append_truncation_notice(len(all_steps))
        self.log.config(state="disabled")

    # ----------------------------------------------------------
    #  HIỂN THỊ BÌNH THƯỜNG
    # ----------------------------------------------------------

    def on_algorithm_change(self, _event):
        self.auto_running = False
        if self.running:
            self.run_token += 1
            self.running = False
            self.run_button.config(state="normal", text="Chạy")
        self._update_parameter_controls()
        self.init_empty()

    def _update_parameter_controls(self):
        """Chỉ cho phép nhập độ sâu khi thuật toán đang chọn là IDS."""
        state = "normal" if self.algo_var.get() == "IDS" else "disabled"
        self.depth_spinbox.config(state=state)
        self.depth_label.config(fg="#111827" if state == "normal" else "#9ca3af")

    def init_empty(self):
        self.has_run = False
        self.solved = False
        self.solution_len = 0
        self.explored_count = 0
        self.log_total_count = 0
        self.journal_filtered_count = 0
        self.journal_truncated_count = 0
        self.current_journal_mode = self.journal_mode_var.get()
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
        self.log_states = []
        self.current_log_steps = []
        self.current_log_algo = None
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
            self.summary.config(
                text=f"Tổng duyệt: {self.explored_count} bước → Lời giải: {self.solution_len} bước",
                fg="#16a34a",
            )
        else:
            self.summary.config(
                text=f"Tổng duyệt: {self.explored_count} bước → Không tìm thấy lời giải",
                fg="#dc2626",
            )
            self.log.insert(tk.END, "KHÔNG TÌM THẤY LỜI GIẢI", ("header",))
        self._append_truncation_notice(len(steps))
        self.log.config(state="disabled")

    def _append_truncation_notice(self, visible_count):
        if self.journal_filtered_count:
            self.log.insert(
                tk.END,
                f"\n[Chế độ Tóm tắt đã lọc {self.journal_filtered_count} sự kiện ít quan trọng]\n",
                ("header",),
            )
        if self.journal_truncated_count:
            self.log.insert(
                tk.END,
                f"[Vượt giới hạn lưu: đã bỏ {self.journal_truncated_count} sự kiện]\n",
                ("sa_reject",),
            )
        if self.log_total_count > visible_count:
            self.log.insert(
                tk.END,
                f"[Giao diện chỉ hiển thị {visible_count}/{self.log_total_count} dòng đã lưu]\n",
                ("header",),
            )

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
            self.status.config(text=f"Đã tìm thấy lời giải bằng {self.algo_var.get()}")
        else:
            self.status.config(text="Không tìm thấy lời giải")
        if self.solved and self.index == len(self.states) - 1:
            self.status.config(text="ĐÃ ĐẠT TRẠNG THÁI ĐÍCH")
        self.highlight_log()

    def highlight_log(self):
        if not self.log_ranges:
            return
        self.log.config(state="normal")
        self.log.tag_remove("active", "1.0", tk.END)
        log_index = None
        if not self.solved and self.index < len(self.log_ranges):
            log_index = self.index
        elif self.solved:
            current_state = self.states[self.index]
            matches = [i for i, state in enumerate(self.log_states) if state == current_state]
            if matches:
                log_index = matches[-1]
        if log_index is not None:
            s, e = self.log_ranges[log_index]
            self.log.tag_add("active", s, e)
            self.log.see(s)
        self.log.config(state="disabled")

    def on_click(self, e):
        if not self.log_ranges:
            return
        idx = self.log.index(f"@{e.x},{e.y}")
        for i, (s, e) in enumerate(self.log_ranges):
            if self.log.compare(idx, ">=", s) and self.log.compare(idx, "<", e):
                if not self.solved and i < len(self.states):
                    self.index = i
                    self.update()
                elif self.solved and i < len(self.log_states):
                    try:
                        self.index = self.states.index(self.log_states[i])
                    except ValueError:
                        return
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
