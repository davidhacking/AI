import random

max_value = 99999999
min_value = -max_value

player_type_player = 1
player_type_ai = 2


def copy_pace(paces, strategy_copy=None):
    res = []
    for p in paces:
        if strategy_copy is None:
            res.append(Pace(p.player, p.strategy))
        else:
            res.append(Pace(p.player, strategy_copy(p.strategy)))
    return res


class Pace:
    def __init__(self, player, strategy):
        self.player = player
        self.strategy = strategy

    def __str__(self):
        return "{}_{}".format(self.player, self.strategy)

    def __hash__(self):
        return hash(self.__str__())


class BaseNode:
    def __init__(self, paces=None):
        self.paces = paces
        if self.paces is not None and len(self.paces) > 0:
            self._last_pace = paces[-1]

    def set_last_pace(self, pace):
        self._last_pace = pace

    def last_pace(self):
        return self._last_pace

    # play的pace有可能是空的，因为已经没有最好的策略了
    def random_pace(self):
        if self.paces is None or len(self.paces) <= 0:
            return
        i = random.randint(0, len(self.paces) - 1)
        return self.paces[i]

    def play(self, pace):
        self._last_pace = pace
        self.paces.append(pace)

    def key(self):
        return "|".join([str(p) for p in self.paces])

    def end(self):
        pass

    def next_all_nodes(self, maximizing_player):
        pass

    # 评估玩家的收益
    def evaluate(self):
        pass


class Choice:
    def __init__(self, value, pace):
        self.value = value
        self.pace = pace

    def __str__(self):
        return "value={}, pace={}".format(self.value, self.pace)


type_min = 1
type_max = 2


class Tree:
    def __init__(self, layer, min_max_type):
        self.layer = layer
        self.min_max_type = min_max_type
        self.node = None
        self.value = 0
        self.children = []

    def add_new_child(self):
        t = type_min if self.min_max_type == type_max else type_max
        child = Tree(self.layer + 1, t)
        self.children.append(child)
        return child
