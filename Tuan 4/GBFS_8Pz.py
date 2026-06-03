import heapq
import copy
import random


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


def Greedy_Search(problem):
    """Greedy Search: chọn trạng thái có h(n) nhỏ nhất"""
    start_node = Node(problem.initial)

    frontier = []
    priority = manhattan_distance(start_node.state, problem.goal)
    heapq.heappush(frontier, (priority, id(start_node), start_node))

    reached = set()
    frontier_state = {state_to_tuple(start_node.state)}

    while frontier:
        _, _, node = heapq.heappop(frontier)
        node_key = state_to_tuple(node.state)
        frontier_state.discard(node_key)

        if problem.goal_test(node.state):
            return solution(node)

        reached.add(node_key)

        for action in problem.actions(node.state):
            child = child_node(problem, node, action)
            child_key = state_to_tuple(child.state)

            if child_key not in frontier_state and child_key not in reached:
                priority = manhattan_distance(child.state, problem.goal)
                heapq.heappush(frontier, (priority, id(child), child))
                frontier_state.add(child_key)

    return None, None


def print_state(state):
    for row in state:
        print(row)
    print("---")


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

    actions, states = Greedy_Search(problem)

    if actions is None:
        print("Không tìm thấy lời giải")
    else:
        print(f"Tổng số bước: {len(actions)}")
        print("Chuỗi hành động:", " -> ".join(actions))
        for state in states:
            print_state(state)
