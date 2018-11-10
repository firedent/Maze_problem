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
        length = 0
        grid_maze_raw = []
        for line in lines:
            line = line.replace(' ', '')
            if len(line) is not 0:
                if length is 0:
                    length = len(line)
                elif len(line) != length:
                    raise MazeError('Incorrect input.')
                if length > 31 or length < 2:
                    raise MazeError('Incorrect input.')
                ele = []
                for i in line:
                    if i in {'0', '1', '2', '3'}:
                        ele.append(int(i))
                    else:
                        # print('数字不存在{0,1,2,3}')
                        raise MazeError('Incorrect input.')
                if ele[-1] == 1 or ele[-1] == 3:
                    raise MazeError('Input does not represent a maze.')
                grid_maze_raw.append(ele)
            if len(grid_maze_raw) > 41:
                raise MazeError('Incorrect input.')

        if len(grid_maze_raw) < 2:
            raise MazeError('Incorrect input.')
        if 2 in grid_maze_raw[-1] or 3 in grid_maze_raw[-1]:
            raise MazeError('Input does not represent a maze.')

        self.grid_maze_raw = grid_maze_raw
        self.x_dim = length
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
        gate_set = set()
        for i in [(0, 'W'), (self.x_dim - 2, 'E')]:
            for j in range(self.y_dim - 1):
                if i[1] in self.grid_inner_point[i[0]][j]:
                    gate_set.add(
                        ((i[0], j), self.NEIGHBOUR[i[1]]((i[0], j)))
                    )

        for i in range(self.x_dim - 1):
            for j in [(0, 'N'), (self.y_dim - 2, 'S')]:
                if j[1] in self.grid_inner_point[i][j[0]]:
                    gate_set.add(
                        ((i, j[0]), self.NEIGHBOUR[j[1]]((i, j[0])))
                    )

        self.num_gate = len(gate_set)
        pillar_set = set()
        num_set_of_wall = 0
        visited_point_for_wall = set()
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                if (x, y) not in visited_point_for_wall:
                    vp = self.__traversal_by_bfs(x, y, self.grid_point)
                    if len(vp) == 1:
                        pillar_set |= vp
                    else:
                        num_set_of_wall += 1
                        visited_point_for_wall |= vp

        self.pillar_set = pillar_set
        self.num_set_of_wall = num_set_of_wall
        num_accessible_area = 0
        visited_inner_point_for_area = set()
        for g in gate_set:
            if g[0] not in visited_inner_point_for_area:
                vip = self.__traversal_by_bfs(g[0][0], g[0][1], self.grid_inner_point, x_r=1, y_b=1)
                visited_inner_point_for_area |= vip
                num_accessible_area += 1

        self.num_accessible_area = num_accessible_area
        self.num_inaccessible_inner_point = (self.y_dim - 1) * (self.x_dim - 1) - len(visited_inner_point_for_area)

        grid_inner_point_copied = copy.deepcopy(self.grid_inner_point)
        cul_de_sacs_set = set()
        initial_cul_de_sacs_set = set()
        q = Queue()
        for p in visited_inner_point_for_area:
            if len(self.grid_inner_point[p[0]][p[1]]) == 1:
                q.enqueue(p)
                initial_cul_de_sacs_set.add(p)

        while not q.is_empty():
            current_point = q.dequeue()
            cul_de_sacs_set.add(current_point)
            next_point = self.__get_children(current_point[0], current_point[1], grid_inner_point_copied)[0]
            if 0 <= next_point[0] <= self.x_dim - 2 and 0 <= next_point[1] <= self.y_dim - 2:
                grid_inner_point_copied[next_point[0]][next_point[1]] = \
                    grid_inner_point_copied[next_point[0]][next_point[1]].replace(
                        self.OPPOSITION[grid_inner_point_copied[current_point[0]][current_point[1]]],
                        ''
                    )
                if len(grid_inner_point_copied[next_point[0]][next_point[1]]) == 1:
                    q.enqueue(next_point)
            grid_inner_point_copied[current_point[0]][current_point[1]] = ''

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
        self.grid_inner_point_trimmed = grid_inner_point_copied
        self.cul_de_sacs_set = cul_de_sacs_set
        visited_inner_point_for_path = set()
        entry_exit_path_list = []

        entry_exit_path_set = set()
        for g in gate_set:
            if g[0] not in cul_de_sacs_set and g[0] not in visited_inner_point_for_path:
                visited_point_list = list()
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
                    entry_exit_path_list.append(visited_point_list)

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
        self.entry_exit_path_set = entry_exit_path_set

    def __int_grid(self, directions):
        grid = [[''] * self.y_dim for _ in range(self.x_dim)]
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                for d in directions[self.get_inner_point(x, y)]:
                    grid[x][y] += d
                    n = self.NEIGHBOUR[d]
                    pre = (n((x, y))[0], n((x, y))[1], self.OPPOSITION[d])
                    if 0 <= pre[0] <= self.x_dim - 1 and 0 <= pre[1] <= self.y_dim - 1:
                        grid[pre[0]][pre[1]] += pre[2]

        return grid

    def __get_children(self, x, y, grid):
        children = list()
        direction = grid[x][y]
        for d in direction:
            children.append(self.NEIGHBOUR[d]((x, y)))
        return children

    def __traversal_by_bfs(self, x, y, grid, x_l=0, x_r=0, y_t=0, y_b=0, *, key=None):
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

        return visited_point

    def get_inner_point(self, x, y):
        return self.grid_maze_raw[y][x]

    def analyse(self):
        gate_output_dict = {
            0: 'no gate.',
            1: 'a single gate.'
        }
        print(f'The maze has {gate_output_dict.get(self.num_gate, f"{self.num_gate} gates.")}')

        wall_output_dict = {
            0: 'no wall.',
            1: 'walls that are all connected.'
        }
        print(f'The maze has '
              f'{wall_output_dict.get(self.num_set_of_wall,f"{self.num_set_of_wall} sets of walls that are all connected.")}')

        inaccessible_point_output_dict = {
            0: 'no inaccessible inner point.',
            1: 'a unique inaccessible inner point.'
        }
        t_str_for_area_output = f"{self.num_inaccessible_inner_point} inaccessible inner points."
        print(f'The maze has '
              f'{inaccessible_point_output_dict.get(self.num_inaccessible_inner_point, t_str_for_area_output)}')

        accessible_area_output_dict = {
            0: 'no accessible area.',
            1: 'a unique accessible area.'
        }
        print(f'The maze has '
              f'{accessible_area_output_dict.get(self.num_accessible_area, f"{self.num_accessible_area} accessible areas.")}')

        cul_de_sacs_output_dict = {
            0: 'no accessible cul-de-sac.',
            1: 'accessible cul-de-sacs that are all connected.'
        }
        t_str_for_cul_output = f'{self.num_cul_de_sacs_set} sets of accessible cul-de-sacs that are all connected.'
        print(f'The maze has {cul_de_sacs_output_dict.get(self.num_cul_de_sacs_set, t_str_for_cul_output)}')

        entry_exit_path_output_dict = {
            0: 'no entry-exit path with no intersection not to cul-de-sacs.',
            1: 'a unique entry-exit path with no intersection not to cul-de-sacs.'
        }
        t_str_for_path_output = f'{self.num_entry_exit_path} entry-exit paths with no intersections not to cul-de-sacs.'
        print(f'The maze has {entry_exit_path_output_dict.get(self.num_entry_exit_path, t_str_for_path_output)}')

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

        tex_content_pillars = list()
        tex_content_pillars.append('% Pillars\n')
        for pillar in sorted(self.pillar_set, key=lambda p: (p[1], p[0])):
            tex_content_pillars.append(f'    \\fill[green] ({pillar[0]},{pillar[1]}) circle(0.2);\n')

        tex_content_cul_de_sacs = list()
        tex_content_cul_de_sacs.append('% Inner points in accessible cul-de-sacs\n')
        for i in sorted(self.cul_de_sacs_set, key=lambda s: (s[1], s[0])):
            tex_content_cul_de_sacs.append(f'    \\node at ({i[0]+0.5},{i[1]+0.5}) ''{};\n')

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

        with open(self.file_path.parent / (self.file_path.stem + '.tex'), mode='w') as f:
            f.write(tex_content_head)
            f.writelines(tex_content_walls)
            f.writelines(tex_content_pillars)
            f.writelines(tex_content_cul_de_sacs)
            f.writelines(tex_content_entry_exit_path)
            f.write(tex_content_tail)
