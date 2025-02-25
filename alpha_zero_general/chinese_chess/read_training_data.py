from pickle import Pickler, Unpickler
import numpy as np
from ChineseChessGame import ChineseChessBoard, ChineseChessGame

if __name__ == '__main__':
    with open(r'/workspace/alpha_zero/chinese_chess_models/checkpoint_0.pth.tar.examples', "rb") as f:
        trainExamplesHistory = Unpickler(f).load()
        for examples in trainExamplesHistory:
            for index, item in enumerate(examples):
                b, p, r = item
                is_all_zero = np.all(b == 0, axis=0)
                b = np.where(is_all_zero, -1, np.argmax(b, axis=0))
                board = ChineseChessBoard()
                for i in range(10):
                    for j in range(9):
                        board[i, j] = '.' if b[i][j] == -1 else ChineseChessBoard.Idx_2_Fen[b[i][j]]
                board = ChineseChessBoard(board.board)
                print("==============================")
                print(f"index={index}, r={r}")
                board.print_board()
                k = 0
                for i, pi in enumerate(p):
                    if pi == 0:
                        continue
                    k += 1
                    m = board.action_to_move(i)
                    print(f"{k}. {i+1} {m}: {pi}")
                input("enter...")
