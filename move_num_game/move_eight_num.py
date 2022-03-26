# 八数码 滑动谜题
from ai import ai, bfs
import math
import random

next_node_map = {
    0: [1, 3],
    1: [0, 2],
    2: [1, 5],
    3: [0, 4],
    4: [1, 3, 5, 7],
    5: [2, 4, 8],
    6: [3, 7],
    7: [4, 6, 8],
    8: [5, 7]
}


def gen_end_state_nums(length):
    res = set()
    for k in range(0, length):
        l = []
        for i in range(1, length + 1):
            if k == i - 1:
                l.append("0")
            l.append(str(i))
        res.add("".join(l))
    l = []
    for i in range(1, length + 1):
        l.append(str(i))
    l.append("0")
    res.add("".join(l))
    return res


eight_num_problem_end_state = gen_end_state_nums(8)


class MoveNumGame(ai.BaseNode):
    def __init__(self, nums, end_states, paces=None):
        super().__init__(paces)
        length = int(math.sqrt(len(nums)))
        assert length * length == len(nums)
        self.nums = nums
        self.zero_index = 0
        for i, n in enumerate(nums):
            if n == "0":
                self.zero_index = i
                break
        self.end_states = end_states

    def copy_nums(self):
        res = []
        for n in self.nums:
            res.append(n)
        return res

    def end(self):
        return self.nums in self.end_states

    def next_all_nodes(self, maximizing_player=True):
        next_nodes = []
        for k in next_node_map[self.zero_index]:
            new_nums = self.copy_nums()
            new_nums[k], new_nums[self.zero_index] = new_nums[self.zero_index], new_nums[k]
            super().play(k)
            node = MoveNumGame("".join(new_nums), self.end_states)
            self.base_copy(node)
            next_nodes.append(node)
        return next_nodes


def test_next_all_nodes():
    node = MoveNumGame("123458670", eight_num_problem_end_state)
    res = node.next_all_nodes()
    assert len(res) == 2


def test_search_with_bfs():
    node = MoveNumGame("123458670", eight_num_problem_end_state)
    b = bfs.BFS(node)
    depth = b.search()
    assert depth == 1


if __name__ == '__main__':
    test_search_with_bfs()
    test_next_all_nodes()
