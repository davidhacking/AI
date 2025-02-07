import time

class Chessboard:
    def __init__(self, movs_str):
        assert movs_str
        movs_str = movs_str.strip()
        # 按换行符分割字符串
        lines = movs_str.split('\n')
        self.moves = []
        for line in lines:
            # 去除行号和点号，再按空格分割得到每一步棋
            moves = line.split('. ')[1].split()
            self.moves.extend(moves)
        self.board = [
            ['R1', 'N1', 'B1', 'A1', 'K', 'A2', 'B2', 'N2', 'R2'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', 'C1', '.', '.', '.', '.', '.', 'C2', '.'],
            ['P1', '.', 'P2', '.', 'P3', '.', 'P4', '.', 'P5'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['p1', '.', 'p2', '.', 'p3', '.', 'p4', '.', 'p5'],
            ['.', 'c1', '.', '.', '.', '.', '.', 'c2', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['r1', 'n1', 'b1', 'a1', 'k', 'a2', 'b2', 'n2', 'r2']
        ]
        self.piece2name = {
            'R': '车', 'N': '马', 'B': '象', 'A': '士', 'K': '将',
            'C': '炮', 'P': '兵', 'r': '车', 'n': '马', 'b': '相',
            'a': '仕', 'k': '帅', 'c': '炮', 'p': '卒'
        }
        self.straight_delta = {
            "1": 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
            "一": 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        }
        self.non_straight_pieces = set(['马', '象', '士', '相', '仕'])
        self.index_dict = {
            '１': 0, '２': 1, '３': 2, '４': 3, '５': 4, '６': 5, '７': 6, '８': 7, '９': 8,
            '1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8,
            '九': 0, '八': 1, '七': 2, '六': 3, '五': 4, '四': 5, '三': 6, '二': 7, '一': 8,
        }
        self.name2piece = {v: k for k, v in self.piece2name.items()}
        self.height = len(self.board)
        self.width = len(self.board[0])
        self.mov_dir = {
            'k': [(0, -1), (1, 0), (0, 1), (-1, 0)],
            'K': [(0, -1), (1, 0), (0, 1), (-1, 0)],
            'a': [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            'A': [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            'b': [(-2, -2), (2, -2), (2, 2), (-2, 2)],
            'B': [(-2, -2), (2, -2), (2, 2), (-2, 2)],
            'n': [(-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1)],
            'N': [(-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1)],
            'p': [(0, -1), (0, 1), (-1, 0), (1, 0)],
            'P': [(0, -1), (0, 1), (-1, 0), (1, 0)]
        }
        moves = self.moves
        self.moves = []
        is_red = True
        for m in moves:
            print(f"before convert {m}")
            m = self.convert_move(m, is_red)
            print(f"after convert {m}")
            # input("输入继续。。")
            self.move_piece(*m)
            self.print_board()
            is_red = not is_red
            self.moves.append(m)

    def print_board(self):
        for i in range(self.height):
            row_str = f"{i:2d} "
            for j in range(self.width):
                piece = str(self.board[i][j])
                if len(piece) == 1:
                    row_str += f"{piece}  "
                else:
                    row_str += f"{piece} "
            print(row_str)

        col_numbers = ' ' * 3
        for j in range(self.width):
            col_numbers += f"{j:2d} "
        print(col_numbers)

    def find_piece(self, piece):
        pieces = []
        for i, row in enumerate(self.board):
            for j, val in enumerate(row):
                if val[0] == piece:
                    pieces.append((j, i))
        return pieces

    def move_piece(self, x1, y1, x2, y2):
        piece = self.board[y1][x1]
        self.board[y1][x1] = '.'
        self.board[y2][x2] = piece

    def convert_move(self, move, is_red):
        """
        将中文着法转换为点对点坐标
        :param move: 中文着法，如 "炮二平四"
        :param is_red: 是否为红方
        :return: 起始坐标和目标坐标，如 ((2, 7), (2, 5))
        """
        # 解析着法
        piece_char = None
        piece_x = None
        piece_y = None
        if move[0] == '前':
            piece_char = move[1]
        elif move[0] == '后':
            piece_char = move[1]
        else:
            piece_char = move[0]
        assert piece_char in self.name2piece
        straight_flag = True
        if piece_char in self.non_straight_pieces:
            straight_flag = False
        piece_char = self.name2piece[piece_char]
        if is_red:
            piece_char = piece_char.lower()
        else:
            piece_char = piece_char.upper()
        pieces = self.find_piece(piece_char)
        assert len(pieces) > 0
        if move[0] == '前':
            if is_red:
                piece_x, piece_y = min(pieces, key=lambda point: point[1])
            else:
                piece_x, piece_y = max(pieces, key=lambda point: point[1])
        elif move[0] == '后':
            if is_red:
                piece_x, piece_y = max(pieces, key=lambda point: point[1])
            else:
                piece_x, piece_y = min(pieces, key=lambda point: point[1])
        else:
            assert move[1] in self.index_dict
            point_x = self.index_dict[move[1]]
            piece_x, piece_y = [item for item in pieces if item[0] == point_x][0]
        assert piece_char is not None
        assert piece_x is not None
        assert piece_y is not None

        direction = move[2]  # 移动方向（进、退、平）
        end_x = piece_x
        end_y = piece_y
        action_delta = None
        if not straight_flag:
            end_x = self.index_dict[move[3]]
            assert piece_char in self.mov_dir
            for dx, dy in self.mov_dir[piece_char]:
                tx = piece_x + dx
                ty = piece_y + dy
                if tx < 0 or tx >= self.width:
                    continue
                if ty < 0 or ty >= self.height:
                    continue
                if end_x == tx:
                    if is_red:
                        if direction == '进' and ty - piece_y > 0:
                            continue
                        elif direction == '退' and ty - piece_y < 0:
                            continue
                    if not is_red:
                        if direction == '退' and ty - piece_y > 0:
                            continue
                        elif direction == '进' and ty - piece_y < 0:
                            continue
                    end_y = ty
        else:
            if direction == '平':
                end_x = self.index_dict[move[3]]
            elif direction == '进' or direction == '退':
                action_delta = self.straight_delta[move[3]]
                if is_red and direction == '进':
                    action_delta = -action_delta
                if not is_red and direction == '退':
                    action_delta = -action_delta
                end_y = piece_y + action_delta
        return piece_x, piece_y, end_x, end_y

class PaceIns:
    _instance = None
    _paces = Chessboard("""
 1. 炮二平四 炮２平５
 2. 马八进七 马２进３
 3. 马二进三 马８进９
 4. 车一平二 车９平８
 5. 车九平八 车１平２
 6. 炮四进五 车２进６
 7. 炮八平九 车２平３
 8. 车八进二 炮８平７
 9. 车二进九 马９退８
10. 相三进五 士６进５
11. 炮四退六 炮５平６
12. 炮四平七 车３平４
13. 车八进四 卒３进１
14. 炮七进四 象７进５
15. 马七进八 车４平３
16. 炮七进一 卒７进１
17. 仕四进五 卒９进１
18. 炮九平六 炮７退１
19. 马八进六 马３退１
20. 马六退七 马１进２
21. 马七进六 马２退３
22. 马六退四 马３进１
23. 炮七退二 炮６进２
24. 兵三进一 卒７进１
25. 炮七平三 炮７进６
26. 炮六平三 马８进９
27. 马四进六 马１进３
28. 马六进四 马３进４
29. 前炮退一 炮６平２
30. 兵五进一 炮２退１
31. 马四退三 马９进８
32. 前炮平二 马４进２
33. 帅五平四 马２退３
34. 炮二进一 马８退６
35. 马三进二 马３进５
36. 炮三进四 马５退７
37. 马二进一 炮２退２
38. 炮二进五 马６退７
39. 炮三进一 卒５进１
40. 马一退二 卒５进１
41. 炮二退一 卒５平６
42. 马二退四 炮２平１
43. 炮三退一 前马进８
44. 马四退二 马８进９
45. 炮三进一 象５进７
46. 炮三平七 炮１进５
47. 炮七退六 炮１平８
48. 炮二退五 马９退７
49. 帅四平五 前马退８
50. 炮二平七 象７退５
51. 前炮进一 马８进６
52. 兵一进一 卒９进１
53. 前炮平一 卒１进１
54. 炮七平九 马７进８
55. 炮一退三 卒１进１
56. 仕五进四 马６进４
57. 炮九平六 卒６进１
58. 仕六进五 马４退５
59. 炮一平四 卒６进１
60. 仕五进四 马５进６
61. 帅五平四 马８进９
62. 炮六进一 马６退５
63. 炮六进二 马９进８
64. 炮四平五 马５进４
65. 炮六平四 马８退６
66. 炮五平六 卒１平２
67. 炮四平三 卒２进１
68. 炮三退一 马６进７
69. 炮六平四 马４退５
70. 炮三退一 卒２平３
71. 炮四平五 马５进７
72. 相五进三 后马退５
73. 相七进五 马５退３
74. 帅四进一 马７进９
75. 帅四退一 马３进４
76. 炮五退一 马９退８
77. 炮五平九 马４退６
78. 炮三平四 卒３平４
79. 炮九进一 卒４平５
80. 炮四退一 马８退９
81. 帅四平五 马６进４
82. 炮九平六 卒５平６
""").moves
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PaceIns, cls).__new__(cls)
            cls._instance.index = 0
        return cls._instance

    def get_pace(self):
        if self.index < len(self._paces):
            pace = self._paces[self.index]
            self.index += 1
            print(f"get_pace {self.index} / {len(self._paces)}")
            return pace
        else:
            return None

class TestChineseChessPlayer():
    def __init__(self, game, player=1):
        self.game = game
        self.player = player
        self.paceIns = PaceIns()

    def play(self, board):
        input("按回车继续")
        s = self.paceIns.get_pace()
        x1, y1, x2, y2 = int(s[0]), int(s[1]), int(s[2]), int(s[3])
        print(f"play {x1},{y1} -> {x2},{y2}")
        a = self.game.move_to_action(board, x1, y1, x2, y2)
        return a


class HumanChineseChessPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valids = self.game.getValidMoves(board, 1)
        for i, v in enumerate(valids):
            if v == 0:
                continue
            print("[", i, end="] ")
        while True:
            input_move = input()
            input_a = input_move.split(" ")
            if len(input_a) == 4:
                try:
                    x1, y1, x2, y2 = [int(i) for i in input_a]
                    a = self.game.move_to_action(board, x1, y1, x2, y2)
                    if valids[a]:
                        break
                except ValueError:
                    # Input needs to be an integer
                    'Invalid integer'
            print('Invalid move')
        return a

movs_str = """
 1. 炮二平四 炮２平５
 2. 马八进七 马２进３
 3. 马二进三 马８进９
 4. 车一平二 车９平８
 5. 车九平八 车１平２
 6. 炮四进五 车２进６
 7. 炮八平九 车２平３
 8. 车八进二 炮８平７
 9. 车二进九 马９退８
10. 相三进五 士６进５
11. 炮四退六 炮５平６
12. 炮四平七 车３平４
13. 车八进四 卒３进１
14. 炮七进四 象７进５
15. 马七进八 车４平３
16. 炮七进一 卒７进１
17. 仕四进五 卒９进１
18. 炮九平六 炮７退１
19. 马八进六 马３退１
20. 马六退七 马１进２
21. 马七进六 马２退３
22. 马六退四 马３进１
23. 炮七退二 炮６进２
24. 兵三进一 卒７进１
25. 炮七平三 炮７进６
26. 炮六平三 马８进９
27. 马四进六 马１进３
28. 马六进四 马３进４
29. 前炮退一 炮６平２
30. 兵五进一 炮２退１
31. 马四退三 马９进８
32. 前炮平二 马４进２
33. 帅五平四 马２退３
34. 炮二进一 马８退６
35. 马三进二 马３进５
36. 炮三进四 马５退７
37. 马二进一 炮２退２
38. 炮二进五 马６退７
39. 炮三进一 卒５进１
40. 马一退二 卒５进１
41. 炮二退一 卒５平６
42. 马二退四 炮２平１
43. 炮三退一 前马进８
44. 马四退二 马８进９
45. 炮三进一 象５进７
46. 炮三平七 炮１进５
47. 炮七退六 炮１平８
48. 炮二退五 马９退７
49. 帅四平五 前马退８
50. 炮二平七 象７退５
51. 前炮进一 马８进６
52. 兵一进一 卒９进１
53. 前炮平一 卒１进１
54. 炮七平九 马７进８
55. 炮一退三 卒１进１
56. 仕五进四 马６进４
57. 炮九平六 卒６进１
58. 仕六进五 马４退５
59. 炮一平四 卒６进１
60. 仕五进四 马５进６
61. 帅五平四 马８进９
62. 炮六进一 马６退５
63. 炮六进二 马９进８
64. 炮四平五 马５进４
65. 炮六平四 马８退６
66. 炮五平六 卒１平２
67. 炮四平三 卒２进１
68. 炮三退一 马６进７
69. 炮六平四 马４退５
70. 炮三退一 卒２平３
71. 炮四平五 马５进７
72. 相五进三 后马退５
73. 相七进五 马５退３
74. 帅四进一 马７进９
75. 帅四退一 马３进４
76. 炮五退一 马９退８
77. 炮五平九 马４退６
78. 炮三平四 卒３平４
79. 炮九进一 卒４平５
80. 炮四退一 马８退９
81. 帅四平五 马６进４
82. 炮九平六 卒５平６
"""

if __name__ == "__main__":
    cb = Chessboard(movs_str)
    for m in cb.moves:
        print(m)