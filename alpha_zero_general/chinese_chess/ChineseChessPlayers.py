import time
import random

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
        for i, m in enumerate(moves):
            print(f"{i} before convert {m}")
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
        direction = move[2]  # 移动方向（进、退、平）
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
            points = [item for item in pieces if item[0] == point_x]
            if len(points) == 1:
                piece_x, piece_y = points[0]
            else:
                if piece_char == 'a' or piece_char == 'b':
                    if direction == '进':
                        if points[0][0] > points[1][0]:
                            piece_x, piece_y = points[0]
                        else:
                            piece_x, piece_y = points[1]
                    elif direction == '退':
                        if points[0][0] < points[1][0]:
                            piece_x, piece_y = points[0]
                        else:
                            piece_x, piece_y = points[1]
                if piece_char == 'A' or piece_char == 'B':
                    if direction == '进':
                        if points[0][0] < points[1][0]:
                            piece_x, piece_y = points[0]
                        else:
                            piece_x, piece_y = points[1]
                    elif direction == '退':
                        if points[0][0] > points[1][0]:
                            piece_x, piece_y = points[0]
                        else:
                            piece_x, piece_y = points[1]
                
                if piece_char == 'p':
                    points = sorted(points, key=lambda x: x[0])
                    if move[0] == "一":
                        piece_x, piece_y = points[0]
                    elif move[0] == "二":
                        piece_x, piece_y = points[1]
                    elif move[0] == "三":
                        piece_x, piece_y = points[2]
                    elif move[0] == "四":
                        piece_x, piece_y = points[3]
                    elif move[0] == "五":
                        piece_x, piece_y = points[4]
                if piece_char == 'P':
                    points = sorted(points, key=lambda x: -x[0])
                    if move[0] == "一":
                        piece_x, piece_y = points[0]
                    elif move[0] == "二":
                        piece_x, piece_y = points[1]
                    elif move[0] == "三":
                        piece_x, piece_y = points[2]
                    elif move[0] == "四":
                        piece_x, piece_y = points[3]
                    elif move[0] == "五":
                        piece_x, piece_y = points[4]
        assert piece_char is not None
        assert piece_x is not None
        assert piece_y is not None

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
                if (piece_char == 'k' or piece_char == 'a'):
                    if ty < 7:
                        continue
                if (piece_char == 'K' or piece_char == 'A'):
                    if ty > 2:
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
 1. 兵七进一 象７进５
 2. 马八进七 马８进７
 3. 马二进三 卒７进１
 4. 相三进五 马２进１
 5. 兵九进一 车１进１
 6. 仕四进五 卒３进１
 7. 兵七进一 车１平３
 8. 兵七进一 车３进２
 9. 马七进八 炮２进５
10. 马八进七 马１进３
11. 仕五进六 马３进４
12. 车九进三 炮８进４
13. 车一平四 卒７进１
14. 车九退一 卒７进１
15. 车九平八 卒７进１
16. 炮二退一 卒７进１
17. 炮二进一 马７进６
18. 车四进四 车９平７
19. 车四平三 车７进５
20. 相五进三 马６进５
21. 相七进五 马５进７
22. 仕六进五 马４进６
23. 炮二平一 卒７进１
24. 仕五进四 卒７平６
25. 帅五进一 马７退９
26. 炮一进四 马９进８
27. 帅五平六 马８退６
28. 仕六退五 前马进８
29. 车八进三 马６退５
30. 炮一平九 士６进５
31. 车八进一 炮８退３
32. 车八平五 炮８平１
33. 车五平九 马５进４
34. 兵九进一 马８退９
35. 车九平六 马４退６
36. 仕五退四 马９进７
37. 仕四进五 马７退５
38. 帅六退一 马５退４
39. 兵九平八 马４进３
40. 兵八进一 马３退４
""").moves
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PaceIns, cls).__new__(cls)
            cls._instance.index = 0
        return cls._instance

    def get_pace(self):
        if self.index < len(self._paces):
            pace = self._paces[self.index]
            print(f"get_pace {self.index} / {len(self._paces)}")
            self.index += 1
            return pace
        else:
            self.index += 1
            return None


def convertToBoard(map):
    result = ""
    for _ in range(3):
        result += '               \n'

    for row in map:
        line = '   '
        for cell in row:
            line += cell
        line += '   \n'
        result += line

    for _ in range(3):
        result += '               \n'

    return result

class TestChineseChessPlayer():
    def __init__(self, game, player=1):
        self.game = game
        self.player = player
        self.paceIns = PaceIns()
        self.turn_to_sb = False

    def play(self, board):
        # input("按回车继续")
        s = self.paceIns.get_pace()
        if s is not None:
            x1, y1, x2, y2 = int(s[0]), int(s[1]), int(s[2]), int(s[3])
            print(f"play {x1},{y1} -> {x2},{y2}")
            a = self.game.move_to_action(board, x1, y1, x2, y2)
            return a
        from xqlightpy.ai_play2 import predict_best_move_and_score
        player = 1 if (self.paceIns.index-1) % 2 == 0 else -1
        originBoard = board
        canonicalBoard = self.game.getCanonicalForm(board, player)
        board = self.game.get_fen(canonicalBoard)
        board = board + (' w' if player == 1 else ' b')
        move = predict_best_move_and_score(board)
        if move == "-3-3-3-3":
            self.turn_to_sb = True
        if self.turn_to_sb:
            valids = self.game.getValidMoves(originBoard, 1)
            a = None
            for i in range(len(valids)):
                if valids[i] == 1:
                    a = i
                    next_board, _ = self.game.getNextState(canonicalBoard, player, a)
                    winner = self.game.getGameEnded(next_board, player)
                    if winner != 0:
                        print(f"getGameEnded winner={winner}")
                        return a
            print(f"takeRandom action={a}")
            return a
        x1, y1, x2, y2 = int(move[0]), int(move[1]), int(move[2]), int(move[3])
        print(f"play2 {x1},{y1} -> {x2},{y2}")
        a = self.game.move_to_action(originBoard, x1, y1, x2, y2)
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
