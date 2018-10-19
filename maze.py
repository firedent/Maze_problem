# coding=utf-8
from queue_adt import *
from pathlib import Path
import copy


class MazeError(Exception):
    pass


class Maze:
    NEIGHBOUR = {
        'N': lambda p: (p[0], p[1] - 1),
        'S': lambda p: (p[0], p[1] + 1),
        'W': lambda p: (p[0] - 1, p[1]),
        'E': lambda p: (p[0] + 1, p[1])
    }

    OPPOSITION = {
        'S': 'N',
        'N': 'S',
        'W': 'E',
        'E': 'W'
    }

    def __init__(self, filename):

        self.file_path = Path(filename)
        with open(self.file_path) as f:
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
        # grid原始数据
        self.grid_maze_raw = grid_maze_raw
        # grid的横长
        self.x_dim = length
        # grid的纵长
        self.y_dim = len(grid_maze_raw)

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

        self.grid_point = self.__int_grid(directions_of_point)
        self.grid_inner_point = self.__int_grid(directions_of_inner_point)

        # ------------GATE------------
        # gate 第三四问，求accessible area需要用
        # gate结构：((门X坐标, 门Y坐标), (进门X坐标, 进门Y坐标))
        gate_set = set()
        for i in [(0, 'W'), (self.x_dim - 2, 'E')]:
            for j in range(self.y_dim - 1):
                if i[1] in self.grid_inner_point[i[0]][j]:
                    # 等同于 num_gate = len(gate_set)
                    # num_gate += 1
                    gate_set.add(
                        ((i[0], j), self.NEIGHBOUR[i[1]]((i[0], j)))
                    )
        for i in range(self.x_dim - 1):
            for j in [(0, 'N'), (self.y_dim - 2, 'S')]:
                if j[1] in self.grid_inner_point[i][j[0]]:
                    # 等同于 num_gate = len(gate_set)
                    # num_gate += 1
                    gate_set.add(
                        ((i, j[0]), self.NEIGHBOUR[j[1]]((i, j[0])))
                    )
        self.num_gate = len(gate_set)
        # ------------END GATE------------

        # ------------WALL------------
        # 遍历节点
        num_set_of_wall = 0
        visited_point_for_wall = set()
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                if (x, y) not in visited_point_for_wall:
                    vp = self.__traversal_by_bfs(x, y, self.grid_point)
                    if len(vp) != 1:
                        num_set_of_wall += 1
                    visited_point_for_wall |= vp
        self.num_set_of_wall = num_set_of_wall
        # ------------END WALL------------

        # ------------ACCESSIBLE AREA------------
        # ------------INACCESSIBLE AREA------------
        num_accessible_area = 0
        visited_inner_point_for_area = set()
        for g in gate_set:
            if g[0] not in visited_inner_point_for_area:
                vip = self.__traversal_by_bfs(g[0][0], g[0][1], self.grid_inner_point, x_r=1, y_b=1)
                visited_inner_point_for_area |= vip
                num_accessible_area += 1

        self.num_accessible_area = num_accessible_area
        self.num_inaccessible_inner_point = (self.y_dim - 1) * (self.x_dim - 1) - len(visited_inner_point_for_area)
        # ------------END INACCESSIBLE AREA------------
        # ------------END ACCESSIBLE AREA------------

        # ------------CUL-DE-SACS------------
        # 创建grid_inner_point的替身
        # path要用，这是一个把cul-de-sacs当做wall的grid
        grid_inner_point_copied = copy.deepcopy(self.grid_inner_point)
        # 所有cul_de_sacs
        cul_de_sacs_set = set()
        # 初始出度为1的节点
        initial_cul_de_sacs_set = set()
        # 首先在可到达节点里找出所有出度是1的节点，并放到队列里
        q = Queue()
        for p in visited_inner_point_for_area:
            if len(self.grid_inner_point[p[0]][p[1]]) == 1:
                q.enqueue(p)
                initial_cul_de_sacs_set.add(p)

        while not q.is_empty():
            # 从队列中取出一个来
            current_point = q.dequeue()
            cul_de_sacs_set.add(current_point)
            # 找到此节点相邻节点
            next_point = self.__get_children(current_point[0], current_point[1], grid_inner_point_copied)[0]
            if 0 <= next_point[0] <= self.x_dim - 2 and 0 <= next_point[1] <= self.y_dim - 2:
                # 更改相邻节点的direction
                grid_inner_point_copied[next_point[0]][next_point[1]] = \
                    grid_inner_point_copied[next_point[0]][next_point[1]].replace(
                        self.OPPOSITION[grid_inner_point_copied[current_point[0]][current_point[1]]],
                        ''
                    )
                # 如果当前节点也变成出度为1的节点了，就放到队列里
                if len(grid_inner_point_copied[next_point[0]][next_point[1]]) == 1:
                    q.enqueue(next_point)
            # 更改本节点的direction
            grid_inner_point_copied[current_point[0]][current_point[1]] = ''

        # 开始暴力解法
        num_cul_de_sacs_set = 0
        visited_inner_point_for_cul_de_sacs = set()
        for cul in sorted(initial_cul_de_sacs_set):
            if cul not in visited_inner_point_for_cul_de_sacs:
                visited_inner_point_for_cul_de_sacs |= self.__traversal_by_bfs(
                    cul[0], cul[1], self.grid_inner_point, x_r=1, y_b=1,
                    key=lambda arg: arg in cul_de_sacs_set
                )
                num_cul_de_sacs_set += 1
        self.num_cul_de_sacs_set = num_cul_de_sacs_set

        # 修剪过的grid_inner_point
        self.grid_inner_point_trimmed = grid_inner_point_copied
        # cul_de_sacs的集合，display需要用到
        self.cul_de_sacs_set = cul_de_sacs_set
        # ------------END CUL-DE-SACS------------

        # ------------PATH------------
        visited_inner_point_for_path = set()
        # list可以删掉
        entry_exit_path_list = []
        # list可以删掉
        entry_exit_path_set = set()
        for g in gate_set:
            # 如果这个门 不是cul-de-sacs 也没有被访问过
            if g[0] not in cul_de_sacs_set and g[0] not in visited_inner_point_for_path:
                # 艹，再写一次BFS，qnmd简洁性

                # list可以删掉
                visited_point_list = list()
                # list可以删掉

                visited_point_set = set()
                bfs_q = Queue()
                bfs_q.enqueue(g[0])
                dirty = False
                while not bfs_q.is_empty():
                    bfs_p = bfs_q.dequeue()
                    if len(grid_inner_point_copied[bfs_p[0]][bfs_p[1]]) != 2:
                        dirty = True
                    else:
                        visited_point_list.append(bfs_p)
                    visited_point_set.add(bfs_p)
                    for c in self.__get_children(bfs_p[0], bfs_p[1], grid_inner_point_copied):
                        if c not in visited_point_set:
                            if 0 <= c[0] <= self.x_dim - 2 \
                                    and 0 <= c[1] <= self.y_dim - 2:
                                bfs_q.enqueue(c)
                if not dirty:
                    # list可以删掉
                    entry_exit_path_list.append(visited_point_list)
                    # list可以删掉

                    # 不够优雅 不够优雅
                    # 找到线路的第一和最后一个，直接做并集
                    visited_point_set |= \
                        set(
                            self.__get_children(
                                visited_point_list[0][0],
                                visited_point_list[0][1],
                                grid_inner_point_copied)

                        )
                    visited_point_set |= \
                        set(
                            self.__get_children(
                                visited_point_list[-1][0],
                                visited_point_list[-1][1],
                                grid_inner_point_copied
                            )
                        )

                    entry_exit_path_set |= visited_point_set
                visited_inner_point_for_path |= visited_point_set
        self.num_entry_exit_path = len(entry_exit_path_list)

        # anaglse要用
        self.entry_exit_path_set = entry_exit_path_set
        # ------------END PATH------------

    def __int_grid(self, directions):
        grid = [[''] * self.y_dim for _ in range(self.x_dim)]
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                # grid_inner_point_no_object[x][y] = directions[self.get_inner_point(x, y)]
                # 遍历本节点可以指向的方向
                for d in directions[self.get_inner_point(x, y)]:
                    # 一次添加本节点可以指向的方向
                    grid[x][y] += d
                    # pre用来接收返回的 指向的方向的下一个节点的坐标和下一个节点的指向方向
                    n = self.NEIGHBOUR[d]
                    pre = (n((x, y))[0], n((x, y))[1], self.OPPOSITION[d])
                    if 0 <= pre[0] <= self.x_dim - 1 and 0 <= pre[1] <= self.y_dim - 1:
                        # 将下一个节点的指向方向添加进去
                        grid[pre[0]][pre[1]] += pre[2]
        return grid

    def __get_children(self, x, y, grid):
        children = list()
        direction = grid[x][y]
        for d in direction:
            children.append(self.NEIGHBOUR[d]((x, y)))
        return children

    def __traversal_by_bfs(self, x, y, grid, x_l=0, x_r=0, y_t=0, y_b=0, *, key=None):
        # x_l=0, x_r=0, y_t=0, y_b=0修剪grid，分变为：左、右、上、下。
        visited_point = set()
        q = Queue()
        q.enqueue((x, y))
        while not q.is_empty():
            p = q.dequeue()
            visited_point.add(p)
            for c in self.__get_children(p[0], p[1], grid):
                if 0 + x_l <= c[0] <= self.x_dim - 1 - x_r \
                        and 0 + y_t <= c[1] <= self.y_dim - 1 - y_b:
                    if c not in visited_point:
                        if key is None:
                            q.enqueue(c)
                        elif key(c):
                            q.enqueue(c)
        # 返回的set包含起始节点本身
        return visited_point

    def get_inner_point(self, x, y):
        return self.grid_maze_raw[y][x]

    def analyse(self):
        # ------------GATE------------
        gate_output_dict = {
            0: 'no gate.',
            1: 'a single gate.'
        }
        print(f'The maze has {gate_output_dict.get(self.num_gate, f"{self.num_gate} gates.")}')

        # ------------WALL------------
        wall_output_dict = {
            0: 'no wall.',
            1: 'walls that are all connected.'
        }
        print(f'The maze has '
              f'{wall_output_dict.get(self.num_set_of_wall,f"{self.num_set_of_wall} sets of walls that are all connected.")}')

        # ------------INACCESSIBLE AREA------------
        inaccessible_point_output_dict = {
            0: 'no inaccessible inner point.',
            1: 'a unique inaccessible inner point.'
        }
        t_str_for_area_output = f"{self.num_inaccessible_inner_point} inaccessible inner points."
        print(f'The maze has '
              f'{inaccessible_point_output_dict.get(self.num_inaccessible_inner_point, t_str_for_area_output)}')
        # ------------END INACCESSIBLE AREA------------

        # ------------ACCESSIBLE AREA------------
        accessible_area_output_dict = {
            0: 'no accessible area.',
            1: 'a unique accessible area.'
        }
        print(f'The maze has '
              f'{accessible_area_output_dict.get(self.num_accessible_area, f"{self.num_accessible_area} accessible areas.")}')
        # ------------END ACCESSIBLE AREA------------

        # ------------CUL-DE-SACS------------
        cul_de_sacs_output_dict = {
            0: 'no accessible cul-de-sac.',
            1: 'accessible cul-de-sacs that are all connected.'
        }
        t_str_for_cul_output = f'{self.num_cul_de_sacs_set} sets of accessible cul-de-sacs that are all connected.'
        print(f'The maze has {cul_de_sacs_output_dict.get(self.num_cul_de_sacs_set, t_str_for_cul_output)}')
        # ------------END CUL-DE-SACS------------

        # ------------PATH------------
        entry_exit_path_output_dict = {
            0: 'no entry-exit path with no intersection not to cul-de-sacs.',
            1: 'a unique entry-exit path with no intersection not to cul-de-sacs.'
        }
        t_str_for_path_output = f'{self.num_entry_exit_path} entry-exit paths with no intersections not to cul-de-sacs.'
        print(f'The maze has {entry_exit_path_output_dict.get(self.num_entry_exit_path, t_str_for_path_output)}')
        # ------------END PATH------------

    def display(self):
        tex_content_head = '\\documentclass[10pt]{article}\n' \
                           '\\usepackage{tikz}\n' \
                           '\\usetikzlibrary{shapes.misc}\n' \
                           '\\usepackage[margin=0cm]{geometry}\n' \
                           '\\pagestyle{empty}\n' \
                           '\\tikzstyle{every node}=[cross out, draw, red]\n' \
                           '\n' \
                           '\\begin{document}\n' \
                           '\n' \
                           '\\vspace*{\\fill}\n' \
                           '\\begin{center}\n' \
                           '\\begin{tikzpicture}[x=0.5cm, y=-0.5cm, ultra thick, blue]\n'

        tex_content_tail = '\\end{tikzpicture}\n' \
                           '\\end{center}\n' \
                           '\\vspace*{\\fill}\n' \
                           '\n' \
                           '\\end{document}\n'

        # ----------WALL----------
        tex_content_walls = list()
        tex_content_walls.append('% Walls\n')
        for y in range(self.y_dim):
            x = 0
            while x <= self.x_dim - 1:
                if 'E' not in self.grid_point[x][y]:
                    x += 1
                    continue
                tmp = list()
                tmp.append((x, y))
                for t in range(x + 1, self.x_dim):
                    if 'E' not in self.grid_point[t][y]:
                        tmp.append((t, y))
                        x = t + 1
                        break
                tex_content_walls.append(f'    \\draw ({tmp[0][0]},{tmp[0][1]}) -- ({tmp[1][0]},{tmp[1][1]});\n')
        for x in range(self.x_dim):
            y = 0
            while y <= self.y_dim - 1:
                if 'S' not in self.grid_point[x][y]:
                    y += 1
                    continue
                tmp = list()
                tmp.append((x, y))
                for t in range(y + 1, self.y_dim):
                    if 'S' not in self.grid_point[x][t]:
                        tmp.append((x, t))
                        y = t + 1
                        break
                tex_content_walls.append(f'    \\draw ({tmp[0][0]},{tmp[0][1]}) -- ({tmp[1][0]},{tmp[1][1]});\n')
        # ----------END WALL----------

        # ----------PILLAR----------
        tex_content_pillars = list()
        tex_content_pillars.append('% Pillars\n')
        for y in range(self.y_dim):
            for x in range(self.x_dim):
                if self.grid_point[x][y] == '':
                    tex_content_pillars.append(f'    \\fill[green] ({x},{y}) circle(0.2);\n')
        # ----------END PILLAR----------

        # ----------CUL-DE-SACS----------
        tex_content_cul_de_sacs = list()
        tex_content_cul_de_sacs.append('% Inner points in accessible cul-de-sacs\n')
        for i in sorted(self.cul_de_sacs_set, key=lambda s: (s[1], s[0])):
            tex_content_cul_de_sacs.append(f'    \\node at ({i[0]+0.5},{i[1]+0.5}) ''{};\n')
        # ----------END CUL-DE-SACS----------

        # ----------ENTRY-EXIT PATH----------
        tex_content_entry_exit_path = list()
        tex_content_cul_de_sacs.append(f'% Entry-exit paths without intersections\n')
        for y in range(self.y_dim - 1):
            tmp_path_list = []
            x = self.x_dim - 1
            while x >= 0:
                if (x, y) not in self.entry_exit_path_set or 'W' not in self.grid_inner_point_trimmed[x][y]:
                    x -= 1
                    continue
                tmp = list()
                tmp.append((x, y))
                t = x - 1
                while t >= 0:
                    if 'W' not in self.grid_inner_point_trimmed[t][y]:
                        break
                    t -= 1
                tmp.append((t, y))
                x = t - 1
                tmp_path_list.append(
                    '    \\draw[dashed, yellow] '
                    f'({tmp[1][0]+0.5},{tmp[1][1]+0.5}) -- ({tmp[0][0]+0.5},{tmp[0][1]+0.5});\n')
            tex_content_entry_exit_path.extend(tmp_path_list[::-1])

        for x in range(self.x_dim - 1):
            tmp_path_list = []
            y = self.y_dim - 1
            while y >= 0:
                if (x, y) not in self.entry_exit_path_set or 'N' not in self.grid_inner_point_trimmed[x][y]:
                    y -= 1
                    continue
                tmp = list()
                tmp.append((x, y))
                t = y - 1
                while t >= 0:
                    if 'N' not in self.grid_inner_point_trimmed[x][t]:
                        break
                    t -= 1
                tmp.append((x, t))
                y = t - 1
                tmp_path_list.append(
                    '    \\draw[dashed, yellow] '
                    f'({tmp[1][0]+0.5},{tmp[1][1]+0.5}) -- ({tmp[0][0]+0.5},{tmp[0][1]+0.5});\n')
            tex_content_entry_exit_path.extend(tmp_path_list[::-1])
        # ----------END ENTRY-EXIT PATH----------

        # 写入result文件
        # with open(self.file_path.stem + '.tex', mode='w') as f:
        with open(self.file_path.parent / (self.file_path.stem + '.tex'), mode='w') as f:
            # with open('test_output.tex', mode='w') as f:
            f.write(tex_content_head)
            f.writelines(tex_content_walls)
            f.writelines(tex_content_pillars)
            f.writelines(tex_content_cul_de_sacs)
            f.writelines(tex_content_entry_exit_path)
            f.write(tex_content_tail)
