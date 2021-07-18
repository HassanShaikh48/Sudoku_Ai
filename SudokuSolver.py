from operator import attrgetter


class Solver:
    def checkvalidpuzzle(self, arr):
        subsquarestartingpoints = [[0, 0], [0, 3], [0, 6], [3, 0], [3, 3], [3, 6], [6, 0], [6, 3], [6, 6]]
        # Checking row validity of every row
        for row in range(9):
            has = set()
            for col in range(9):
                if arr[row][col] == 0:
                    continue
                if arr[row][col] in has:
                    return False
                has.add(arr[row][col])
        # Checking column validity of every column
        for col in range(9):
            has = set()
            for row in range(9):
                if arr[row][col] == 0:
                    continue
                if arr[row][col] in has:
                    return False
                has.add(arr[row][col])
        # Checking box validity
        for pointrow, pointcol in subsquarestartingpoints:
            has = set()
            for row in range(3):
                for col in range(3):
                    if arr[pointrow+row][pointcol+col] == 0:
                        continue
                    if arr[pointrow+row][pointcol+col] in has:
                        return False
                    has.add(arr[pointrow+row][pointcol+col])
        return True

    def print_board(self, arr):
        for i in range(9):
            for j in range(9):
                if arr[i][j]==0:
                    print("_", end=" ")
                else:
                    print(arr[i][j], end=" ")
            print("")

    @staticmethod
    def solve_sudoku(arr):
        """
        To convert to an exact cover problem, create a binary matrix.


        729 options

        Each cell can be filled with any number between 1 and 9.
        324 constraints
        1. Each row must contain all of the numbers 1 through 9, for a total of 81.
        2. All values from 1 to 9 must be present in each column, for a total of 81.
        3. Each block must contain all of the numbers 1 through 9, for a total of 81.
        4. Fill each cell, for a total of 81.

        The options are arranged in the following order: row > col > value.
        The constraints are arranged in the following order.
        """
        # Represent the binary matrix as sparse matrix (has < 729 * 4 ones in a matrix of 729 * 342)
        positions = []

        def add_position(ch, r, c, x):
            positions.append([ch, [
                9 * r + x,  # Row constraint
                81 + 9 * c + x,  # Col constraint
                162 + 9 * ((r // 3) * 3 + (c // 3)) + x,  # Block constraint
                243 + 9 * r + c  # Cell constraint
            ]])

        choice_row = 0
        for i in range(9):  # Row
            for j in range(9):  # Column
                if arr[i][j] == 0:
                    for k in range(9):  # Value
                        add_position(choice_row, i, j, k)
                        choice_row += 1
                else:
                    k = arr[i][j] - 1
                    add_position(choice_row + k, i, j, k)
                    choice_row += 9
        alg_x = AlgorithmX(324, positions)
        if not alg_x.solve():
            return False
        rows = alg_x.solution
        if len(rows) != 81:
            return False
        for row in rows:
            i, row = divmod(row, 81)
            j, value = divmod(row, 9)
            arr[i][j] = value + 1  # value is 0-8
        return True


class AlgorithmXNode:
    def __init__(self, value=0):
        """
        Make a node that has self-links. value of param: It has a variety of uses:
        - there isn't anything for the root node
        - the total number of cells in each header node's column
        - in all other nodes, the row id
        """
        self.value = value
        self.left = self.right = self.up = self.down = self.top = self

    def insert_h(self):
        """
        Using left and right connections, place this node in the row.
        """
        self.left.right = self.right.left = self

    def insert_v(self, update_top=True):
        """
        Put this node to the column.
        :update top is a parameter. If true, the header counter should be updated.
        """
        self.up.down = self.down.up = self
        if update_top:
            self.top.value += 1

    def insert_above(self, node):
        """
        Update the top by inserting this node above the provided node in the column.
        """
        self.top = node.top
        self.up = node.up
        self.down = node
        self.insert_v()

    def insert_after(self, node):
        """
        This node should be placed to the right of the provided node.
        """
        self.right = node.right
        self.left = node
        self.insert_h()

    def remove_h(self):
        """
        This node should be removed from the row. Insert h is the inverse of inser_ h.
        """
        self.left.right = self.right
        self.right.left = self.left

    def remove_v(self, update_top=True):
        """
        This node should be removed from the column. If true, update the counter in the
        header.
        :param update top: If true, update the counter in the header.
        """
        self.up.down = self.down
        self.down.up = self.up
        if update_top:
            self.top.value -= 1

    def cover(self):
        self.top.remove_h()
        for row in self.top.loop('down'):
            for node in row.loop('right'):
                node.remove_v()

    def uncover(self):
        for row in self.top.loop('up'):
            for node in row.loop('left'):
                node.insert_v()
        self.top.insert_h()

    def loop(self, direction):
        """
        :return: Nodes from self to self (both exclusive), one at a time. :param direction:
        One of 'left', 'right', 'up', 'down'. :param direction: One of 'left', 'right', 'up', 'down'.
        """
        if direction not in {'left', 'right', 'up', 'down'}:
            raise ValueError(f"Direction must be one of 'left', 'right', 'up', 'down', got {direction}")
        next_node = attrgetter(direction)
        node = next_node(self)
        while node != self:
            yield node
            node = next_node(node)


class AlgorithmX:
    """
    To solve a constraint fulfilment problem represented in the form of Exact Cover,
    use Algorithm X with dancing connections.
    """

    def __init__(self, constraint_count, matrix):
        matrix.sort()
        headers = [AlgorithmXNode() for _ in range(constraint_count)]
        for row, cols in matrix:
            first = None  # first node in row
            for col in cols:
                node = AlgorithmXNode(row)
                # Insert in column
                node.insert_above(headers[col])
                # Insert in row
                if first is None:
                    first = node
                else:
                    node.insert_after(first)
        # Header row
        self.root = AlgorithmXNode()
        last = self.root
        for header in headers:
            header.insert_after(last)
            last = header
        self.solution = []

    def solve(self):
        if self.root.right == self.root:
            # All constraints have been satisfied
            return True
        # Find column with least number of nodes
        header = min(self.root.loop('right'), key=attrgetter('value'))
        if header.value == 0:
            # No valid solution exists
            return False
        header.cover()
        for row in header.loop('down'):
            for node in row.loop('right'):
                node.cover()
            if self.solve():
                # Add row to solution
                self.solution.append(row.value)
                return True
            # Try a different value
            for node in row.loop('left'):
                node.uncover()
        header.uncover()
        # Backtrack
        return False
