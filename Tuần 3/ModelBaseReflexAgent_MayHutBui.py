import random

model_state = None
last_action = None
visited = set()

opposite = {
    "Trai":"Phai",
    "Phai":"Trai",
    "Len":"Xuong",
    "Xuong":"Len"
}

def Pos_moves(x,y):
    moves=[]

    if y>0:
        moves.append("Trai")

    if y<3:
        moves.append("Phai")

    if x<3:
        moves.append("Xuong")

    if x>0:
        moves.append("Len")

    return moves


def next_pos(x,y,action):

    if action=="Trai":
        y-=1

    elif action=="Phai":
        y+=1

    elif action=="Xuong":
        x+=1

    elif action=="Len":
        x-=1

    return x,y


def print_matrix(matrix):

    for i in range(len(matrix)):

        for j in range(len(matrix[i])):
            print(matrix[i][j],end=" ")

        print()

    print()


def check(matrix):
    return all(cell==0 for row in matrix for cell in row)


def choose_action(x,y,moves):

    global last_action

    #tránh quay đầu
    if last_action!=None:

        back_move=opposite[last_action]

        if back_move in moves and len(moves)>1:
            moves.remove(back_move)

    #ưu tiên ô chưa đi
    new_moves=[]

    for move in moves:

        nx,ny=next_pos(x,y,move)

        if (nx,ny) not in visited:
            new_moves.append(move)
    if len(new_moves)>0:
        return random.choice(new_moves)
    return random.choice(moves)


def do_action(percept,x,y,step=0):

    global model_state
    global last_action

    while True:

        visited.add((x,y))

        print(f"Vị trí hiện tại: ({x},{y})")

        if percept[x][y]==1:

            print("Hành động: Hut")

            percept[x][y]=0
            model_state[x][y]=0

        else:

            model_state[x][y]=0

        print_matrix(percept)

        if check(percept):

            print(f"Đã sạch hết sau {step} bước.")
            break

        moves=Pos_moves(x,y)

        action=choose_action(x,y,moves)

        print("Di chuyển:",action)

        x,y=next_pos(x,y,action)

        last_action=action

        step+=1


if __name__=="__main__":

    percept=percept=[[1,1,1,1],[1,1,1,1],[1,1,1,0],[1,0,0,1]]

    model_state = [[None for _ in range(len(percept[0]))]
                   for _ in range(len(percept))
                   ]

    x=int(input("Nhập tọa độ x: "))
    y=int(input("Nhập tọa độ y: "))

    do_action(percept,x,y,step=0)