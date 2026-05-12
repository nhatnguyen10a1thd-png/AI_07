import random


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
def do_action(percept,x,y,step=0):
        
        # Kiểm tra điều kiện dừng: sạch hết
        if all(cell == 0 for row in percept for cell in row):
            print(f"Đã sạch hết sau {step} bước.")
            print_matrix(percept)
            return
        if percept[x][y]==1:
            percept[x][y]=0
            moves=Pos_moves(x,y)
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
            moves=Pos_moves(x,y)
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
        print("Hành đồng:",action)
        print_matrix(percept)
        do_action(percept,x,y,step)

if __name__=="__main__":
    percept=[[1,1,1,0],[0,1,0,0],[1,0,1,0],[0,0,0,1]]
    x=int(input("Nhập tọa độ x: "))
    y=int(input("Nhập tọa độ y: "))
    do_action(percept,x,y,step=0)
    
            