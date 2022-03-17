from collections import defaultdict
import copy
import ai

win_pattern = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],
    [1, 5, 9],
    [3, 5, 7],
]

point_map = defaultdict(list)


def init_point_map():
    for p in win_pattern:
        point_map[p[0]].append(p)
        point_map[p[1]].append(p)
        point_map[p[2]].append(p)


def check_win(paces, xxoo_type):
    for p in win_pattern:
        if paces[p[0]] == xxoo_type and paces[p[1]] == xxoo_type and paces[p[2]] == xxoo_type:
            return True
    return False


def fill_all(paces):
    for i in range(1, 10):
        if paces[i] is None:
            return False
    return True


class XXOO:
    def __init__(self, paces=None, last_pace=None):
        if paces is None:
            self.paces = {}
            for i in range(1, 10):
                self.paces[i] = None
        else:
            self.paces = paces
        self._last_pace = last_pace

    def set_last_pace(self, last_pace):
        self._last_pace = last_pace

    def last_pace(self):
        return self._last_pace

    def end(self):
        return check_win(self.paces, ai.player_type_player) or check_win(self.paces, ai.player_type_ai) or fill_all(self.paces)

    def winner(self):
        if check_win(self.paces, ai.player_type_player):
            return ai.player_type_player
        if check_win(self.paces, ai.player_type_ai):
            return ai.player_type_ai
        return None

    def key(self):
        pace_str = "\n{} {} {}\n{} {} {}\n{} {} {}\n".format(self.paces[1], self.paces[2],
                                                             self.paces[3], self.paces[4],
                                                             self.paces[5], self.paces[6], self.paces[7],
                                                             self.paces[8],
                                                             self.paces[9])
        return pace_str

    def next_all_nodes(self, maximizing_player):
        xxoo_type = ai.player_type_ai
        if maximizing_player:
            xxoo_type = ai.player_type_player
        res = []
        for i in range(1, 10):
            if self.paces[i] is not None:
                continue
            paces = copy.copy(self.paces)
            paces[i] = xxoo_type
            res.append(XXOO(paces, i))
        return res

    def evaluate(self):
        win = self.winner()
        if win == ai.player_type_player:
            return ai.max_value
        elif win == ai.player_type_ai:
            return ai.min_value
        # 如何评价当前局面的优劣？有更多赢的可能性
        paces = self.paces
        return evaluate(paces)

    def play(self, index, xxoo_type):
        if index > 9 or index < 1 or self.paces.get(index) is not None:
            return
        self.paces[index] = xxoo_type

    def draw_broad(self):
        print('-----------')
        print(' {} | {} | {}'.format(" " if self.paces[1] is None else "X" if self.paces[1] == ai.player_type_ai else "O",
                                     " " if self.paces[2] is None else "X" if self.paces[2] == ai.player_type_ai else "O",
                                     " " if self.paces[3] is None else "X" if self.paces[3] == ai.player_type_ai else "O"))
        print('-----------')
        print(' {} | {} | {}'.format(" " if self.paces[4] is None else "X" if self.paces[4] == ai.player_type_ai else "O",
                                     " " if self.paces[5] is None else "X" if self.paces[5] == ai.player_type_ai else "O",
                                     " " if self.paces[6] is None else "X" if self.paces[6] == ai.player_type_ai else "O"))
        print('-----------')
        print(' {} | {} | {}'.format(" " if self.paces[7] is None else "X" if self.paces[7] == ai.player_type_ai else "O",
                                     " " if self.paces[8] is None else "X" if self.paces[8] == ai.player_type_ai else "O",
                                     " " if self.paces[9] is None else "X" if self.paces[9] == ai.player_type_ai else "O"))
        print('-----------')


def evaluate(paces, xxoo_type=ai.player_type_player, reverse_type=ai.player_type_ai):
    cur_type_score = 0
    for k in paces.keys():
        v = paces[k]
        if v != xxoo_type:
            continue
        for ps in point_map[k]:
            if paces[ps[0]] != reverse_type and paces[ps[1]] != reverse_type and paces[ps[2]] != reverse_type:
                cur_type_score += 1
    reverse_type_score = 0

    for k in paces.keys():
        v = paces[k]
        if v != reverse_type:
            continue
        for ps in point_map[k]:
            if paces[ps[0]] != xxoo_type and paces[ps[1]] != xxoo_type and paces[ps[2]] != xxoo_type:
                reverse_type_score += 1
    return cur_type_score - reverse_type_score
