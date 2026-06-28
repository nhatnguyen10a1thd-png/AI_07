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


def isGoal(state):

    return state == goal


def printState(state):

    for row in state:
        print(row)

    print()


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


# function DEPTH-LIMITED-SEARCH(problem, l)

def depthLimitedSearch(start, limit):

    # frontier ← a LIFO queue (stack)

    frontier = []

    frontier.append(start)

    # result ← failure

    result = "failure"

    visited = []

    step = 1

    # while not IS-EMPTY(frontier)

    while len(frontier) > 0:

        # node ← POP(frontier)

        node = frontier.pop()

        # if problem.IS-GOAL(node.STATE)

        if isGoal(node.state):

            print("Tim thay dich!\n")
            return node

        # if DEPTH(node) > l

        if node.depth > limit:

            result = "cutoff"

        # else if not IS-CYCLE(node)

        elif not isCycle(visited, node.state):

            visited.append(node.state)

            # for each child in EXPAND(problem, node)

            children = expand(node)

            for child in children:

                print("Buoc", step, ":", child.action)

                printState(child.state)

                step += 1

                # add child to frontier

                frontier.append(child)

    return result


# function ITERATIVE-DEEPENING-SEARCH(problem)

def iterativeDeepeningSearch(start):

    # for depth = 0 to ∞

    for depth in range(1000000):

        print("\n===================")
        print("DO SAU", depth)
        print("===================\n")

        result = depthLimitedSearch(start, depth)

        # if result ≠ cutoff then return result

        if result != "cutoff":

            if result != "failure":

                print("Da tim thay loi giai!")

            return


start = Node(

    [
        [2,1,3],
        [4,5,6],
        [7,8,0]
    ],

    2,
    2,
    0,
    "Bat dau"

)

iterativeDeepeningSearch(start)