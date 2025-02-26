import numpy as np
from enum import Enum
import random

Winner = Enum("Winner", "red black draw")

MaximumTurnsWithoutPieceCapture = 640

def action_encode(piece_index, action_num):
    """
    将棋子索引和动作编号编码为单个整数
    参数范围：
    - piece_index: 0-31 (32种可能)
    - action_num: 0-18 (19种可能)
    输出范围：0-607 (607种组合)
    """
    if not 0 <= piece_index <= 31:
        raise ValueError("棋子索引需在0-31之间")
    if not 0 <= action_num <= 18:
        raise ValueError("动作编号需在0-18之间")
    return piece_index * 19 + action_num

def decode_action(action):
    """
    将编码后的动作解码为原始棋子索引和动作编号
    参数范围：0-607
    """
    if not 0 <= action <= 607:
        raise ValueError("动作编码需在0-607之间")
    
    piece_index = action // 19
    action_num = action % 19
    return (piece_index, action_num)

class ChineseChessBoard():
    RED = 1
    BLACK = -1
    INIT_BOARD = [
        ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', 'C', '.', '.', '.', '.', '.', 'C', '.'],
        ['P', '.', 'P', '.', 'P', '.', 'P', '.', 'P'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['p', '.', 'p', '.', 'p', '.', 'p', '.', 'p'],
        ['.', 'c', '.', '.', '.', '.', '.', 'c', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r']
    ]

    Fen_2_Idx = {
        'p': 0,
        'c': 1,
        'r': 2,
        'k': 3,
        'b': 4,
        'a': 5,
        'n': 6,
        'P': 7,
        'C': 8,
        'R': 9,
        'K': 10,
        'B': 11,
        'A': 12,
        'N': 13
    }
    Idx_2_Fen = {
        v: k for k, v in Fen_2_Idx.items()
    }
    PIECE_NUM = len(Fen_2_Idx.keys())
    BOARD_HEIGHT = len(INIT_BOARD)
    BOARD_WIDTH = len(INIT_BOARD[0])
    def __init__(self, board=None):
        if board is not None:
            self.board = np.copy(board)
        else:
            self.board = ChineseChessBoard.get_board_array(ChineseChessBoard.INIT_BOARD)
        self.height = ChineseChessBoard.BOARD_HEIGHT
        self.width = ChineseChessBoard.BOARD_WIDTH
        self.piece_index_to_point = {}
        self.point_to_piece_index = {}
        piece_index = 0
        self.k_point = None
        self.K_point = None
        for i in range(self.height):
            for j in range(self.width):
                piece = self[i, j]
                if piece == 'k':
                    self.k_point = (j, i)
                elif piece == 'K':
                    self.K_point = (j, i)
                if piece != '.':
                    self.piece_index_to_point[piece_index] = (j, i)
                    self.point_to_piece_index[(j, i)] = piece_index
                    piece_index += 1
        self.get_legal_actions_flag = False
        self.get_legal_actions()

    def to_fen(self):
        fen_parts = []
        for i in range(self.height):
            empty_count = 0
            row_str = ""
            for j in range(self.width):
                cell = self[i, j]
                if cell == '.':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += cell.swapcase()
            if empty_count > 0:
                row_str += str(empty_count)
            fen_parts.append(row_str)
        fen = '/'.join(fen_parts)
        return fen
    
    def fen_to_planes(self):
        planes = np.zeros(shape=(self.PIECE_NUM, self.BOARD_HEIGHT, self.BOARD_WIDTH), dtype=np.float32)
        for i in range(self.height):
            for j in range(self.width):
                index = i * self.width + j
                idx = int(self.board[index])
                if idx != 0:
                    planes[idx-1][i][j] = 1
        return planes
    
    @staticmethod
    def from_planes(b):
        is_all_zero = np.all(b == 0, axis=0)
        b = np.where(is_all_zero, -1, np.argmax(b, axis=0))
        board = ChineseChessBoard()
        for i in range(10):
            for j in range(9):
                board[i, j] = '.' if b[i][j] == -1 else ChineseChessBoard.Idx_2_Fen[b[i][j]]
        board = ChineseChessBoard(board.board)
        return board

    def __getitem__(self, index):
        i, j = index
        index = i * self.width + j
        if self.board[index] == 0:
            return "."
        return self.Idx_2_Fen[self.board[index]-1]
    
    def __setitem__(self, index, value):
        i, j = index
        index = i * self.width + j
        if value in self.Fen_2_Idx:
            self.board[index] = self.Fen_2_Idx[value]+1
        else:
            self.board[index] = 0

    def get_turn_num(self):
        return self.board[self.height*self.width]
    
    def inc_turn_num(self):
        self.board[self.height*self.width] += 1
    
    def get_last_piece_capture_turn_num(self):
        return self.board[self.height*self.width+1]

    def set_last_piece_capture_turn_num(self, value):
        self.board[self.height*self.width+1] = value

    def get_winner(self, color):
        if self.K_point is None:
            # print(f"no black king red win")
            return Winner.red
        if self.k_point is None:
            # print(f"no red king black win")
            return Winner.black
        t = self.get_turn_num() - self.get_last_piece_capture_turn_num()
        if t > MaximumTurnsWithoutPieceCapture:
            return Winner.draw
        return None

    def print_board(self):
        for i in range(self.height):
            row_str = f"{i:1d} "
            for j in range(self.width):
                piece = str(self[i, j])
                row_str += f"{piece} "
            print(row_str)

        col_numbers = ' ' * 2
        for j in range(self.width):
            col_numbers += f"{j:1d} "
        print(col_numbers)
        print(f"turn_num={self.get_turn_num()}, lpctn={self.get_last_piece_capture_turn_num()}")

    @staticmethod
    def get_board_array(ch_board):
        board = np.zeros((ChineseChessBoard.BOARD_HEIGHT, ChineseChessBoard.BOARD_WIDTH), dtype=np.float32)
        for i, row in enumerate(ch_board):
            for j, piece in enumerate(row):
                if piece in ChineseChessBoard.Fen_2_Idx:
                    board[i, j] = ChineseChessBoard.Fen_2_Idx[piece]+1
                else:
                    board[i, j] = 0
        turn_num, last_piece_capture_turn_num = 0, 0
        extra_info = np.array([turn_num, last_piece_capture_turn_num], dtype=np.float32)
        return np.concatenate((board.flatten(), extra_info))
    
    def get_legal_actions(self, color=RED):
        if self.get_legal_actions_flag:
            return self._red_legal_actions if color == ChineseChessBoard.RED else self._black_legal_actions
        self.get_legal_actions_flag = True
        self._red_legal_moves = set(self._init_legal_moves(ChineseChessBoard.RED))
        red_legal_actions = []
        self._kill_K_moves = []
        for move in self._red_legal_moves:
            a = self.move_to_action(*move)
            if self[move[3], move[2]] == 'K':
                self._kill_K_moves.append(move)
            red_legal_actions.append(a)
        self._red_legal_actions = set(red_legal_actions)
        self._black_legal_moves = set(self._init_legal_moves(ChineseChessBoard.BLACK))
        black_legal_actions = []
        self._kill_k_moves = []
        for move in self._black_legal_moves:
            a = self.move_to_action(*move)
            if self[move[3], move[2]] == 'k':
                self._kill_k_moves.append(move)
            black_legal_actions.append(a)
        self._black_legal_actions = set(black_legal_actions)
        return self._red_legal_actions if color == ChineseChessBoard.RED else self._black_legal_actions

    mov_dir = {
        'k': [(0, -1), (1, 0), (0, 1), (-1, 0), 
              (0, -9), (0, -8), (0, -7), (0, -6), (0, -5),
              (0, 9), (0, 8), (0, 7), (0, 6), (0, 5)],
        'K': [(0, -1), (1, 0), (0, 1), (-1, 0), 
              (0, -9), (0, -8), (0, -7), (0, -6), (0, -5),
              (0, 9), (0, 8), (0, 7), (0, 6), (0, 5)],
        'a': [(-1, -1), (1, -1), (-1, 1), (1, 1)],
        'A': [(-1, -1), (1, -1), (-1, 1), (1, 1)],
        'b': [(-2, -2), (2, -2), (2, 2), (-2, 2)],
        'B': [(-2, -2), (2, -2), (2, 2), (-2, 2)],
        'n': [(-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1)],
        'N': [(-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1)],
        'p': [(0, -1), (0, 1), (-1, 0), (1, 0)],
        'P': [(0, -1), (0, 1), (-1, 0), (1, 0)]
    }
    stright_action_func = lambda name, action_index, x, y: (action_index, y) if action_index <= 8 else (x, action_index - 9)
    action_func = lambda name, action_index, x, y: (x + ChineseChessBoard.mov_dir[name][action_index][0], y + ChineseChessBoard.mov_dir[name][action_index][1])
    r_stright_action_func = lambda name, x1, y1, x2, y2: x2 if y1 == y2 else (y2 + 9)
    r_action_func = lambda name, x1, y1, x2, y2: ChineseChessBoard.mov_dir[name].index((x2 - x1, y2 - y1))
    
    action_dict = {
        "r": stright_action_func,
        "c": stright_action_func,
        "n": action_func,
        "b": action_func,
        "a": action_func,
        "p": action_func,
        "k": action_func,
        "R": stright_action_func,
        "C": stright_action_func,
        "N": action_func,
        "B": action_func,
        "A": action_func,
        "P": action_func,
        "K": action_func,
    }
    action_size = 608
    
    def _is_same_side(self, x, y, color):
        if color == ChineseChessBoard.RED and self[y, x].islower():
            return True
        if color == ChineseChessBoard.BLACK and self[y, x].isupper():
            return True
        return False
    
    def _can_move(self, x, y, color): # basically check the move
        if x < 0 or x > self.width - 1:
            return False
        if y < 0 or y > self.height - 1:
            return False
        if self._is_same_side(x, y, color):
            return False
        return True

    def _x_board_from(self, x, y):
        l = x - 1
        r = x + 1
        while l > -1 and self[y, l] == '.':
            l = l - 1
        while r < self.width and self[y, r] == '.':
            r = r + 1
        return l, r

    def _y_board_from(self, x, y):
        d = y - 1
        u = y + 1
        while d > -1 and self[d, x] == '.':
            d = d - 1
        while u < self.height and self[u, x] == '.':
            u = u + 1
        return d, u
    
    def is_red_at_bottom(self):
        kx, ky = self.k_point
        Kx, Ky = self.K_point
        board_flag = True # 红棋位于棋盘下方
        if ky >= 0 and ky <= 2:
            board_flag = False # 红棋位于棋盘上方方
        return board_flag
    
    def has_block_in_kings(self):
        kx, ky = self.k_point
        Kx, Ky = self.K_point
        if kx != Kx:
            return True
        has_block = False
        i = min(Ky, ky) + 1
        while i < max(ky, Ky):
            if self[i, kx] != '.':
                has_block = True
                break
            i += 1
        return has_block

    def _init_legal_moves(self, color): # 先判断老将的位置，如果没有老将直接返回空，按老将的位置判定小兵活动范围
        if self.k_point is None or self.K_point is None:
            return []
        kx, ky = self.k_point
        Kx, Ky = self.K_point
        board_flag = self.is_red_at_bottom()
        has_block = self.has_block_in_kings()
        _legal_moves = []
        for y in range(self.height):
            for x in range(self.width):
                ch = self[y, x]
                if (color == ChineseChessBoard.RED and ch.isupper()):
                    continue
                if (color == ChineseChessBoard.BLACK and ch.islower()):
                    continue
                if ch in ChineseChessBoard.mov_dir:
                    for d in ChineseChessBoard.mov_dir[ch]:
                        x_ = x + d[0]
                        y_ = y + d[1]
                        if not self._can_move(x_, y_, color):
                            continue
                        elif ch == 'p':  # for red pawn
                            if board_flag:
                                if y_ > 6 or y_ > y:
                                    continue
                            else:
                                if y_ < 3 or y_ < y:
                                    continue
                            if board_flag:
                                if y > 4 and x_ != x:
                                    continue
                            else:
                                if y < 5 and x_ != x:
                                    continue
                        elif ch == 'P':  # for black pawn
                            if board_flag:
                                if y_ < 3 or y_ < y:
                                    continue
                            else:
                                if y_ > 6 or y_ > y:
                                    continue
                            if board_flag:
                                if y < 5 and x_ != x:
                                    continue
                            else:
                                if y > 4 and x_ != x:
                                    continue
                        elif ch == 'n' or ch == 'N' or ch == 'b' or ch == 'B': # for knight and bishop
                            if ch == 'b':
                                if board_flag:
                                    if y_ < 5:
                                        continue
                                else:
                                    if y_ > 4:
                                        continue
                            if ch == 'B':
                                if board_flag:
                                    if y_ > 4:
                                        continue
                                else:
                                    if y_ < 5:
                                        continue
                            if self[y+int(d[1]/2), x+int(d[0]/2)] != '.':
                                continue
                            if ch == 'b':
                                if board_flag:
                                    if y < 5:
                                        continue
                                else:
                                    if y > 4:
                                        continue
                            if ch == 'B':
                                if board_flag:
                                    if y > 4:
                                        continue
                                else:
                                    if y < 5:
                                        continue
                        elif ch != 'p' and ch != 'P': # for king and advisor
                            if x_ < 3 or x_ > 5 or y_ < 0 or y_ > 9:
                                continue
                            if ch == 'a':
                                if board_flag:
                                    if y_ < 7:
                                        continue
                                else:
                                    if y_ > 2:
                                        continue
                            if ch == 'A':
                                if board_flag:
                                    if y_ > 2:
                                        continue
                                else:
                                    if y_ < 7:
                                        continue
                            if ch == 'k':
                                if has_block:
                                    if board_flag:
                                        if y_ < 7:
                                            continue
                                    else:
                                        if y_ > 2:
                                            continue
                                else:
                                    if board_flag:
                                        if y_ < 7 and (x_ != Kx or y_ != Ky):
                                            continue
                                    else:
                                        if y_ > 2 and (x_ != Kx or y_ != Ky):
                                            continue
                            if ch == 'K':
                                if has_block:
                                    if board_flag:
                                        if y_ > 2:
                                            continue
                                    else:
                                        if y_ < 7:
                                            continue
                                else:
                                    if board_flag:
                                        if y_ > 2 and (x_ != kx or y_ != ky):
                                            continue
                                    else:
                                        if y_ < 7 and (x_ != kx or y_ != ky):
                                            continue
                        _legal_moves.append((x, y, x_, y_))
                        
                elif ch != '.': # for connon and root
                    l,r = self._x_board_from(x,y)
                    d,u = self._y_board_from(x,y)
                    for x_ in range(l+1,x):
                        _legal_moves.append((x, y, x_, y))
                    for x_ in range(x+1,r):
                        _legal_moves.append((x, y, x_, y))
                    for y_ in range(d+1,y):
                        _legal_moves.append((x, y, x, y_))
                    for y_ in range(y+1,u):
                        _legal_moves.append((x, y, x, y_))
                    if ch == 'r' or ch == 'R': # for root
                        if self._can_move(l, y, color):
                            _legal_moves.append((x, y, l, y))
                        if self._can_move(r, y, color):
                            _legal_moves.append((x, y, r, y))
                        if self._can_move(x, d, color):
                            _legal_moves.append((x, y, x, d))
                        if self._can_move(x, u, color):
                            _legal_moves.append((x, y, x, u))
                    else: # for connon
                        l_, _ = self._x_board_from(l,y)
                        _, r_ = self._x_board_from(r,y)
                        d_, _ = self._y_board_from(x,d)
                        _, u_ = self._y_board_from(x,u)
                        if self._can_move(l_, y, color):
                            _legal_moves.append((x, y, l_, y))
                        if self._can_move(r_, y, color):
                            _legal_moves.append((x, y, r_, y))
                        if self._can_move(x, d_, color):
                            _legal_moves.append((x, y, x, d_))
                        if self._can_move(x, u_, color):
                            _legal_moves.append((x, y, x, u_))
        _legal_moves = [move for move in _legal_moves if not (move[0] == move[2] and move[1] == move[3])]
        return _legal_moves

    def isValidAction(self, action, color):
        if color == ChineseChessBoard.RED:
            b = action in self._red_legal_actions
        else:
            b = action in self._black_legal_actions
        if not b:
            print(f"isValidAction action={action} color={color}")
            print(f"_red_legal_actions={sorted(list(self._red_legal_actions))}")
            print(f"_black_legal_actions={sorted(list(self._black_legal_actions))}")
            self.print_board()
        return b

    def move_to_action(self, x1, y1, x2, y2):
        assert (x1, y1) in self.point_to_piece_index
        ch = self[y1, x1]
        piece_index = self.point_to_piece_index[(x1, y1)]
        d = (x2-x1, y2-y1)
        if ch in ['r', 'R', 'c', 'C']:
            action_index = ChineseChessBoard.r_stright_action_func(ch, x1, y1, x2, y2)
        else:
            action_index = ChineseChessBoard.r_action_func(ch, x1, y1, x2, y2)
        return action_encode(piece_index, action_index)

    def action_to_move(self, action):
        piece_index, action_index = decode_action(action)
        assert piece_index in self.piece_index_to_point
        x1, y1 = self.piece_index_to_point[piece_index]
        ch = self[y1, x1]
        assert ch != "."
        action_item = ChineseChessBoard.action_dict[ch]
        x2, y2 = action_item(ch, action_index, x1, y1)
        return x1, y1, x2, y2
        
    def takeAction(self, action, color):
        # print(f"takeAction action={action} color={color}")
        assert self.isValidAction(action, color)
        x1, y1, x2, y2 = self.action_to_move(action)
        ch = self[y1, x1]
        old_piece = self[y2, x2]
        self[y1, x1] = '.'
        self[y2, x2] = ch
        if old_piece != '.':
            self.set_last_piece_capture_turn_num(self.get_turn_num())
        self.inc_turn_num()

class ChineseChessGame():
    """
    This class specifies the base Game class. To define your own game, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.

    Use 1 for player1 and -1 for player2.

    See othello/OthelloGame.py for an example implementation.
    """
    def __init__(self, board=None):
        self.cnt = 0
        if board is not None:
            self.board = ChineseChessBoard(board)
        else:
            self.board = ChineseChessBoard()
    
    def getSearchAIAction(self, board, need_random=False):
        board = ChineseChessBoard(board)
        if len(board._kill_K_moves) > 0:
            m = board._kill_K_moves[0]
            # print(f"board._kill_K_moves={board._kill_K_moves}")
            return board.move_to_action(*m)
        is_red_at_bottom = board.is_red_at_bottom()
        color = ' w'
        if not is_red_at_bottom:
            color = ' b'
            board = self.getCanonicalForm(board.board, -1)
            board = ChineseChessBoard(board)
        # board.print_board()
        from chinese_chess.xqlightpy.ai_play2 import predict_best_move_and_score
        fen_board = board.to_fen()
        fen_board = fen_board + color
        # print(f"is_red_at_bottom={is_red_at_bottom} fen_board={fen_board}")
        move = predict_best_move_and_score(fen_board)
        # print(f"move={move}")
        try:
            x1, y1, x2, y2 = int(move[0]), int(move[1]), int(move[2]), int(move[3])
            return board.move_to_action(x1, y1, x2, y2)
        except Exception as e:
            if need_random:
                return random.choice(list(board._red_legal_actions)) if is_red_at_bottom else random.choice(list(board._black_legal_actions))
            else:
                return -1
    
    def getInitBoard(self):
        return ChineseChessBoard().board
    
    def getBoardSize(self):
        return (ChineseChessBoard.PIECE_NUM, self.board.height, self.board.width)

    def getActionSize(self):
        return ChineseChessBoard.action_size

    def getNextState(self, board, player, action):
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        self.cnt += 1
        next_player = -player
        board = ChineseChessBoard(board)
        board.takeAction(action, player)
        return board.board, next_player

    def getValidMoves(self, board, player):
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        valid_moves = [0] * self.getActionSize()
        board = ChineseChessBoard(board)
        actions = board.get_legal_actions(player)
        for a in actions:
            valid_moves[a] = 1
        return valid_moves

    def getGameEnded(self, board, player):
        board = ChineseChessBoard(board)
        winner = board.get_winner(player)
        if winner is None:
            return 0
        if winner == Winner.draw:
            return 0.000001
        if player == ChineseChessBoard.RED:
            if winner == Winner.red:
                return 1
            elif winner == Winner.black:
                return -1
        if player == ChineseChessBoard.BLACK:
            if winner == Winner.black:
                return 1
            elif winner == Winner.red:
                return -1
        return 0

    def getCanonicalForm(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """
        if player == ChineseChessBoard.RED:
            return board

        board = ChineseChessBoard(board)
        for i in range(ChineseChessBoard.BOARD_HEIGHT):
            for j in range(ChineseChessBoard.BOARD_WIDTH):
                piece = board[i, j]
                if piece != '.':
                    board[i, j] = piece.swapcase()
        return board.board

    def getSymmetries(self, board, pi):
        """
        Input:
            board: current board
            pi: policy vector of size self.getActionSize()

        Returns:
            symmForms: a list of [(board,pi)] where each tuple is a symmetrical
                       form of the board and the corresponding pi vector. This
                       is used when training the neural network from examples.
        """
        # For Chinese Chess, symmetry might be more complex due to the board's layout
        # For simplicity, we return the original board and pi
        assert board.shape == (ChineseChessBoard.BOARD_HEIGHT*ChineseChessBoard.BOARD_WIDTH+2,)
        board = ChineseChessBoard(board)
        board_np = board.fen_to_planes()
        # return [(board_np, pi)]
        def rotate_180(board):
            height = board.BOARD_HEIGHT
            width = board.BOARD_WIDTH
            board_rotate180 = ChineseChessBoard()
            for i in range(height):
                for j in range(width):
                    board_rotate180[height - 1 - i, width - 1 - j] = board[i, j]
            return ChineseChessBoard(board_rotate180.board)
        board_rotate180 = rotate_180(board)
        board_rotate180_np = board_rotate180.fen_to_planes()
        # board 镜像 move 的 delta[0] * -1 进行转换
        def mirror(matrix):
            height = board.BOARD_HEIGHT
            width = board.BOARD_WIDTH
            mirrored = ChineseChessBoard()
            for i in range(height):
                for j in range(width):
                    mirrored[height - 1 - i, j] = matrix[i, j]
            return ChineseChessBoard(mirrored.board)
        board_mirror = mirror(board)
        board_mirror_np = board_mirror.fen_to_planes()
        height = board.BOARD_HEIGHT
        width = board.BOARD_WIDTH
        pi_rotate180 = [0 for _ in range(len(pi))]
        pi_mirror = [0 for _ in range(len(pi))]
        # board.print_board()
        # board_rotate180.print_board()
        # board_mirror.print_board()
        for a, p in enumerate(pi):
            if p == 0:
                continue
            m = board.action_to_move(a)
            d1 = (-1*(m[2] - m[0]), -1*(m[3] - m[1]))
            m1 = (width - 1 - m[0], height - 1 - m[1])
            m1 = (m1[0], m1[1], m1[0]+d1[0], m1[1]+d1[1])
            # print(f"{m} -> {m1}")
            a1 = board_rotate180.move_to_action(*m1)
            assert a1 in board_rotate180._black_legal_actions or a1 in board_rotate180._red_legal_actions
            pi_rotate180[a1] = pi[a]
            d2 = ((m[2] - m[0]), -1*(m[3] - m[1]))
            m2 = (m[0], height - 1 - m[1])
            m2 = (m2[0], m2[1], m2[0]+d2[0], m2[1]+d2[1])
            # print(f"{m} -> {m2}")
            a2 = board_mirror.move_to_action(*m2)
            assert a2 in board_mirror._black_legal_actions or a2 in board_mirror._red_legal_actions
            pi_mirror[a2] = pi[a]
        return [(board_np, pi), (board_rotate180_np, pi_rotate180), (board_mirror_np, pi_mirror)]

    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        board = ChineseChessBoard(board)
        return board.to_fen()

    @staticmethod
    def display(board):
        board = ChineseChessBoard(board)
        board.print_board()
    
    @staticmethod
    def convert_predict_board(board):
        board = ChineseChessBoard(board)
        return board.fen_to_planes()
    
    @staticmethod
    def move_to_action(board, x1, y1, x2, y2):
        board = ChineseChessBoard(board)
        return board.move_to_action(x1, y1, x2, y2)
    
    @staticmethod
    def action_to_move(board, action):
        board = ChineseChessBoard(board)
        return board.action_to_move(action)
    
if __name__ == "__main__":
    board = [
        ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', 'C', '.', '.', '.', '.', '.', 'C', '.'],
        ['P', '.', 'P', '.', 'P', '.', 'P', '.', 'P'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['p', '.', 'p', '.', 'p', '.', 'p', '.', 'p'],
        ['.', 'c', '.', '.', '.', '.', '.', 'c', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r']
    ]
    board = ChineseChessBoard(ChineseChessBoard.get_board_array(board))
    board.print_board()
    print(board.to_fen())
    print(sorted(list(board.action_to_move(a) for a in board.get_legal_actions(ChineseChessBoard.RED))))
    print(sorted(list(board.action_to_move(a) for a in board.get_legal_actions(ChineseChessBoard.BLACK))))
