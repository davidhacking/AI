import copy

red_camp = 0
black_camp = 1

piece_index0 = 0
piece_index1 = 1

# 车价值
chess_c_value = [
    [206, 208, 207, 213, 214, 213, 207, 208, 206],
    [206, 212, 209, 216, 233, 216, 209, 212, 206],
    [206, 208, 207, 214, 216, 214, 207, 208, 206],
    [206, 213, 213, 216, 216, 216, 213, 213, 206],
    [208, 211, 211, 214, 215, 214, 211, 211, 208],

    [208, 212, 212, 214, 215, 214, 212, 212, 208],
    [204, 209, 204, 212, 214, 212, 204, 209, 204],
    [198, 208, 204, 212, 212, 212, 204, 208, 198],
    [200, 208, 206, 212, 200, 212, 206, 208, 200],
    [194, 206, 204, 212, 200, 212, 204, 206, 194]
]


class ChessMap:
    def __init__(self):
        self._chess_map = chess_map


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class BasePiece:
    def __init__(self, camp, index_name, value_map, pos=None):
        self.camp = camp  # 阵营
        self.pos = pos  # 位置
        self.index_name = index_name  # 编号
        self.alive = True  # 是否存活
        self._name = None
        self._camp_chess_name = None
        value_map = copy.copy(value_map)
        if self.camp == red_camp:
            self.value_map = value_map
        else:
            value_map.reverse()
            self.value_map = value_map

        if self.pos is None:
            self.pos = Position()

    def x(self):
        return self.pos.x

    def y(self):
        return self.pos.y

    def move(self, pos):
        self.pos = pos

    def camp_chess_name(self):
        if self._camp_chess_name is not None:
            return self._camp_chess_name
        self._camp_chess_name = "{}{}".format(self.__class__.__name__, self.camp)
        return self._camp_chess_name

    def name(self):
        if self._name is not None:
            return self._name
        self._name = "{}{}{}".format(self.__class__.__name__, self.camp, self.index_name)
        return self._name

    def value(self):
        return self.value_map[self.pos.y][self.pos.x]


class ChessC(BasePiece):
    def __init__(self, camp, index_name, pos=None):
        super().__init__(camp, index_name, chess_c_value, pos)

    def next_pace(self):
        res = []
        # 左侧检索
        for i in range(self.pos.x - 1, -1, -1):
            chess = chess_map[self.pos.y][i]
            if chess is not None:
                if chess.camp != self.camp:
                    res.append(chess.pos)
                break
            res.append(Position(i, self.pos.y))
        # 右侧检索
        for i in range(self.pos.x + 1, 9):
            chess = chess_map[self.pos.y][i]
            if chess is not None:
                if chess.camp != self.camp:
                    res.append(chess.pos)
                break
            res.append(Position(i, self.pos.y))
        # 上侧检索
        for i in range(self.pos.y - 1, -1, -1):
            chess = chess_map[self.pos.x][i]
            if chess is not None:
                if chess.camp != self.camp:
                    res.append(chess.pos)
                break
            res.append(Position(self.pos.x, i))
        # 下侧检索
        for i in range(self.pos.y + 1, 10):
            chess = chess_map[self.pos.x][i]
            if chess is not None:
                if chess.camp != self.camp:
                    res.append(chess.pos)
                break
            res.append(Position(self.pos.x, i))


chess_map = [
    ["C0", 'M0', 'X0', 'S0', 'J0', 'S1', 'X1', 'M1', "C1"],
    [None, None, None, None, None, None, None, None, None],
    [None, 'P0', None, None, None, None, None, 'P1', None],
    ['Z0', None, 'Z1', None, 'Z2', None, 'Z3', None, 'Z4'],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    ['z0', None, 'z1', None, 'z2', None, 'z3', None, 'z4'],
    [None, 'p0', None, None, None, None, None, 'p1', None],
    [None, None, None, None, None, None, None, None, None],
    ["c0", 'm0', 'x0', 's0', 'j0', 's1', 'x1', 'm1', "c1"]
]

chess_pieces = [
    ChessC(red_camp, piece_index0, Position(0, 9)),
    ChessC(red_camp, piece_index1, Position(8, 9)),
    ChessC(black_camp, piece_index0, Position(0, 0)),
    ChessC(black_camp, piece_index1, Position(8, 0)),
]


def init():
    for piece in chess_pieces:
        chess_map[piece.y()][piece.x()] = piece


if __name__ == '__main__':
    pass
