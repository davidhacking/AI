import copy
import chess_value

red_camp = 1
black_camp = 2

piece_index0 = 0
piece_index1 = 1


class ChessMap:
    def __init__(self, pieces=None):
        self._chess_map = []
        self.J0 = None
        self.j0 = None
        for i in range(0, 10):
            self._chess_map.append(list())
            for j in range(0, 9):
                self._chess_map[i].append(None)
        if pieces is not None:
            for piece in pieces:
                piece = piece.copy()
                self._chess_map[piece.y()][piece.x()] = piece
                if piece.name() == J0.name():
                    self.J0 = piece
                elif piece.name() == j0.name():
                    self.j0 = piece

    def get_piece(self, x, y):
        return self._chess_map[y][x]

    def copy(self):
        chess_map = ChessMap()
        for i in range(0, 10):
            for j in range(0, 9):
                chess_map._chess_map[i][j] = self._chess_map[i][j].copy()
                piece = chess_map._chess_map[i][j]
                if piece.name() == J0.name():
                    chess_map.J0 = piece
                elif piece.name() == j0.name():
                    chess_map.j0 = piece


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class BasePiece:
    def __init__(self, camp=None, index_name=None, value_map=None, pos=None):
        self._camp = camp  # 阵营
        self._pos = pos  # 位置
        self._index_name = index_name  # 编号
        self._alive = True  # 是否存活
        self._name = None
        self._camp_chess_name = None
        if value_map is not None:
            value_map = copy.copy(value_map)
            if self._camp == red_camp:
                self._value_map = value_map
            else:
                value_map.reverse()
                self._value_map = value_map

        if self._pos is None:
            self._pos = Position()

    def base_copy(self, piece):
        piece._camp = self._camp
        piece._pos = self._pos
        piece._index_name = self._index_name
        piece._alive = self._alive
        piece._name = self._name
        piece._camp_chess_name = self._camp_chess_name
        piece._value_map = self._value_map

    def pos(self):
        return self._pos

    def camp(self):
        return self._camp

    def x(self):
        return self._pos.x

    def y(self):
        return self._pos.y

    def move(self, pos):
        self._pos = pos

    def camp_chess_name(self):
        if self._camp_chess_name is not None:
            return self._camp_chess_name
        self._camp_chess_name = "{}{}".format(self.__class__.__name__, self._camp)
        return self._camp_chess_name

    def name(self):
        if self._name is not None:
            return self._name
        self._name = "{}{}{}".format(self.__class__.__name__, self._camp, self._index_name)
        return self._name

    def __str__(self):
        return self.name()

    def value(self):
        return self._value_map[self._pos.y][self._pos.x]


class ChessC(BasePiece):
    def __init__(self, camp=None, index_name=None, pos=None):
        super().__init__(camp, index_name, chess_value.chess_c_value, pos)

    def copy(self):
        res = ChessC()
        self.base_copy(res)
        return res

    def next_all_pos(self, chess_map):
        res = []
        # 左右侧检索
        for i in range(0, 9):
            if i == self.x():
                continue
            piece = chess_map.get_piece(i, self.y())
            if piece is not None:
                if piece.camp() != self.camp():
                    res.append(piece.pos())
                break
            res.append(Position(i, self.y()))
        # 上下侧检索
        for i in range(0, 10):
            if i == self.y():
                continue
            piece = chess_map.get_piece(self.x(), i)
            if piece is not None:
                if piece.camp() != self.camp():
                    res.append(piece.pos())
                break
            res.append(Position(self.x(), i))
        return res


