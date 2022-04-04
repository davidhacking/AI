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