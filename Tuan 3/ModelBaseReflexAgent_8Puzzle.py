import random
import copy

visited=[]

goal=[
    [1,2,3],
    [4,5,6],
    [7,8,0]
]

def print_board(board):

    for i in range(len(board)):

        for j in range(len(board[i])):
            print(board[i][j],end=" ")

        print()

    print()


def find_zero(board):

    for i in range(3):

        for j in range(3):

            if board[i][j]==0:
                return i,j


def Pos_moves(x,y):

    moves=[]

    if y>0:
        moves.append("Trai")

    if y<2:
        moves.append("Phai")

    if x>0:
        moves.append("Len")

    if x<2:
        moves.append("Xuong")

    return moves


def move(board,action):

    new_board=copy.deepcopy(board)

    x,y=find_zero(new_board)

    if action=="Trai":
        nx,ny=x,y-1

    elif action=="Phai":
        nx,ny=x,y+1

    elif action=="Len":
        nx,ny=x-1,y

    elif action=="Xuong":
        nx,ny=x+1,y

    new_board[x][y],new_board[nx][ny] = \
    new_board[nx][ny],new_board[x][y]

    return new_board


def check(board):

    return board==goal


def board_to_tuple(board):

    return tuple(tuple(row) for row in board)


def do_action(board,step=0):

    while True:

        print("Trạng thái hiện tại:")
        print_board(board)

        if check(board):

            print(f"Đã giải xong sau {step} bước.")
            break

        visited.append(board_to_tuple(board))

        x,y=find_zero(board)

        moves=Pos_moves(x,y)

        possible=[]

        # ưu tiên trạng thái chưa đi
        for action in moves:

            new_board=move(board,action)

            if board_to_tuple(new_board) not in visited:
                possible.append(action)

        if len(possible)>0:
            action=random.choice(possible)

        else:
            action=random.choice(moves)

        print("Hành động:",action)

        board=move(board,action)

        step+=1


if __name__=="__main__":

    board=[
        [1,2,3],
        [4,0,6],
        [7,5,8]
    ]

    do_action(board)