class ChessM(BasePiece):
    def __init__(self, camp=None, index_name=None, pos=None):
        super().__init__(camp, index_name, chess_value.chess_m_value, pos)

    def copy(self):
        res = ChessM()
        self.base_copy(res)
        return res

    def next_all_pos(self, chess_map):
        res = []
        x = self.x()
        y = self.y()
        if can_reach(self, chess_map, x + 1, y - 2, x, y - 1):
            res.append(Position(x + 1, y - 2))
        if can_reach(self, chess_map, x + 2, y - 1, x + 1, y):
            res.append(Position(x + 2, y - 1))
        if can_reach(self, chess_map, x + 2, y + 1, x + 1, y):
            res.append(Position(x + 2, y + 1))
        if can_reach(self, chess_map, x + 1, y + 2, x, y + 1):
            res.append(Position(x + 1, y + 2))
        if can_reach(self, chess_map, x - 1, y + 2, x, y + 1):
            res.append(Position(x - 1, y + 2))
        if can_reach(self, chess_map, x - 2, y + 1, x - 1, y):
            res.append(Position(x - 2, y + 1))
        if can_reach(self, chess_map, x - 2, y - 1, x - 1, y):
            res.append(Position(x - 2, y - 1))
        if can_reach(self, chess_map, x - 1, y - 2, x, y - 1):
            res.append(Position(x, y - 2))
        return res


def can_reach(self, chess_map, end_x, end_y, ban_x=None, ban_y=None, x_range=(0, 8),
              y_range=(0, 9)):
    if not x_range[0] <= end_x <= x_range[1] or not y_range[0] <= end_y <= y_range[1]:
        return False
    if (ban_x is not None and not x_range[0] <= ban_x <= x_range[1]) or \
            not (ban_y is not None and y_range[0] <= ban_y <= y_range[1]):
        return False
    if ban_x is not None and ban_y is not None:
        piece = chess_map.get_piece(ban_x, ban_y)
        if piece is not None:
            return False
    piece = chess_map.get_piece(end_x, end_y)
    if piece is not None and piece.camp() == self.camp():
        return False
    return True


class ChessX(BasePiece):
    def __init__(self, camp=None, index_name=None, pos=None):
        super().__init__(camp, index_name, chess_value.chess_x_value, pos)

    def copy(self):
        res = ChessX()
        self.base_copy(res)
        return res

    def next_all_pos(self, chess_map):
        res = []
        x = self.x()
        y = self.y()
        if can_reach(self, chess_map, x + 2, y + 2, x + 1, y + 1):
            res.append(Position(x + 2, y + 2))
        if can_reach(self, chess_map, x - 2, y + 2, x - 1, y + 1):
            res.append(Position(x - 2, y + 2))
        if can_reach(self, chess_map, x + 2, y - 2, x + 1, y - 1):
            res.append(Position(x + 2, y - 2))
        if can_reach(self, chess_map, x - 2, y - 2, x - 1, y - 1):
            res.append(Position(x - 2, y - 2))
        return res


class ChessS(BasePiece):
    def __init__(self, camp=None, index_name=None, pos=None):
        super().__init__(camp, index_name, chess_value.chess_x_value, pos)

    def copy(self):
        res = ChessS()
        self.base_copy(res)
        return res

    def next_all_pos(self, chess_map):
        res = []
        x = self.x()
        y = self.y()
        x_range = (3, 5)
        y_range = (7, 9) if self.camp() == red_camp else (0, 2)
        if can_reach(self, chess_map, x + 1, y + 1, ban_x=None, ban_y=None, x_range=x_range, y_range=y_range):
            res.append(Position(x + 1, y + 1))
        if can_reach(self, chess_map, x - 1, y + 1, ban_x=None, ban_y=None, x_range=x_range, y_range=y_range):
            res.append(Position(x - 1, y + 1))
        if can_reach(self, chess_map, x + 1, y - 1, ban_x=None, ban_y=None, x_range=x_range, y_range=y_range):
            res.append(Position(x + 1, y - 1))
        if can_reach(self, chess_map, x - 1, y - 1, ban_x=None, ban_y=None, x_range=x_range, y_range=y_range):
            res.append(Position(x - 1, y - 1))
        return res


