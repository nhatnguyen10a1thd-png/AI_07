from tkinter import *
from tkinter import messagebox


class Node:

    def __init__(self, state, x, y, depth, action):

        self.state = state
        self.x = x
        self.y = y
        self.depth = depth
        self.action = action

goal = [
    [1,2,3],
    [4,5,6],
    [7,8,0]
]
logs = []

def isGoal(state):

    return state == goal

def copyState(state):
    newState = []
    for row in state:
        newState.append(row[:])
    return newState

def isCycle(visited, state):
    for v in visited:
        if v == state:
            return True
    return False

def expand(node):
    children = []
    directions = [
        (-1, 0, "Di len"),
        (1, 0, "Di xuong"),
        (0, -1, "Qua trai"),
        (0, 1, "Qua phai")

    ]
    for dx, dy, action in directions:
        nx = node.x + dx
        ny = node.y + dy
        if nx >= 0 and nx < 3 and ny >= 0 and ny < 3:
            newState = copyState(node.state)
            newState[node.x][node.y], newState[nx][ny] = \
            newState[nx][ny], newState[node.x][node.y]
            child = Node(
                newState,
                nx,
                ny,
                node.depth + 1,
                action

            )
            children.append(child)
    return children


def printState(state):
    s = ""
    for row in state:
        s += str(row) + "\n"
    return s

def depthLimitedSearch(start, limit):
    frontier = []
    frontier.append(start)
    visited = []
    step = 1
    result = "failure"
    while len(frontier) > 0:
        node = frontier.pop()
        if isGoal(node.state):
            logs.append("Tim thay dich!\n")
            return node
        if node.depth > limit:
            result = "cutoff"
        elif not isCycle(visited, node.state):
            visited.append(node.state)
            children = expand(node)
            for child in children:
                text = ""
                text += "Do sau: " + str(limit) + "\n"
                text += "Buoc " + str(step) + ": "
                text += child.action + "\n"
                text += printState(child.state)
                text += "----------------------\n"
                logs.append(text)
                step += 1
                frontier.append(child)
    return result

def iterativeDeepeningSearch(start):
    logs.clear()
    for depth in range(5):
        logs.append("\n-------------------------\n")
        logs.append("DO SAU " + str(depth) + "\n")
        logs.append("-------------------------\n\n")
        result = depthLimitedSearch(start, depth)
        if result != "cutoff":
            if result != "failure":
                logs.append("Da tim thay loi giai!\n")
            break
    output.delete(1.0, END)
    for log in logs:
        output.insert(END, log)

def solvePuzzle():
    try:
        state = [
            [int(e1.get()), int(e2.get()), int(e3.get())],
            [int(e4.get()), int(e5.get()), int(e6.get())],
            [int(e7.get()), int(e8.get()), int(e9.get())]
        ]
        x = 0
        y = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    x = i
                    y = j
        start = Node(
            state,
            x,
            y,
            0,
            "Bat dau"
        )
        iterativeDeepeningSearch(start)
    except:
        messagebox.showerror(
            "Loi",
            "Nhap du lieu khong hop le!"
        )

root = Tk()
root.title("8 Puzzle - IDS")
root.geometry("800x700")

title = Label(
    root,
    text="8 Puzzle - Iterative Deepening Search",
    font=("Arial", 18, "bold")
)

title.pack(pady=10)
frame = Frame(root)
frame.pack(pady=10)

e1 = Entry(frame, width=5, font=("Arial", 20))
e2 = Entry(frame, width=5, font=("Arial", 20))
e3 = Entry(frame, width=5, font=("Arial", 20))

e4 = Entry(frame, width=5, font=("Arial", 20))
e5 = Entry(frame, width=5, font=("Arial", 20))
e6 = Entry(frame, width=5, font=("Arial", 20))

e7 = Entry(frame, width=5, font=("Arial", 20))
e8 = Entry(frame, width=5, font=("Arial", 20))
e9 = Entry(frame, width=5, font=("Arial", 20))


e1.grid(row=0, column=0, padx=5, pady=5)
e2.grid(row=0, column=1, padx=5, pady=5)
e3.grid(row=0, column=2, padx=5, pady=5)

e4.grid(row=1, column=0, padx=5, pady=5)
e5.grid(row=1, column=1, padx=5, pady=5)
e6.grid(row=1, column=2, padx=5, pady=5)

e7.grid(row=2, column=0, padx=5, pady=5)
e8.grid(row=2, column=1, padx=5, pady=5)
e9.grid(row=2, column=2, padx=5, pady=5)


e1.insert(0, "1")
e2.insert(0, "2")
e3.insert(0, "3")

e4.insert(0, "4")
e5.insert(0, "0")
e6.insert(0, "6")

e7.insert(0, "7")
e8.insert(0, "5")
e9.insert(0, "8")

btn = Button(
    root,
    text="Giai IDS",
    font=("Arial", 14),
    command=solvePuzzle
)
btn.pack(pady=10)

output = Text(
    root,
    width=80,
    height=25,
    font=("Consolas", 11)
)

output.pack(pady=10)

root.mainloop()