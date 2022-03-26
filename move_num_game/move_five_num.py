next_node_map = {
    0: [(0, 1), (1, 0)],
    1: [(0, 0), (0, 2), (1, 1)],
    2: [(0, 1), (1, 2)],
    3: [(0, 0), (1, 1)],
    4: [(0, 1), (1, 0), (1, 2)],
    5: [(0, 2), (1, 1)],
}

end_states = [
    [1, 2, 3],
    [4, 5, 0],
]


def zero_index(nums):
    for i in range(0, 2):
        for j in range(0, 3):
            if nums[i][j] == 0:
                return i * 3 + j, i, j


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


class MoveFiveNumGame(BaseNode):
    def __init__(self, nums, index=(0, 0), x=0, y=0, paces=None):
        super(MoveFiveNumGame, self).__init__(paces)
        self.nums = nums
        self.index = index
        self.x = x
        self.y = y

    def key(self):
        num = self.nums[0][0] * 1e5 + self.nums[0][1] * 1e4 + self.nums[0][2] * 1e3 + self.nums[1][0] * 1e2 + \
              self.nums[1][1] * 1e1 + self.nums[1][2]
        return num

    def copy_nums(self):
        res = [
            [self.nums[0][0], self.nums[0][1], self.nums[0][2]],
            [self.nums[1][0], self.nums[1][1], self.nums[1][2]],
        ]
        return res

    def end(self):
        return self.nums[0][0] == end_states[0][0] and \
               self.nums[0][1] == end_states[0][1] and \
               self.nums[0][2] == end_states[0][2] and \
               self.nums[1][0] == end_states[1][0] and \
               self.nums[1][1] == end_states[1][1] and \
               self.nums[1][2] == end_states[1][2]

    def next_all_nodes(self, maximizing_player=True):
        next_nodes = []
        for k in next_node_map[self.index]:
            new_nums = self.copy_nums()
            new_nums[k[0]][k[1]], new_nums[self.x][self.y] = new_nums[self.x][self.y], new_nums[k[0]][k[1]]
            node = MoveFiveNumGame(new_nums, k[0] * 3 + k[1], k[0], k[1])
            self.base_copy(node)
            node.play((k, node.key()))
            next_nodes.append(node)
        return next_nodes


class QueueNode:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next_node = next_node


class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def put(self, value):
        node = QueueNode(value)
        if self.tail is None:
            self.head = node
            self.tail = node
        self.tail.next_node = node
        self.tail = node
        self.length += 1

    def pop(self):
        if self.head is None:
            return None
        node = self.head
        self.head = self.head.next_node
        if self.length > 0:
            self.length -= 1
        if self.length == 0:
            self.tail = None
        return node.value

    def first(self):
        if self.head is not None:
            return self.head.value

    def __len__(self):
        return self.length


"""
class Solution:
    NEIGHBORS = [[1, 3], [0, 2, 4], [1, 5], [0, 4], [1, 3, 5], [2, 4]]

    def slidingPuzzle(self, board: List[List[int]]) -> int:
        # 枚举 status 通过一次交换操作得到的状态
        def get(status: str) -> Generator[str, None, None]:
            s = list(status)
            x = s.index("0")
            for y in Solution.NEIGHBORS[x]:
                s[x], s[y] = s[y], s[x]
                yield "".join(s)
                s[x], s[y] = s[y], s[x]

        initial = "".join(str(num) for num in sum(board, []))
        if initial == "123450":
            return 0

        q = deque([(initial, 0)])
        seen = {initial}
        while q:
            status, step = q.popleft()
            for next_status in get(status):
                if next_status not in seen:
                    if next_status == "123450":
                        return step + 1
                    q.append((next_status, step + 1))
                    seen.add(next_status)
        
        return -1
"""


class BFS:
    search_fail_res = 1

    def __init__(self, root):
        self.queue = Queue()
        self.queue.put(root)
        self.cache = {}

    def search(self, depth=20):
        if self.queue.first().end():
            return self.queue.first().paces()
        while True:
            node = self.queue.pop()
            if len(node.paces()) >= depth:
                return None
            children = node.next_all_nodes()
            for c in children:
                key = c.key()
                value = self.cache.get(key)
                if value is None:
                    if c.end():
                        return c.paces()
                    self.queue.put(c)
                    self.cache[key] = self.search_fail_res


class Solution(object):
    def slidingPuzzle(self, board):
        """
        :type board: List[List[int]]
        :rtype: int
        """
        index, x, y = zero_index(board)
        node = MoveFiveNumGame(board, index, x, y)
        b = BFS(node)
        res = b.search()
        if res is None:
            return -1
        return len(res)


def test1():
    s = Solution()
    nums = [[1, 2, 3], [4, 0, 5]]
    assert 1 == s.slidingPuzzle(nums)


def test2():
    s = Solution()
    nums = [[1, 2, 3], [5, 4, 0]]
    assert -1 == s.slidingPuzzle(nums)


def test3():
    s = Solution()
    nums = [[4, 1, 2], [5, 0, 3]]
    assert 5 == s.slidingPuzzle(nums)


def test4():
    s = Solution()
    nums = [[3, 0, 1], [2, 4, 5]]
    depth = s.slidingPuzzle(nums)
    assert 14 == depth


if __name__ == '__main__':
    test2()
    test3()
    test4()