class ChessJ(BasePiece):
    def __init__(self, camp=None, index_name=None, pos=None):
        super().__init__(camp, index_name, chess_value.chess_x_value, pos)

    def copy(self):
        res = ChessJ()
        self.base_copy(res)
        return res

    def next_all_pos(self, chess_map):
        res = []
        x = self.x()
        y = self.y()
        x_range = (3, 5)
        y_range = (7, 9) if self.camp() == red_camp else (0, 2)
        if can_reach(self, chess_map, x, y + 1, ban_x=None, ban_y=None, x_range=x_range, y_range=y_range):
            res.append(Position(x, y + 1))
        if can_reach(self, chess_map, x - 1, y, ban_x=None, ban_y=None, x_range=x_range, y_range=y_range):
            res.append(Position(x - 1, y))
        if can_reach(self, chess_map, x, y - 1, ban_x=None, ban_y=None, x_range=x_range, y_range=y_range):
            res.append(Position(x, y - 1))
        if can_reach(self, chess_map, x + 1, y, ban_x=None, ban_y=None, x_range=x_range, y_range=y_range):
            res.append(Position(x + 1, y))
        adversary = chess_map.J0 if self.camp() == red_camp else chess_map.j0
        flag = True
        for i in range(chess_map.J0.y() + 1, chess_map.j0.y()):
            piece = chess_map.get_piece(self.x(), i)
            if piece is not None:
                flag = False
        if flag:
            res.append(Position(adversary.x(), adversary.y()))


class ChessPParam:
    def __init__(self, res, flag):
        self.res = res
        self.flag = flag


class ChessP(BasePiece):
    def __init__(self, camp=None, index_name=None, pos=None):
        super().__init__(camp, index_name, chess_value.chess_x_value, pos)

    def copy(self):
        res = ChessP()
        self.base_copy(res)
        return res

    def iter_piece(self, x, y, chess_map, param):
        piece = chess_map.get_piece(x, y)
        if piece is None and not param.flag:
            param.res.append(Position(x, y))
            return True
        if piece is not None and param.flag and piece.camp() != self.camp():
            param.res.append(Position(x, y))
            return False
        if piece is not None and not param.flag:
            param.flag = True
        return True

    def next_all_pos(self, chess_map):
        res = []
        x = self.x()
        y = self.y()
        # 左侧检索
        param = ChessPParam(res, False)
        for i in range(x - 1, -1, -1):
            self.iter_piece(i, y, chess_map, param)
        res = param.res
        param = ChessPParam(res, False)
        for i in range(x + 1, 9):
            self.iter_piece(i, y, chess_map, param)
        res = param.res
        param = ChessPParam(res, False)
        for i in range(y - 1, -1, -1):
            self.iter_piece(x, i, chess_map, param)
        res = param.res
        param = ChessPParam(res, False)
        for i in range(y + 1, 10):
            self.iter_piece(x, i, chess_map, param)
        res = param.res
        return res


class ChessZ(BasePiece):
    def __init__(self, camp=None, index_name=None, pos=None):
        super().__init__(camp, index_name, chess_value.chess_x_value, pos)

    def copy(self):
        res = ChessZ()
        self.base_copy(res)
        return res

    def next_all_pos(self, chess_map):
        res = []
        x = self.x()
        y = self.y()
        if self.camp() == red_camp:
            if can_reach(self, chess_map, x, y - 1):
                res.append(Position(x, y - 1))
            if can_reach(self, chess_map, x + 1, y, y_range=(4, 9)):
                res.append(Position(x + 1, y))
            if can_reach(self, chess_map, x - 1, y, y_range=(4, 9)):
                res.append(Position(x - 1, y))
        else:
            if can_reach(self, chess_map, x, y + 1):
                res.append(Position(x, y + 1))
            if can_reach(self, chess_map, x + 1, y, y_range=(6, 9)):
                res.append(Position(x + 1, y))
            if can_reach(self, chess_map, x - 1, y, y_range=(6, 9)):
                res.append(Position(x - 1, y))
        return res


