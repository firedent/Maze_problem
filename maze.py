# Insert your code here
import collections


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

    def __int_grid_inner_point(self):
        """
        >>> m = Maze('maze_1.txt')
        >>> m._Maze__int_grid_inner_point()
        >>> m.grid_inner_point[1][0]
        InnerPoint(1, 0, 0)
        >>> m.grid_inner_point[7][0]
        InnerPoint(7, 0, 0)
        >>> m.grid_inner_point[0][5]
        InnerPoint(0, 5, 1)
        >>> m.grid_inner_point[7][5]
        InnerPoint(7, 5, 0)
        >>> m.grid_inner_point[6][4].direction
        'S'
        >>> m.grid_inner_point[5][1].direction
        'NW'
        >>> m.grid_inner_point[4][4].direction
        'W'
        >>> m.grid_inner_point[0][0].direction
        'WE'
        >>> m.grid_inner_point[1][0].direction
        'NWS'
        >>> m.grid_inner_point_no_object[6][4]
        'S'
        >>> m.grid_inner_point_no_object[5][1]
        'NW'
        >>> m.grid_inner_point_no_object[4][4]
        'W'
        >>> m.grid_inner_point_no_object[0][0]
        'WE'
        >>> m.grid_inner_point_no_object[1][0]
        'NWS'
        >>> m = Maze('bianjie.txt')
        >>> m._Maze__int_grid_inner_point()
        >>> m.grid_inner_point_no_object[0][0]
        'NW'
        """
        # for 面向对象

        # 初始化
        grid_inner_point = []
        for x in range(self.x_dim):
            line_inner_point = []
            for y in range(self.y_dim):
                line_inner_point.append(InnerPoint(x, y, self.grid_maze_raw[y][x]))
            grid_inner_point.append(line_inner_point)

        operations = {
            'N': lambda p: (p[0], p[1] - 1, 'S'),
            'W': lambda p: (p[0] - 1, p[1], 'E'),
        }

        for x in range(self.x_dim):
            for y in range(self.y_dim):
                for d in grid_inner_point[x][y].direction:
                    pre = operations[d]((x, y))
                    if 0 <= pre[0] <= self.x_dim-1 and 0 <= pre[1] <= self.y_dim-1:
                        grid_inner_point[pre[0]][pre[1]].direction += pre[2]
        self.grid_inner_point = grid_inner_point
        # end for 面向对象

        # for 不是面向对象
        # 初始化
        grid_inner_point_no_object = [[''] * self.y_dim for _ in range(self.x_dim)]
        directions = {
            0: 'NW',
            1: 'W',
            2: 'N',
            3: '',
        }
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                # grid_inner_point_no_object[x][y] = directions[self.get_inner_point(x, y)]
                # 遍历本节点可以指向的方向
                for d in directions[self.get_inner_point(x, y)]:
                    # 一次添加本节点可以指向的方向
                    grid_inner_point_no_object[x][y] += d
                    # pre用来接收返回的 指向的方向的下一个节点的坐标和下一个节点的指向方向
                    pre = operations[d]((x, y))
                    if 0 <= pre[0] <= self.x_dim-1 and 0 <= pre[1] <= self.y_dim-1:
                        # 将下一个节点的指向方向添加进去
                        grid_inner_point_no_object[pre[0]][pre[1]] += pre[2]
        self.grid_inner_point_no_object = grid_inner_point_no_object
        # end 不是面向对象

    def get_inner_point(self, x, y):
        """
        >>> m = Maze('maze_1.txt')
        >>> m.get_inner_point(1, 0)
        0
        >>> m.get_inner_point(7, 0)
        0
        >>> m.get_inner_point(0, 5)
        1
        >>> m.get_inner_point(7, 5)
        0
        >>> m = Maze('bianjie.txt')
        >>> m.get_inner_point(0, 0)
        0
        >>> m.get_inner_point(0, 1)
        1
        >>> m.get_inner_point(1, 0)
        2
        >>> m.get_inner_point(1, 1)
        0
        """
        return self.grid_maze_raw[y][x]

    def __int_grid_point(self):

        grid_point_no_object = [[''] * self.y_dim for _ in range(self.x_dim)]
        directions = {
            0: '',
            1: 'E',
            2: 'S',
            3: 'SE',
        }
        operations = {
            'S': lambda p: (p[0], p[1] + 1, 'N'),
            'E': lambda p: (p[0] + 1, p[1], 'W'),
        }
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                for d in directions[self.get_inner_point(x, y)]:
                    grid_point_no_object[x][y] += d
                    pre = operations[d]((x, y))
                    if 0 <= pre[0] <= self.x_dim-1 and 0 <= pre[1] <= self.y_dim-1:
                        grid_point_no_object[pre[0]][pre[1]] += pre[2]
        self.grid_point_no_object = grid_point_no_object

    def analyse(self):
        """
        >>> maze = Maze('maze_1.txt')
        >>> maze.analyse()
        The maze has 12 gates.
        >>> maze = Maze('maze_2.txt')
        >>> maze.analyse()
        The maze has 20 gates.
        >>> maze = Maze('labyrinth.txt')
        >>> maze.analyse()
        The maze has 2 gates.
        >>> maze = Maze('bianjie.txt')
        >>> maze.analyse()
        The maze has 2 gates.
        """
        self.__int_grid_inner_point()
        # self.__int_grid_point()

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

    def display(self):
        pass
