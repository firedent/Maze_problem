# Insert your code here
from queue_adt import *


class MazeError(Exception):
    pass


class InnerPoint:
    def __init__(self, x, y, raw):
        directions = {
            0: 'NW',
            1: 'W',
            2: 'N',
            3: '',
        }
        self.x = x
        self.y = y
        self.raw = raw
        self.direction = directions[raw]

    def __repr__(self):
        return f'InnerPoint({self.x}, {self.y}, {self.raw})'


class Point:
    def __init__(self):
        self.connect = ''

    def __repr__(self):
        return f'Point({self.direction})'


class Maze:
    def __init__(self, filename):
        """
        >>> m = Maze('incorrect_input_1.txt')
        Traceback (most recent call last):
        maze.MazeError: Incorrect input.
        >>> m = Maze('incorrect_input_2.txt')
        Traceback (most recent call last):
        maze.MazeError: Incorrect input.
        >>> m = Maze('not_a_maze_1.txt')
        Traceback (most recent call last):
        maze.MazeError: Input does not represent a maze.
        >>> m = Maze('not_a_maze_2.txt')
        Traceback (most recent call last):
        maze.MazeError: Input does not represent a maze.
        >>> m = Maze('maze_1.txt')
        >>> m.grid_maze_raw[0][7]
        0
        >>> m.grid_maze_raw[5][0]
        1
        >>> m.grid_maze_raw[4][6]
        3
        >>> m.grid_maze_raw[0][7]
        0
        """
        with open(filename) as f:
            lines = f.read().splitlines()
        # 找长度
        length = 0
        grid_maze_raw = []
        for line in lines:
            # 去除空格
            line = line.replace(' ', '')
            # 如果当前行不是空行
            if len(line) is not 0:
                # 如果之前length的长度是0，把当前行的长度赋值给length
                if length is 0:
                    length = len(line)
                # 如果length已经不是0了，比较当前行的长度是否等于之前的长度，不等于就抛出异常
                elif len(line) != length:
                    # print('两行长度不相等')
                    raise MazeError('Incorrect input.')
                # 看看当前行里的数字有没有超过范围
                if length > 31 or length < 2:
                    # print(f'每行数字超限{length}')
                    raise MazeError('Incorrect input.')
                ele = []
                # str -> int & 分离数字
                for i in line:
                    i_int = int(i)
                    if i_int in {0, 1, 2, 3}:
                        ele.append(i_int)
                    # 如果不是那几个数，就抛出异常
                    else:
                        print('数字不存在{0,1,2,3}')
                        raise MazeError('Incorrect input.')
                # 每行最后一位不可能是1或3
                if ele[-1] == 1 or ele[-1] == 3:
                    raise MazeError('Input does not represent a maze.')
                grid_maze_raw.append(ele)
            # 判断当前已经多少行了
            if len(grid_maze_raw) > 41:
                # print(f'行数太多,{len(grid_maze_raw)}')
                raise MazeError('Incorrect input.')
        # 判断全部加载完之后，是否到达允许的最小行数
        if len(grid_maze_raw) < 2:
            # print(f'行数太少,{len(grid_maze_raw)}')
            raise MazeError('Incorrect input.')
        # 最后一行不可能是2或3
        if 2 in grid_maze_raw[-1] or 3 in grid_maze_raw[-1]:
            raise MazeError('Input does not represent a maze.')
        self.grid_maze_raw = grid_maze_raw
        self.x_dim = length
        self.y_dim = len(grid_maze_raw)
        self.grid_point_no_object = None
        self.grid_inner_point_no_object = None

    def __int_grid(self, directions):
        """
        >>> m = Maze('maze_1.txt')
        >>> p = m._Maze__int_grid({0: '',1: 'E',2: 'S',3: 'SE'})
        >>> ip = m._Maze__int_grid({0: 'NW',1: 'W',2: 'N',3: ''})
        >>> ip[6][4]
        'S'
        >>> ip[5][1]
        'NW'
        >>> ip[4][4]
        'W'
        >>> ip[0][0]
        'WE'
        >>> ip[1][0]
        'NWS'
        >>> p[0][0]
        'E'
        >>> p[7][0]
        'W'
        >>> p[7][5]
        'N'
        >>> p[0][5]
        'NE'
        >>> m = Maze('bianjie.txt')
        >>> p = m._Maze__int_grid({0: '',1: 'E',2: 'S',3: 'SE'})
        >>> ip = m._Maze__int_grid({0: 'NW',1: 'W',2: 'N',3: ''})
        >>> ip[0][0]
        'NW'
        >>> p[0][0]
        ''
        >>> p[1][1]
        'WN'
        """
        grid = [[''] * self.y_dim for _ in range(self.x_dim)]
        operations = {
            'S': lambda p: (p[0], p[1] + 1, 'N'),
            'E': lambda p: (p[0] + 1, p[1], 'W'),
            'N': lambda p: (p[0], p[1] - 1, 'S'),
            'W': lambda p: (p[0] - 1, p[1], 'E'),
        }
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                # grid_inner_point_no_object[x][y] = directions[self.get_inner_point(x, y)]
                # 遍历本节点可以指向的方向
                for d in directions[self.get_inner_point(x, y)]:
                    # 一次添加本节点可以指向的方向
                    grid[x][y] += d
                    # pre用来接收返回的 指向的方向的下一个节点的坐标和下一个节点的指向方向
                    pre = operations[d]((x, y))
                    if 0 <= pre[0] <= self.x_dim - 1 and 0 <= pre[1] <= self.y_dim - 1:
                        # 将下一个节点的指向方向添加进去
                        grid[pre[0]][pre[1]] += pre[2]
        return grid

    def __get_children(self, x, y, grid):
        children = list()
        operators = {
            'N': lambda p: (p[0], y - 1),
            'S': lambda p: (p[0], p[1] + 1),
            'W': lambda p: (p[0] - 1, p[1]),
            'E': lambda p: (p[0] + 1, p[1]),
        }
        direction = grid[x][y]
        for d in direction:
            children.append(operators[d]((x, y)))
        return children

    def __traversal_by_bfs(self, x, y, grid):
        """
        >>> m = Maze('maze_1.txt')
        >>> m.grid_point_no_object = m._Maze__int_grid({0: '',1: 'E',2: 'S',3: 'SE'})
        >>> m.grid_inner_point_no_object = m._Maze__int_grid({0: 'NW',1: 'W',2: 'N',3: ''})
        >>> sorted(m._Maze__traversal_by_bfs(4,2,m.grid_point_no_object))
        [(2, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 2), (4, 1), (4, 2), (4, 3), (5, 2), (6, 0), (6, 1), (6, 2), (7, 0)]
        >>> sorted(m._Maze__traversal_by_bfs(1,3,m.grid_point_no_object))
        [(1, 3)]
        >>> sorted(m._Maze__traversal_by_bfs(2,0,m.grid_inner_point_no_object))
        [(2, 0), (2, 1), (3, 1)]
        >>> sorted(m._Maze__traversal_by_bfs(3,0,m.grid_inner_point_no_object))
        [(3, 0), (4, 0), (4, 1), (5, 0), (5, 1)]
        >>> sorted(m._Maze__traversal_by_bfs(0,1,m.grid_inner_point_no_object))
        [(0, 1)]
        """
        visited_point = set()
        q = Queue()
        q.enqueue((x, y))
        while not q.is_empty():
            p = q.dequeue()
            visited_point.add(p)
            for c in self.__get_children(p[0], p[1], grid):
                if 0 <= c[0] <= self.x_dim - 1 and 0 <= c[1] <= self.y_dim - 1:
                    if (c[0], c[1]) not in visited_point:
                        q.enqueue(c)

        # 返回的set包含起始节点本身
        return visited_point

    def get_inner_point(self, x, y):
        return self.grid_maze_raw[y][x]

    def analyse(self):
        """
        >>> maze = Maze('maze_1.txt')
        >>> maze.analyse()
        The maze has 12 gates.
        The maze has 8 sets of walls that are all connected.
        >>> maze = Maze('maze_2.txt')
        >>> maze.analyse()
        The maze has 20 gates.
        The maze has 4 sets of walls that are all connected.
        >>> maze = Maze('labyrinth.txt')
        >>> maze.analyse()
        The maze has 2 gates.
        The maze has 2 sets of walls that are all connected.
        >>> maze = Maze('bianjie.txt')
        >>> maze.analyse()
        The maze has 2 gates.
        The maze has walls that are all connected.
        """

        directions_of_point = {
            0: '',
            1: 'E',
            2: 'S',
            3: 'SE'
        }
        directions_of_inner_point = {
            0: 'NW',
            1: 'W',
            2: 'N',
            3: ''
        }
        self.grid_point_no_object = self.__int_grid(directions_of_point)
        self.grid_inner_point_no_object = self.__int_grid(directions_of_inner_point)

        # ------------GATE------------
        # 可以删掉
        gate_set = set()
        # end 可以删掉
        num_gate = 0
        for i in [(0, 'W'), (self.x_dim - 2, 'E')]:
            for j in range(self.y_dim - 1):
                if i[1] in self.grid_inner_point_no_object[i[0]][j]:
                    num_gate += 1
                    # 可以删掉
                    gate_set.add(((i[0], j), i[1]))
                    # end 可以删掉
        for i in range(self.x_dim - 1):
            for j in [(0, 'N'), (self.y_dim - 2, 'S')]:
                if j[1] in self.grid_inner_point_no_object[i][j[0]]:
                    num_gate += 1
                    # 可以删掉
                    gate_set.add(((i, j[0]), j[1]))
                    # end 可以删掉
        # 字典映射
        gate_output_dict = {
            0: 'no gate.',
            1: 'a single gate.'
        }
        print(f'The maze has {gate_output_dict.get(num_gate, f"{num_gate} gates.")}')
        # ------------END GATE------------

        # ------------WALL------------
        # 遍历节点
        num_set_of_wall = 0
        visited_point_for_wall = set()
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                if (x, y) not in visited_point_for_wall:
                    vp = self.__traversal_by_bfs(x, y, self.grid_point_no_object)
                    if len(vp) != 1:
                        num_set_of_wall += 1
                    visited_point_for_wall |= vp
        # 字典映射
        gate_output_dict = {
            0: 'no wall.',
            1: 'walls that are all connected.'
        }
        print(f'The maze has '
              f'{gate_output_dict.get(num_set_of_wall,f"{num_set_of_wall} sets of walls that are all connected.")}')
        # ------------END WALL------------

    def display(self):
        pass