"""
 chess_map = [
   0      1     2     3     4     5     6     7     8
 0 ["C0", 'M0', 'X0', 'S0', 'J0', 'S1', 'X1', 'M1', "C1"],
 1 [None, None, None, None, None, None, None, None, None],
 2 [None, 'P0', None, None, None, None, None, 'P1', None],
 3 ['Z0', None, 'Z1', None, 'Z2', None, 'Z3', None, 'Z4'],
 4 [None, None, None, None, None, None, None, None, None],
 5 [None, None, None, None, None, None, None, None, None],
 6 ['z0', None, 'z1', None, 'z2', None, 'z3', None, 'z4'],
 7 [None, 'p0', None, None, None, None, None, 'p1', None],
 8 [None, None, None, None, None, None, None, None, None],
 9 ["c0", 'm0', 'x0', 's0', 'j0', 's1', 'x1', 'm1', "c1"]
 ]
"""

c0 = ChessC(red_camp, piece_index0, Position(0, 9))
c1 = ChessC(red_camp, piece_index1, Position(8, 9))
C0 = ChessC(black_camp, piece_index0, Position(0, 0))
C1 = ChessC(black_camp, piece_index1, Position(8, 0))

m0 = ChessM(red_camp, piece_index0, Position(1, 9))
m1 = ChessM(red_camp, piece_index1, Position(7, 9))
M0 = ChessM(black_camp, piece_index0, Position(1, 0))
M1 = ChessM(black_camp, piece_index1, Position(7, 0))

x0 = ChessX(red_camp, piece_index0, Position(2, 9))
x1 = ChessX(red_camp, piece_index1, Position(6, 9))
X0 = ChessX(black_camp, piece_index0, Position(2, 0))
X1 = ChessX(black_camp, piece_index1, Position(6, 0))

s0 = ChessS(red_camp, piece_index0, Position(3, 9))
s1 = ChessS(red_camp, piece_index1, Position(5, 9))
S0 = ChessS(black_camp, piece_index0, Position(3, 0))
S1 = ChessS(black_camp, piece_index1, Position(5, 0))

j0 = ChessJ(red_camp, piece_index0, Position(4, 9))
J0 = ChessJ(black_camp, piece_index0, Position(4, 0))

p0 = ChessP(red_camp, piece_index0, Position(1, 7))
p1 = ChessP(red_camp, piece_index1, Position(7, 7))
P0 = ChessP(black_camp, piece_index0, Position(1, 2))
P1 = ChessP(black_camp, piece_index1, Position(7, 2))

z0 = ChessZ(red_camp, piece_index0, Position(0, 6))
z1 = ChessZ(red_camp, piece_index0, Position(2, 6))
z2 = ChessZ(red_camp, piece_index0, Position(4, 6))
z3 = ChessZ(red_camp, piece_index0, Position(6, 6))
z4 = ChessZ(red_camp, piece_index0, Position(8, 6))
Z0 = ChessZ(black_camp, piece_index0, Position(0, 3))
Z1 = ChessZ(black_camp, piece_index0, Position(2, 3))
Z2 = ChessZ(black_camp, piece_index0, Position(4, 3))
Z3 = ChessZ(black_camp, piece_index0, Position(6, 3))
Z4 = ChessZ(black_camp, piece_index0, Position(8, 3))

init_chess_pieces = [
    c0,
    c1,
    C0,
    C1,
    m0,
    m1,
    M0,
    M1,
    x0,
    x1,
    X0,
    X1,
    s0,
    s1,
    S0,
    S1,
    j0,
    J0,
    p0,
    p1,
    P0,
    P1,
    z0,
    z1,
    z2,
    z3,
    z4,
    Z0,
    Z1,
    Z2,
    Z3,
    Z4,
]

if __name__ == '__main__':
    pass
