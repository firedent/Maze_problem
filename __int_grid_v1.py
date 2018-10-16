# coding=utf-8
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
        # grid_inner_point = []
        # for x in range(self.x_dim):
        #     line_inner_point = []
        #     for y in range(self.y_dim):
        #         line_inner_point.append(InnerPoint(x, y, self.grid_maze_raw[y][x]))
        #     grid_inner_point.append(line_inner_point)
        #
        # operations = {
        #     'N': lambda p: (p[0], p[1] - 1, 'S'),
        #     'W': lambda p: (p[0] - 1, p[1], 'E'),
        # }
        #
        # for x in range(self.x_dim):
        #     for y in range(self.y_dim):
        #         for d in grid_inner_point[x][y].direction:
        #             pre = operations[d]((x, y))
        #             if 0 <= pre[0] <= self.x_dim-1 and 0 <= pre[1] <= self.y_dim-1:
        #                 grid_inner_point[pre[0]][pre[1]].direction += pre[2]
        # self.grid_inner_point = grid_inner_point
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
        operations = {
            'N': lambda p: (p[0], p[1] - 1, 'S'),
            'W': lambda p: (p[0] - 1, p[1], 'E'),
        }
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                for d in directions[self.get_inner_point(x, y)]:
                    grid_inner_point_no_object[x][y] += d
                    pre = operations[d]((x, y))
                    if 0 <= pre[0] <= self.x_dim-1 and 0 <= pre[1] <= self.y_dim-1:
                        grid_inner_point_no_object[pre[0]][pre[1]] += pre[2]
        self.grid_inner_point_no_object = grid_inner_point_no_object
        # end 不是面向对象

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
            'N': lambda p: (p[0], p[1] - 1, 'S'),
            'W': lambda p: (p[0] - 1, p[1], 'E'),
        }
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                for d in directions[self.get_inner_point(x, y)]:
                    grid_point_no_object[x][y] += d
                    pre = operations[d]((x, y))
                    if 0 <= pre[0] <= self.x_dim-1 and 0 <= pre[1] <= self.y_dim-1:
                        grid_point_no_object[pre[0]][pre[1]] += pre[2]
        self.grid_point_no_object = grid_point_no_object