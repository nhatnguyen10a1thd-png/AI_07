import random

def interpret_input(percept):
    for i in range(len(percept)):
        for j in range(len(percept[i])):
            if percept[i][j] == 0:
                return i, j

def Pos_move(i, j):
    move=[]
    if i + 1 <= 2:  # Đi XUỐNG
        move.append("Xuong")
    if i - 1 >= 0:  # Đi LÊN
        move.append("Len")
    if j + 1 < 2:  # Đi PHẢI
        move.append("Phai")
    if j - 1 >= 0:  # Đi TRÁI
        move.append("Trai")
    return move

def check(matrix):
    goal = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]
    return matrix == goal

def do_action(i,j,percept,step=0):
    if check(percept):
        print(f"Đã đạt trạng thái mục tiêu sau {step} bước!")
        return
    moves=Pos_move(i, j)
    action=random.choice(moves)
    if action=="Xuong":
        percept[i][j], percept[i+1][j] = percept[i+1][j], percept[i][j]
        i+=1
    elif action=="Len":
        percept[i][j], percept[i-1][j] = percept[i-1][j], percept[i][j]
        i-=1
    elif action=="Phai": 
        percept[i][j], percept[i][j+1] = percept[i][j+1], percept[i][j]
        j+=1
    elif action=="Trai":
        percept[i][j], percept[i][j-1] = percept[i][j-1], percept[i][j]
        j-=1
    print(f"Step {step+1}: Đi {action}")
    print_matrix(percept)
    step+=1
    do_action(i, j, percept, step)
    
def print_matrix(matrix, title=""):
    if title:
        print(title)
    for row in matrix:
        for val in row:
            print("_" if val == 0 else val, end=" ")
        print()
    print()

def Simple_reflex_agent(percept):
    print_matrix(percept, "=== Trạng thái ban đầu ===")

    # state ← INTERPRET-INPUT(percept)
    i, j = interpret_input(percept)
    print(f"Vị trí ô trống: hàng {i}, cột {j}\n")

    # rule ← RULE-MATCH(state, rules)
    

    # action ← rule.ACTION
    do_action(i, j, percept)



# ========== MAIN ==========
if __name__ == "__main__":
    percept = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]
    Simple_reflex_agent(percept)