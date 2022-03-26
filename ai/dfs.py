
class DFS:
    def __init__(self, node):
        self.node = node
        self.cache = {}

    def search(self):
        return self._search(self.node)

    def _search(self, node):
        key = node.key()
        result = self.cache.get(key)
        if result is not None:
            return result
        if node.end():
            self.cache[key] = node.paces()
            return

