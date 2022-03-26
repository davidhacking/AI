from ai import ai


class MinMaxAI:
    def __init__(self):
        self.value_cache = {}
        self.tree = ai.Tree(0, ai.type_min)

    def next_pace(self, node, depth=4, maximizing_player=True):
        if node.end():
            return None
        best_choice = self.search(node, depth, maximizing_player, self.tree)
        return best_choice

    def search(self, node, depth, maximizing_player, debug_tree=None):
        key = node.key()
        choice = self.value_cache.get(key)
        if choice is not None:
            debug_tree.node = key
            debug_tree.value = choice.value
            return choice
        if depth == 0 or node.end():
            value = node.evaluate()
            choice = ai.Choice(value, node.last_pace())
            self.value_cache[key] = choice
            debug_tree.node = key
            debug_tree.value = choice.value
            debug_tree.depth = depth
            return choice
        if maximizing_player:
            v = ai.min_value
            best_pace = None
            nodes = node.next_all_nodes(maximizing_player)
            for child in nodes:
                if child is None:
                    break
                t_child = debug_tree.add_new_child()
                if best_pace is None:
                    best_pace = child.last_pace()
                choice = self.search(child, depth - 1, False, t_child)
                if choice.value > v:
                    v = choice.value
                    best_pace = child.last_pace()
            choice = ai.Choice(v, best_pace)
            self.value_cache[key] = choice
            debug_tree.node = key
            debug_tree.value = choice.value
            return choice
        v = ai.max_value
        best_pace = None
        for child in node.next_all_nodes(maximizing_player):
            if child is None:
                break
            t_child = debug_tree.add_new_child()
            if best_pace is None:
                best_pace = child.last_pace()
            choice = self.search(child, depth - 1, True, t_child)
            if choice.value < v:
                v = choice.value
                best_pace = child.last_pace()
        choice = ai.Choice(v, best_pace)
        self.value_cache[key] = choice
        debug_tree.node = key
        debug_tree.value = choice.value
        return choice

