import ai


# https://www.jianshu.com/p/3b464aeba078


class AlphaBetaAI:
    def __init__(self, debug=False):
        self.value_cache = {}
        self.debug = debug
        self.tree = None
        if self.debug:
            self.tree = ai.Tree(0, ai.type_min)

    def next_pace(self, node, depth=5, maximizing_player=True):
        if node.end():
            return None
        best_choice = self.search(node, depth, ai.min_value, ai.max_value, maximizing_player, self.tree)
        return best_choice

    def add_debug(self, debug_tree, key, value, depth=None):
        if not self.debug:
            return
        debug_tree.node = key
        debug_tree.value = value
        debug_tree.depth = depth

    def search(self, node, depth, alpha, beta, maximizing_player, debug_tree=None):
        key = node.key()
        choice = self.value_cache.get(key)
        if choice is not None:
            self.add_debug(debug_tree, key, choice.value)
            return choice
        if depth == 0 or node.end():
            value = node.evaluate()
            choice = ai.Choice(value, node.last_pace())
            self.value_cache[key] = choice
            self.add_debug(debug_tree, key, choice.value, depth)
            return choice
        if maximizing_player:
            return self.search_max(alpha, beta, debug_tree, depth, key, maximizing_player, node)
        choice = self.search_min(alpha, beta, debug_tree, depth, key, maximizing_player, node)
        return choice

    def search_min(self, alpha, beta, debug_tree, depth, key, maximizing_player, node):
        v = ai.max_value
        best_pace = None
        nodes = node.next_all_nodes(maximizing_player)
        for child in nodes:
            if child is None:
                break
            if best_pace is None:
                best_pace = child.last_pace()
            choice = self.search(child, depth - 1, alpha, beta, True,
                                 debug_tree.add_new_child() if self.debug else None)
            if choice.value < v:
                v = choice.value
                best_pace = child.last_pace()
            beta = min(beta, v)
            if beta <= alpha:
                break
        choice = ai.Choice(v, best_pace)
        self.value_cache[key] = choice
        self.add_debug(debug_tree, key, choice.value)
        return choice

    def search_max(self, alpha, beta, debug_tree, depth, key, maximizing_player, node):
        v = ai.min_value
        best_pace = None
        nodes = node.next_all_nodes(maximizing_player)
        for child in nodes:
            if child is None:
                break
            if best_pace is None:
                best_pace = child.last_pace()
            choice = self.search(child, depth - 1, alpha, beta, False,
                                 debug_tree.add_new_child() if self.debug else None)
            if choice.value > v:
                v = choice.value
                best_pace = child.last_pace()
            alpha = max(alpha, v)
            if beta <= alpha:
                break
        choice = ai.Choice(v, best_pace)
        self.value_cache[key] = choice
        self.add_debug(debug_tree, key, choice.value)
        return choice
