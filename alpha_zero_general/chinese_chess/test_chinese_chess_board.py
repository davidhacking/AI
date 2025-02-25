import unittest
from ChineseChessGame import ChineseChessBoard

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


if __name__ == '__main__':
    unittest.main()