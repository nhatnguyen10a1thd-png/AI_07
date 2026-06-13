# ai/complex/and_or_search.py
import time
from ai.search_result import SearchResult

def and_or_solve(start_state, rules, max_depth=8):
    """
    Solves the puzzle using AND-OR Graph Search.
    Environment is non-deterministic: sliding a piece can result in moving 1 cell or 2 cells (if empty).
    Returns a conditional plan tree.
    """
    start_time = time.time()
    steps = [(0, "Bắt đầu AND-OR Graph Search (Trượt ngẫu nhiên 1 hoặc 2 ô)", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [0]

    # Helper: Non-deterministic outcomes of an action
    def get_outcomes(state, action):
        # Outcome 1: Move 1 cell (standard)
        st1 = rules.apply_action(state, action)
        
        # Outcome 2: Move 2 cells (slippery floor - if the path ahead is still clear)
        pid, direction = action
        st2 = st1
        if rules.can_move(st1, pid, direction):
            st2 = rules.apply_action(st1, action)
            
        # If the state is the same, only return one outcome
        if st1.encode() == st2.encode():
            return [st1]
        return [st1, st2]

    # Recursive AND-OR Search
    def search(state, visited_states, depth):
        visited_count[0] += 1
        
        if state.is_goal():
            return "Goal reached"
            
        if depth >= max_depth:
            return "Failure: depth limit"
            
        state_encoded = state.encode()
        if state_encoded in visited_states:
            return "Failure: cycle"
            
        visited_states.add(state_encoded)
        
        legal_actions = rules.legal_actions(state)
        # Try each action (OR branch)
        for action in legal_actions:
            outcomes_list = get_outcomes(state, action)
            generated_count[0] += len(outcomes_list)
            
            # Log the step
            desc = f"OR: Chọn {action[0]} {action[1]} → Có {len(outcomes_list)} kết quả khả thi (AND)"
            steps.append((step_num[0], desc, outcomes_list[0]))
            step_num[0] += 1
            
            plan = {}
            possible = True
            
            # Check all outcomes (AND branch)
            for out_state in outcomes_list:
                subplan = search(out_state, visited_states, depth + 1)
                if "Failure" in str(subplan):
                    possible = False
                    break
                plan[out_state.encode()] = subplan
                
            if possible:
                visited_states.remove(state_encoded)
                return {
                    "action": action,
                    "conditional_plan": plan
                }
                
        visited_states.remove(state_encoded)
        return "Failure"

    visited = set()
    result_plan = search(start_state, visited, 0)
    solved = not isinstance(result_plan, str) or "Failure" not in result_plan

    # Extract a linear sample path from the plan for demonstration in the visualizer
    sample_path = []
    if solved and isinstance(result_plan, dict):
        curr_plan = result_plan
        curr_state = start_state
        while isinstance(curr_plan, dict) and "action" in curr_plan:
            act = curr_plan["action"]
            sample_path.append(act)
            outcomes = get_outcomes(curr_state, act)
            # Pick standard 1-cell outcome as representative
            curr_state = outcomes[0]
            curr_plan = curr_plan["conditional_plan"].get(curr_state.encode())

    # Format result details
    extra_info = {"plan_tree": str(result_plan)}
    
    return SearchResult(
        algorithm="AND-OR Search",
        solved=solved,
        path=sample_path,
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra=extra_info
    )
