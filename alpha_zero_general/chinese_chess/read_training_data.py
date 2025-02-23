from pickle import Pickler, Unpickler
import numpy as np
from ChineseChessGame import ChineseChessBoard, ChineseChessGame

if __name__ == '__main__':
    with open(r'.examples', "rb") as f:
        trainExamplesHistory = Unpickler(f).load()
        for item in trainExamplesHistory:
            b, p, r = item
            is_all_zero = np.all(b == 0, axis=0)
            b = np.where(is_all_zero, -1, np.argmax(b, axis=0))
            board = ChineseChessBoard()
            for i in range(10):
                for j in range(9):
                    board[j, i] = '.' if b[i][j] == -1 else ChineseChessBoard.Idx_2_Fen[b[i][j]]
            board.print_board()
            print(r"p={p}, r={r}")
            print("==============================")