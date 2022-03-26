# breadth-first-search
# 优先检索出一个最短路径的解
import ds


class BFS:
    search_fail_res = 1

    def __init__(self, root):
        self.queue = ds.Queue()
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
                    self.cache[key] = c.evaluate()
