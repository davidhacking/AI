import copy
import chess_value

red_camp = 'Red'
black_camp = 'Black'

piece_index0 = 0
piece_index1 = 1


class ChessMap:
    def __init__(self, pieces):
        self._chess_map = []
        # self.name2piece = {}
        for i in range(0, 10):
            self._chess_map.append(list())
            for j in range(0, 9):
                self._chess_map[i].append(None)
        for piece in pieces:
            self._chess_map[piece.y()][piece.x()] = piece
        #     self.name2piece[piece.name()] = piece

    def get_piece(self, x, y):
        return self._chess_map[y][x]


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class BasePiece:
    def __init__(self, camp, index_name, value_map, pos=None):
        self._camp = camp  # 阵营
        self._pos = pos  # 位置
        self.index_name = index_name  # 编号
        self.alive = True  # 是否存活
        self._name = None
        self._camp_chess_name = None
        value_map = copy.copy(value_map)
        if self._camp == red_camp:
            self.value_map = value_map
        else:
            value_map.reverse()
            self.value_map = value_map

        if self._pos is None:
            self._pos = Position()

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
        self._name = "{}{}{}".format(self.__class__.__name__, self._camp, self.index_name)
        return self._name

    def value(self):
        return self.value_map[self._pos.y][self._pos.x]


class ChessC(BasePiece):
    def __init__(self, camp, index_name, pos=None):
        super().__init__(camp, index_name, chess_value.chess_c_value, pos)

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
    def __init__(self, camp, index_name, pos=None):
        super().__init__(camp, index_name, chess_value.chess_m_value, pos)

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
    def __init__(self, camp, index_name, pos=None):
        super().__init__(camp, index_name, chess_value.chess_x_value, pos)

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
    def __init__(self, camp, index_name, pos=None):
        super().__init__(camp, index_name, chess_value.chess_x_value, pos)

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
    def __init__(self, camp, index_name, pos=None):
        super().__init__(camp, index_name, chess_value.chess_x_value, pos)

    def adversary(self):
        old_str = red_camp if self.camp() == red_camp else black_camp
        new_str = black_camp if self.camp() == red_camp else red_camp
        return self.name().replace(old_str, new_str)

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
        adversary = J0 if self.camp() == red_camp else j0
        flag = False
        for i in range(J0.y() + 1, j0.y()):
            piece = chess_map.get_piece(self.x(), i)
            if piece is not None:
                flag = True
        if flag:
            res.append(Position(adversary.pos().x, adversary.pos().y))


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
]

if __name__ == '__main__':
    pass
