import unittest
import random
import numpy as np
from ChineseChessGame import ChineseChessBoard, ChineseChessGame

class TestChineseChessBoard(unittest.TestCase):
    def setUp(self):
        pass

    def test_red_king_legal_moves(self):
        # Test legal moves for the red king
        board = [
            ['.', '.', '.', '.', 'K', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'k', '.', '.', '.', '.']
        ]
        board = ChineseChessBoard(ChineseChessBoard.get_board_array((board)))
        legal_moves = board.get_legal_actions(ChineseChessBoard.RED)
        self.assertEqual(4, legal_moves.__len__())
        self.assertIn(board.move_to_action(4, 9, 3, 9), legal_moves)
        self.assertIn(board.move_to_action(4, 9, 5, 9), legal_moves)
        self.assertIn(board.move_to_action(4, 9, 4, 8), legal_moves)
        self.assertIn(board.move_to_action(4, 9, 4, 0), legal_moves)

    def test_black_king_legal_moves(self):
        # Test legal moves for the black king
        board = [
            ['.', '.', '.', '.', 'K', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'k', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.']
        ]
        board = ChineseChessBoard(ChineseChessBoard.get_board_array(board))
        legal_moves = board.get_legal_actions(ChineseChessBoard.BLACK)
        self.assertEqual(4, len(legal_moves))
        self.assertIn(board.move_to_action(4, 0, 3, 0), legal_moves)
        self.assertIn(board.move_to_action(4, 0, 5, 0), legal_moves)
        self.assertIn(board.move_to_action(4, 0, 4, 1), legal_moves)
        self.assertIn(board.move_to_action(4, 0, 4, 8), legal_moves)

    def test_red_king_blocked_moves(self):
        # Test red king moves when blocked by other pieces
        board = [
            ['.', '.', '.', '.', 'K', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'a', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'k', '.', '.', '.', '.']
        ]
        board = ChineseChessBoard(ChineseChessBoard.get_board_array(board))
        legal_moves = board.get_legal_actions(ChineseChessBoard.RED)
        self.assertEqual(6, len(legal_moves))
        self.assertIn(board.move_to_action(4, 8, 3, 7), legal_moves)
        self.assertIn(board.move_to_action(4, 8, 5, 7), legal_moves)
        self.assertIn(board.move_to_action(4, 8, 3, 9), legal_moves)
        self.assertIn(board.move_to_action(4, 8, 5, 9), legal_moves)
        self.assertIn(board.move_to_action(4, 9, 3, 9), legal_moves)
        self.assertIn(board.move_to_action(4, 9, 5, 9), legal_moves)

    def test_black_king_blocked_moves(self):
        # Test black king moves when blocked by other pieces
        board = [
            ['.', '.', '.', '.', 'K', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'A', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'a', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'k', '.', '.', '.', '.']
        ]
        board = ChineseChessBoard(ChineseChessBoard.get_board_array(board))
        legal_moves = board.get_legal_actions(ChineseChessBoard.BLACK)
        self.assertEqual(6, len(legal_moves))
        self.assertIn(board.move_to_action(4, 1, 3, 0), legal_moves)
        self.assertIn(board.move_to_action(4, 1, 5, 0), legal_moves)
        self.assertIn(board.move_to_action(4, 1, 3, 2), legal_moves)
        self.assertIn(board.move_to_action(4, 1, 5, 2), legal_moves)
        self.assertIn(board.move_to_action(4, 0, 3, 0), legal_moves)
        self.assertIn(board.move_to_action(4, 0, 5, 0), legal_moves)
    
    def test_p(self):
        data = """
0 . . . . . . . . . 
1 . . . P a . . . . 
2 . . . P b k . . . 
3 . N . . . N . . . 
4 . . b . . C . . . 
5 . . . . . . . . . 
6 . . . . . . . . . 
7 . . . . B . . . . 
8 . . n C A . . . . 
9 . . . . K A B . . 
"""
        lines = data.strip().split('\n')
        board = []
        for line in lines:
            row = line[2:].split()
            board.append(row)
        board = ChineseChessBoard(ChineseChessBoard.get_board_array(board))
        legal_moves = board.get_legal_actions(ChineseChessBoard.BLACK)
        self.assertIn(board.move_to_action(3, 1, 3, 0), legal_moves)
    
    def test_action(self):
        rboard = ChineseChessBoard()
        g = ChineseChessGame()
        bboard = ChineseChessBoard(g.getCanonicalForm(rboard.board, -1))
        rlegal_moves = rboard.get_legal_actions(ChineseChessBoard.RED)
        a = random.choice(list(rlegal_moves))
        rboard.takeAction(a, ChineseChessBoard.RED)
        bboard.takeAction(a, ChineseChessBoard.BLACK)
        bboard = ChineseChessBoard(g.getCanonicalForm(bboard.board, -1))
        self.assertEqual(rboard.to_fen(), bboard.to_fen())

    def test_action2(self):
        bboard = ChineseChessBoard()
        g = ChineseChessGame()
        rboard = ChineseChessBoard(g.getCanonicalForm(bboard.board, -1))
        blegal_moves = bboard.get_legal_actions(ChineseChessBoard.BLACK)
        a = random.choice(list(blegal_moves))
        bboard.takeAction(a, ChineseChessBoard.BLACK)
        rboard.takeAction(a, ChineseChessBoard.RED)
        rboard = ChineseChessBoard(g.getCanonicalForm(rboard.board, -1))
        self.assertEqual(rboard.to_fen(), bboard.to_fen())
    
    def test_planes(self):
        board = ChineseChessBoard()
        b = board.fen_to_planes()
        board2 = ChineseChessBoard.from_planes(b)
        b2 = board2.fen_to_planes()
        self.assertEqual(True, np.array_equal(b, b2))



if __name__ == '__main__':
    unittest.main()