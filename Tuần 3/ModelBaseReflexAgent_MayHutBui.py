import random

model_state = None
last_action = None  # nhớ nước đi trước đó

def Pos_moves(x,y):
    moves=[]
    if y>0:moves.append("Trai")
    if y<3:moves.append("Phai")
    if x<3:moves.append("Xuong")
    if x>0 :moves.append("Len")
    return moves

def print_matrix(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            print(matrix[i][j], end=" ")
        print()
    print()

def check(matrix):
    return all(cell == 0 for row in matrix for cell in row)

def do_action(percept,x,y,step=0):
        global model_state, last_action

        if check(percept):
            print(f"Đã sạch hết sau {step} bước.")
            print_matrix(percept)
            return

        moves=Pos_moves(x,y)

        if last_action in moves and len(moves) > 1:
            moves.remove(last_action)

        if percept[x][y]==1:
            percept[x][y]=0
            model_state[x][y]=0
            action=random.choice(moves)
            if action=="Trai":
                y-=1
            elif action=="Phai":
                y+=1
            elif action=="Xuong":
                x+=1
            elif action=="Len":  
                x-=1
        else:
            action=random.choice(moves)
            if action=="Trai":
                y-=1
            elif action=="Phai":
                y+=1
            elif action=="Xuong":
                x+=1
            elif action=="Len":  
                x-=1
        step=step+1
        last_action = action
        print("Hành đồng:",action)
        print_matrix(percept)
        do_action(percept,x,y,step)

if __name__=="__main__":
    percept=[[1,1,1,0],[0,1,0,0],[1,0,1,0],[0,0,0,1]]

    model_state = [[None for _ in range(len(percept[0]))] for _ in range(len(percept))]

    x=int(input("Nhập tọa độ x: "))
    y=int(input("Nhập tọa độ y: "))
    do_action(percept,x,y,step=0)