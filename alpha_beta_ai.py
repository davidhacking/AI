import ai

# https://www.jianshu.com/p/3b464aeba078


class AlphaBetaAI:
    def __init__(self):
        self.value_cache = {}

    def next_pace(self, node, depth=5, maximizing_player=True):
        if node.end():
            return None
        best_choice = self.search(node, depth, ai.min_value, ai.max_value, maximizing_player)
        return best_choice

    def search(self, node, depth, alpha, beta, maximizing_player):
        key = node.key()
        choice = self.value_cache.get(key)
        if choice is not None:
            return choice
        if depth == 0 or node.end():
            value = node.evaluate()
            choice = ai.Choice(value, node.last_pace())
            self.value_cache[key] = choice
            return choice
        if maximizing_player:
            v = ai.min_value
            best_pace = None
            for child in node.next_all_nodes(maximizing_player):
                if child is None:
                    break
                if best_pace is None:
                    best_pace = child.last_pace()
                choice = self.search(child, depth - 1, alpha, beta, False)
                if choice.value > v:
                    v = choice.value
                    best_pace = child.last_pace()
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            choice = ai.Choice(v, best_pace)
            self.value_cache[key] = choice
            return choice
        v = ai.max_value
        best_pace = None
        for child in node.next_all_nodes(maximizing_player):
            if child is None:
                break
            if best_pace is None:
                best_pace = child.last_pace()
            choice = self.search(child, depth - 1, alpha, beta, True)
            if choice.value < v:
                v = choice.value
                best_pace = child.last_pace()
            beta = min(beta, v)
            if beta <= alpha:
                break
        choice = ai.Choice(v, best_pace)
        self.value_cache[key] = choice
        return choice
