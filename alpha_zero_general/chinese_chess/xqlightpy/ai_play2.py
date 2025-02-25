# -*- coding: utf-8 -*-

from chinese_chess.xqlightpy.position import Position, SRC, DST
from chinese_chess.xqlightpy.search import Search
from chinese_chess.xqlightpy.cchess import move2Iccs,Iccs2move
import numpy as np

def move2pos(move):
    sqSrc = SRC(move)
    sqDst = DST(move)
    # print(f"sqSrc={sqSrc}, sqDst={sqDst}")
    # 将字节转换为具体的坐标值
    x1 = sqSrc % 16 - 3
    y1 = sqSrc // 16 - 3
    x2 = sqDst % 16 - 3
    y2 = sqDst // 16 - 3
    # print(f"x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    return str(x1) + str(y1) + str(x2) + str(y2)

def predict_best_move_and_score(fen):
    pos = Position()
    pos.fromFen(fen)
    searcher = Search(pos, 16)
    mov = searcher.searchMain(3, 500)
    return move2pos(mov)

# 示例用法
if __name__ == "__main__":
    board = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w"
    player = 1
    for i in range(10):
        move = predict_best_move_and_score(board)
        pos = Position()
        pos.fromFen(board)
        pos.makeMove(move)
        board = pos.toFen()
        print(f"player={player}, move={move}, after={board}")
        player *= -1
