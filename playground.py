import time


class InnerPoint:
    def __init__(self, x, y, raw):
        self.x = x
        self.y = y
        self.raw = raw
        self.direction = ''
    def __repr__(self):
        return f'InnerPoint({self.x}, {self.y}, {self.raw})'


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.connect = ''


    def __repr__(self):
        return f'Point({self.x}, {self.y}, {self.direction})'

class MazeError(Exception):
    pass


with open('maze_test.txt') as f:
    lines = f.read().splitlines()
# 找长度
length = 0
grid = []
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
        grid.append(ele)
    # 判断当前已经多少行了
    if len(grid) > 41:
        # print(f'行数太多,{len(grid)}')
        raise MazeError('Incorrect input.')
# 判断全部加载完之后，是否到达允许的最小行数
if len(grid) < 2:
    # print(f'行数太少,{len(grid)}')
    raise MazeError('Incorrect input.')
# 最后一行不可能是2或3
if 2 in grid[-1] or 3 in grid[-1]:
    raise MazeError('Input does not represent a maze.')

grid_inner_point = []
grid_point = []


for i in range(len(grid[1])):
    line_inner_point = []
    for j in range(len(grid)):
        line_inner_point.append(InnerPoint(i, j, grid[j][i]))
    grid_inner_point.append(line_inner_point)

