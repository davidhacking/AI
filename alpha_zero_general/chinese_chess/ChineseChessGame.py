import numpy as np
from enum import Enum

Winner = Enum("Winner", "red black draw")
MaximumTurnsWithoutPieceCapture = 60

class ChineseChessBoard():
    RED = 1
    BLACK = -1
    INIT_BOARD = [
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
    BOARD_HEIGHT = len(INIT_BOARD)
    BOARD_WIDTH = len(INIT_BOARD[0])
    def __init__(self, board=None):
        if board is not None:
            self.board = np.copy(board)
        else:
            self.board = ChineseChessBoard.get_board_array(ChineseChessBoard.INIT_BOARD)
        self.height = ChineseChessBoard.BOARD_HEIGHT
        self.width = ChineseChessBoard.BOARD_WIDTH
        self.name2point = {}
        for i in range(self.height):
            for j in range(self.width):
                piece = self[i, j]
                if piece != '.':
                    self.name2point[piece] = (j, i)
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
                    row_str += cell[0].swapcase()
            if empty_count > 0:
                row_str += str(empty_count)
            fen_parts.append(row_str)
        fen = '/'.join(fen_parts)
        return fen

    def __getitem__(self, index):
        i, j = index
        index = i * self.width + j
        return ChineseChessBoard.num2name(self.board[index])
    
    def __setitem__(self, index, value):
        i, j = index
        index = i * self.width + j
        self.board[index] = ChineseChessBoard.action_dict[value][0]

    def get_turn_num(self):
        return self.board[self.height*self.width]
    
    def inc_turn_num(self):
        self.board[self.height*self.width] += 1
    
    def get_last_piece_capture_turn_num(self):
        return self.board[self.height*self.width+1]

    def set_last_piece_capture_turn_num(self, value):
        self.board[self.height*self.width+1] = value

    def get_winner(self, color):
        print(f"turn_num={self.get_turn_num()} last_piece_capture_turn_num={self.get_last_piece_capture_turn_num()}")
        if 'k' not in self.name2point:
            return Winner.black
        elif 'K' not in self.name2point:
            return Winner.red
        if color == ChineseChessBoard.RED and len(self._red_legal_actions) <= 0:
            return Winner.black
        if color == ChineseChessBoard.BLACK and len(self._black_legal_actions) <= 0:
            return Winner.red
        kx, ky = self.name2point['k']
        Kx, Ky = self.name2point['K']
        if kx == Kx:
            has_block = False
            i = min(Ky, ky) + 1
            while i < max(ky, Ky):
                if self[i, kx] != '.':
                    has_block = True
                    break
                i += 1
            if not has_block:
                if color == ChineseChessBoard.RED:
                    return Winner.red
                else:
                    return Winner.black
        t = self.get_turn_num() - self.get_last_piece_capture_turn_num()
        if t > MaximumTurnsWithoutPieceCapture:
            # 和棋黑胜
            return Winner.black
    def print_board(self):
        for i in range(self.height):
            row_str = f"{i:2d} "
            for j in range(self.width):
                piece = str(self[i, j])
                if len(piece) == 1:
                    row_str += f"{piece}  "
                else:
                    row_str += f"{piece} "
            print(row_str)

        col_numbers = ' ' * 3
        for j in range(self.width):
            col_numbers += f"{j:2d} "
        print(col_numbers)

    @staticmethod
    def get_board_array(ch_board):
        board = np.zeros((ChineseChessBoard.BOARD_HEIGHT, ChineseChessBoard.BOARD_WIDTH), dtype=np.float32)
        for i, row in enumerate(ch_board):
            for j, piece in enumerate(row):
                board[i, j] = ChineseChessBoard.name2num(piece)
        turn_num, last_piece_capture_turn_num = 0, 0
        extra_info = np.array([turn_num, last_piece_capture_turn_num], dtype=np.float32)
        return np.concatenate((board.flatten(), extra_info))
    
    @staticmethod
    def name2num(name):
        return ChineseChessBoard.action_dict[name][0]
    
    @staticmethod
    def num2name(num):
        return ChineseChessBoard.num_to_name[num]

    def get_legal_actions(self, color=RED):
        if self.get_legal_actions_flag:
            return self._red_legal_actions if color == ChineseChessBoard.RED else self._black_legal_actions
        self.get_legal_actions_flag = True
        self._red_legal_moves = set(self._init_legal_moves(ChineseChessBoard.RED))
        self._red_legal_actions = set([self.move_to_action(*move) for move in self._red_legal_moves])
        self._black_legal_moves = set(self._init_legal_moves(ChineseChessBoard.BLACK))
        self._black_legal_actions = set([self.move_to_action(*move) for move in self._black_legal_moves])
        return self._red_legal_actions if color == ChineseChessBoard.RED else self._black_legal_actions

    mov_dir = {
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
    stright_action_func = lambda name, action_delta, x, y:  (action_delta, y) if action_delta <= 8 else (x, action_delta - 9)
    action_func = lambda name, action_delta, x, y: (x + ChineseChessBoard.mov_dir[name[0]][action_delta][0], y + ChineseChessBoard.mov_dir[name[0]][action_delta][1])
    r_stright_action_func = lambda name, x1, y1, x2, y2: x2 if y1 == y2 else (y2 + 9)
    r_action_func = lambda name, x1, y1, x2, y2: ChineseChessBoard.mov_dir[name[0]].index((x2 - x1, y2 - y1))
    
    action_dict = {
        "r1": (0, 18, stright_action_func),
        "r2": (19, 37, stright_action_func),
        "R1": (38, 56, stright_action_func),
        "R2": (57, 75, stright_action_func),
        "c1": (76, 94, stright_action_func),
        "c2": (95, 113, stright_action_func),
        "C1": (114, 132, stright_action_func),
        "C2": (133, 151, stright_action_func),
        "n1": (152, 159, action_func),
        "n2": (160, 167, action_func),
        "N1": (168, 175, action_func),
        "N2": (176, 183, action_func),
        "b1": (184, 187, action_func),
        "b2": (188, 191, action_func),
        "B1": (192, 195, action_func),
        "B2": (196, 199, action_func),
        "a1": (200, 203, action_func),
        "a2": (204, 207, action_func),
        "A1": (208, 211, action_func),
        "A2": (212, 215, action_func),
        "p1": (216, 219, action_func),
        "p2": (220, 223, action_func),
        "p3": (224, 227, action_func),
        "p4": (228, 231, action_func),
        "p5": (232, 235, action_func),
        "P1": (236, 239, action_func),
        "P2": (240, 243, action_func),
        "P3": (244, 247, action_func),
        "P4": (248, 251, action_func),
        "P5": (252, 255, action_func),
        "k": (256, 259, action_func),
        "K": (260, 263, action_func),
        ".": (264, -1, None)
    }
    num_to_name = {v[0]: k for k, v in action_dict.items()}
    action_size = max([v[1] for _, v in action_dict.items()]) + 1
    action_num_to_name = {num: action_name for action_name, (start, end, _) in action_dict.items() for num in range(start, end + 1)}

    def move_to_action(self, x1, y1, x2, y2):
        ch = self[y1, x1]
        if ch[0] in ['r', 'R', 'c', 'C']:
            return ChineseChessBoard.action_dict[ch][0] + ChineseChessBoard.r_stright_action_func(ch, x1, y1, x2, y2)
        return ChineseChessBoard.action_dict[ch][0] + ChineseChessBoard.r_action_func(ch, x1, y1, x2, y2)
    
    def _is_same_side(self, x, y, color):
        if color == ChineseChessBoard.RED and self[y, x].islower():
            return True
        if color == ChineseChessBoard.BLACK and self[y, x].isupper():
            return True
    
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

    def _init_legal_moves(self, color): # 先判断老将的位置，如果没有老将直接返回空，按老将的位置判定小兵活动范围
        if 'k' not in self.name2point:
            return []
        if 'K' not in self.name2point:
            return []
        kx, ky = self.name2point['k']
        Kx, Ky = self.name2point['K']
        board_flag = True # 红棋位于棋盘下方
        if ky >= 0 and ky <= 2:
            board_flag = False # 红棋位于棋盘上方方
        _legal_moves = []
        for y in range(self.height):
            for x in range(self.width):
                ch = self[y, x][0]
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
                                if y > 4 and x_ != x:
                                    continue
                            else:
                                if y < 5 and x_ != x:
                                    continue
                        elif ch == 'P':  # for black pawn
                            if board_flag:
                                if y < 5 and x_ != x:
                                    continue
                            else:
                                if y > 4 and x_ != x:
                                    continue
                        elif ch == 'n' or ch == 'N' or ch == 'b' or ch == 'B': # for knight and bishop
                            if self[y+int(d[1]/2), x+int(d[0]/2)] != '.':
                                continue
                            elif ch == 'b':
                                if board_flag:
                                    if y < 5:
                                        continue
                                else:
                                    if y > 4:
                                        continue
                            elif ch == 'B':
                                if board_flag:
                                    if y > 4:
                                        continue
                                else:
                                    if y < 5:
                                        continue
                        elif ch != 'p' and ch != 'P': # for king and advisor
                            if x_ < 3 or x_ > 5:
                                continue
                            if (ch == 'k' or ch == 'a'):
                                if board_flag:
                                    if y_ < 7:
                                        continue
                                else:
                                    if y_ > 2:
                                        continue
                            if (ch == 'K' or ch == 'A'):
                                if board_flag:
                                    if y_ > 2:
                                        continue
                                else:
                                    if y_ < 7:
                                        continue
                        _legal_moves.append((x, y, x_, y_))
                        if (ch == 'k' and color == ChineseChessBoard.RED): #for King to King check
                            d, u = self._y_board_from(x, y)
                            if (u < self.height and self[u, x] == 'K'):
                                _legal_moves.append((x, y, x, u))
                        elif (ch == 'K' and color == ChineseChessBoard.BLACK):
                            d, u = self._y_board_from(x, y)
                            if (d > -1 and self[d, x] == 'k'):
                                _legal_moves.append((x, y, x, d))
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
        return _legal_moves

    def isValidAction(self, action, color):
        print(f"_red_legal_actions={sorted(list(self._red_legal_actions))}")
        print(f"_black_legal_actions={sorted(list(self._black_legal_actions))}")
        return action in self._red_legal_actions if color == ChineseChessBoard.RED else action in self._black_legal_actions
        
    def takeAction(self, action, color):
        print(f"takeAction action={action} color={color}")
        assert self.isValidAction(action, color)
        name = ChineseChessBoard.action_num_to_name[action]
        assert name in self.name2point
        x1, y1 = self.name2point[name]
        action_item = ChineseChessBoard.action_dict[name]
        x2, y2 = action_item[2](name, action-action_item[0], x1, y1)
        old_piece = self[y2, x2]
        self[y1, x1] = '.'
        self[y2, x2] = name
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
        if board is not None:
            self.board = ChineseChessBoard(board)
        else:
            self.board = ChineseChessBoard()
    
    def getInitBoard(self):
        return ChineseChessBoard().board
    
    def getBoardSize(self):
        return (self.board.width, self.board.height)

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
        print(f"getNextState player={player} action={action}")
        next_player = -player
        if player == ChineseChessBoard.RED:
            board = ChineseChessBoard(board)
            board.takeAction(action+1, player)
            next_board = board.board
            return next_board, next_player
        # 需要调整回getCanonicalForm的棋盘，将action转为p2p，再计算出新的action
        canonicalFormBoard = self.getCanonicalForm(board, player)
        canonicalFormBoard = ChineseChessBoard(canonicalFormBoard)
        canonicalFormBoard.takeAction(action+1, -player)
        next_board = self.getCanonicalForm(canonicalFormBoard.board, player)
        return next_board, next_player

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
            valid_moves[a-1] = 1
        return valid_moves

    def getGameEnded(self, board, player):
        board = ChineseChessBoard(board)
        winner = board.get_winner(player)
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
        if player == 1:
            return board

        board = ChineseChessBoard(board)
        for i in range(ChineseChessBoard.BOARD_HEIGHT):
            for j in range(ChineseChessBoard.BOARD_WIDTH):
                piece = board[i, j]
                if piece != '.':
                    board[i, j] = ChineseChessGame.invert_color(piece)
        return board.board

    @staticmethod
    def invert_color(piece):
        if piece.islower():
            return piece.upper()
        elif piece.isupper():
            return piece.lower()
        else:
            return piece

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
        assert board.shape == (ChineseChessBoard.BOARD_HEIGHT*ChineseChessBoard.BOARD_WIDTH,)
        board = board[:-2]
        board = board.reshape(ChineseChessBoard.BOARD_HEIGHT, ChineseChessBoard.BOARD_WIDTH)
        return [(board, pi)]

    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        board == board[:-2]
        return ''.join([''.join(row) for row in board])
    
    def get_elephantfish_board(self, board):
        board = ChineseChessBoard(board)
        elephantfish_board = []
        for i in range(board.height):
            row = []
            for j in range(board.width):
                piece = str(board[i, j])[0]
                piece = piece.swapcase()
                row.append(piece)
            elephantfish_board.append(row)
        return elephantfish_board

    def get_fen(self, board):
        board = ChineseChessBoard(board)
        return board.to_fen()

    @staticmethod
    def display(board):
        board = ChineseChessBoard(board)
        board.print_board()
    
    @staticmethod
    def move_to_action(board, x1, y1, x2, y2):
        board = ChineseChessBoard(board)
        return board.move_to_action(x1, y1, x2, y2)-1
    
if __name__ == "__main__":
    game = ChineseChessGame()
    board = game.getInitBoard()
    curPlayer = 1
    canonicalBoard = game.getCanonicalForm(board, curPlayer)
    game.display(canonicalBoard)
    valids = game.getValidMoves(canonicalBoard, curPlayer)