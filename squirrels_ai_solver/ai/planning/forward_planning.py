# ai/planning/forward_planning.py
import time
from collections import deque
from ai.utils import SearchNode, reconstruct_path
from ai.search_result import SearchResult
from ai.limits import SearchLimit


def forward_planning_solve(start_state, rules, max_nodes=20000, max_seconds=3.0):
    """
    Forward State-Space Planning.

    Xuất phát từ trạng thái ban đầu (Initial State), áp dụng các hành động hợp lệ
    để sinh ra các trạng thái kế tiếp, tiến dần về phía Goal State.

    Khác với BFS thuần túy:
    - Log mô tả rõ "Plan Step" thay vì "depth"
    - Mô tả kế hoạch hành động theo ngôn ngữ planning (preconditions / effects)
    - Lưu "kế hoạch" (plan) thay vì "đường đi" (path)

    Thuật toán:
    1. Khởi tạo plan_queue chứa (state, plan_so_far)
    2. Khởi tạo visited = {initial_state}
    3. TRONG KHI plan_queue không rỗng:
       a. Lấy (state, plan) ra khỏi queue
       b. Nếu state là GOAL: trả về plan
       c. Với mỗi hành động hợp lệ (piece, direction):
          - Kiểm tra precondition: hành động có hợp lệ không?
          - Apply action → next_state (effect)
          - Nếu next_state chưa thăm → thêm vào queue
    4. Nếu queue rỗng: thất bại
    """
    start_time = time.time()

    if start_state.is_goal():
        return SearchResult(
            algorithm="Forward Planning",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=[(0, "Initial State là Goal State — Plan rỗng (trivially solved)", start_state)]
        )

    steps = [(0, "📋 PLANNING: Khởi tạo Initial State", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1

    # Plan queue: each entry = (current_state, plan_list, parent_node)
    # We use SearchNode for path reconstruction
    start_node = SearchNode(start_state)
    frontier = deque([start_node])
    visited = {start_state.encode()}
    limit = SearchLimit(max_nodes, max_seconds)

    while frontier:
        if limit.reached(generated_count):
            break
        node = frontier.popleft()
        visited_count += 1

        # Check GOAL condition
        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            steps.append((step_num,
                          f"🎯 PLAN FOUND! Kế hoạch gồm {len(actions)} hành động",
                          node.state))
            return SearchResult(
                algorithm="Forward Planning",
                solved=True,
                path=actions,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps
            )

        # Generate applicable actions (check preconditions)
        applicable = rules.legal_actions(node.state)
        plan_step = node.depth + 1

        for action in applicable:
            pid, direction = action

            # --- PRECONDITION CHECK (already done by rules.legal_actions) ---
            # Explicit description for planning log
            precond_ok = rules.can_move(node.state, pid, direction)
            if not precond_ok:
                continue  # Precondition not satisfied

            # --- APPLY ACTION (effect) ---
            next_state = rules.apply_action(node.state, action)
            next_encoded = next_state.encode()
            generated_count += 1

            if next_encoded in visited:
                continue

            visited.add(next_encoded)

            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1,
                depth=node.depth + 1
            )

            # Count acorns dropped so far for planning description
            dropped = len(next_state.filled_holes)
            total_squirrels = sum(
                1 for p in next_state.pieces.values() if p.type == "squirrel"
            )

            steps.append((
                step_num,
                f"Plan {plan_step}: [{pid.upper()} → {direction}] | Hạt rơi: {dropped}/{total_squirrels}",
                next_state
            ))
            step_num += 1

            # Early goal check
            if next_state.is_goal():
                actions, _ = reconstruct_path(child)
                steps.append((step_num,
                              f"🎯 GOAL REACHED! Kế hoạch gồm {len(actions)} hành động",
                              next_state))
                return SearchResult(
                    algorithm="Forward Planning",
                    solved=True,
                    path=actions,
                    visited_count=visited_count,
                    generated_count=generated_count,
                    elapsed_time=time.time() - start_time,
                    steps=steps
                )

            frontier.append(child)

    # Planning failed
    return SearchResult(
        algorithm="Forward Planning",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps
    )
