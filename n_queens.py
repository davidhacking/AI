queen = 1
empty = 0


def init_n_queens_map(n):
    res = []
    for i in range(n):
        res.append([])
        for j in range(n):
            res[i].append(empty)
    return res


def parse_n_queens_map(m):
    res = []
    n = len(m)
    for i in range(n):
        res.append("")
        for j in range(n):
            res[i] += "." if m[i][j] == 0 else "Q"
    return res


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def check_point(self, point):
        # 列check
        if point.y == self.y:
            return False
        delta_x = self.x - point.x
        delta_y = self.y - point.y
        # 左斜向右check
        # 右斜向左check
        k = delta_x / delta_y
        if k == 1 or k == -1:
            return False
        return True


class Result:
    def __init__(self, state, result):
        self.state = state
        self.result = result


class BaseNode:
    def __init__(self, paces=None):
        if paces is None:
            paces = []
        self._paces = paces
        self._last_pace = None
        if self._paces is not None and len(self._paces) > 0:
            self._last_pace = paces[-1]

    def last_pace(self):
        return self._last_pace

    def paces(self):
        return self._paces

    def play(self, pace):
        self._last_pace = pace
        self._paces.append(pace)

    def rollback(self):
        last_pace = self._last_pace
        self._paces.pop()
        self._last_pace = None
        if len(self._paces) > 0:
            self._last_pace = self._paces[-1]
        return last_pace

    def key(self):
        return "|".join([str(p) for p in self._paces])

    def end(self):
        pass

    def next_all_nodes(self, maximizing_player=True):
        pass

    def base_copy(self, child):
        child._paces = []
        for p in self._paces:
            child._paces.append(p)
        child._last_pace = self._last_pace

    def clear_paces(self):
        self._paces = []
        self._last_pace = None

    # 评估玩家的收益
    def evaluate(self):
        pass


class NQueensNode(BaseNode):
    def __init__(self, queen_map, queen_num=0, used_points=None, paces=None):
        super(NQueensNode, self).__init__(paces)
        self._queen_map = queen_map
        self.n = len(queen_map)
        self._queen_num = queen_num
        self._used_points = used_points
        if self._used_points is None:
            self._used_points = []

    def copy_points(self):
        res = []
        for p in self._used_points:
            res.append(p)
        return res

    def copy_queen_map(self):
        return parse_n_queens_map(self._queen_map)

    def end(self):
        return self._queen_num == self.n

    def evaluate(self):
        if self.end():
            return Result(res_state_succ, self.copy_queen_map())
        return Result(res_state_not_match, None)

    def next_all_nodes(self, maximizing_player=True):
        if self.end():
            return
        x = self._queen_num
        for y, item in enumerate(self._queen_map[x]):
            if item != empty:
                continue
            point = Point(x, y)
            flag = True
            for p in self._used_points:
                if not p.check_point(point):
                    flag = False
                    break
            if flag:
                self._queen_map[x][y] = queen
                used_points = self.copy_points()
                used_points.append(point)
                node = NQueensNode(self._queen_map, x + 1, used_points, self._paces)
                yield node
                self._queen_map[x][y] = empty


res_state_succ = 1
res_state_not_match = 2


class DFS:
    def __init__(self, node):
        self.node = node

    # 搜索所有满足成功状态的路径 todo 结果重复结果问题
    def search(self):
        result = []
        return self._search(self.node, result)

    def _search(self, node, result):
        if node.end():
            value = node.evaluate()
            if value.state == res_state_succ:
                result.append(value.result)
            return result
        children = node.next_all_nodes()
        for c in children:
            result = self._search(c, result)
        return result


class Solution(object):
    def solveNQueens(self, n):
        """
        :type n: int
        :rtype: List[List[str]]
        """
        m = init_n_queens_map(n)
        node = NQueensNode(m)
        d = DFS(node)
        res = d.search()
        return res


def test_parse_n_queens_map():
    m1 = init_n_queens_map(2)
    m1[0][0] = 1
    m1[0][0] = 1
    m1[0][0] = 1
    print(parse_n_queens_map(m1))


def test1():
    s = Solution()
    res = s.solveNQueens(1)
    pass


def test2():
    s = Solution()
    res = s.solveNQueens(4)
    pass


if __name__ == '__main__':
    test2()
