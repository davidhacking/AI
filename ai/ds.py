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


def test_queue():
    q = Queue()
    q.put(1)
    q.put(2)
    q.put(3)
    assert 1 == q.pop()
    assert 2 == q.pop()
    assert 3 == q.pop()
    assert q.pop() is None
    q.put(1)
    assert 1 == q.pop()


if __name__ == '__main__':
    test_queue()
