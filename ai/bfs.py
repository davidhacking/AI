# breadth-first-search
# 优先检索出一个最短路径的解
import queue


class BFS:
    def __init__(self, root):
        self.queue = queue.Queue(100)
        self.queue.put(root)
        self.cache = {}

    def search(self, depth=100):
        while True:
            node = self.queue.get()
            if node.end() or len(node.paces()) >= depth:
                return len(node.paces())
            children = node.next_all_nodes()
            for c in children:
                self.queue.put(c)
