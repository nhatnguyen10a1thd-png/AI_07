# ai/uninformed/dfs.py
import time
from ai.utils import SearchNode, reconstruct_path
from ai.search_result import SearchResult
from ai.limits import SearchLimit

def dfs_solve(start_state, rules, max_depth=100, max_nodes=20000, max_seconds=3.0):
    """Solves the puzzle using Depth-First Search (DFS) with a maximum depth limit."""
    start_time = time.time()
    
    start_node = SearchNode(start_state)
    if start_state.is_goal():
        return SearchResult(
            algorithm="DFS",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=[(0, "Start (Goal reached immediately)", start_state)]
        )

    # Frontier is a LIFO stack
    frontier = [start_node]
    explored = set()
    frontier_encoded = {start_state.encode()}
    
    steps = [(0, "Start", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1
    limit = SearchLimit(max_nodes, max_seconds)

    while frontier:
        if limit.reached(generated_count):
            break
        node = frontier.pop()
        node_encoded = node.state.encode()
        frontier_encoded.discard(node_encoded)
        explored.add(node_encoded)
        visited_count += 1

        if node.state.is_goal():
            actions, _ = reconstruct_path(node)
            return SearchResult(
                algorithm="DFS",
                solved=True,
                path=actions,
                visited_count=visited_count,
                generated_count=generated_count,
                elapsed_time=time.time() - start_time,
                steps=steps
            )

        # Apply depth limit to prevent deep paths that are suboptimal or infinite
        if node.depth >= max_depth:
            continue

        for action in rules.legal_actions(node.state):
            next_state = rules.apply_action(node.state, action)
            next_encoded = next_state.encode()

            if next_encoded not in explored and next_encoded not in frontier_encoded:
                child = SearchNode(
                    state=next_state,
                    parent=node,
                    action=action,
                    path_cost=node.path_cost + 1,
                    depth=node.depth + 1
                )
                generated_count += 1
                steps.append((step_num, f"{action[0]} {action[1]} (depth={child.depth})", next_state))
                step_num += 1

                if next_state.is_goal():
                    actions, _ = reconstruct_path(child)
                    return SearchResult(
                        algorithm="DFS",
                        solved=True,
                        path=actions,
                        visited_count=visited_count,
                        generated_count=generated_count,
                        elapsed_time=time.time() - start_time,
                        steps=steps
                    )

                frontier.append(child)
                frontier_encoded.add(next_encoded)

    return SearchResult(
        algorithm="DFS",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps
    )
