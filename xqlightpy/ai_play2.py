# -*- coding: utf-8 -*-

from xqlightpy.position import Position
from xqlightpy.search import Search
from xqlightpy.cchess import move2Iccs,Iccs2move
import numpy as np

def predict_best_move_and_score(fen):
    pos = Position()
    pos.fromFen(fen)
    searcher = Search(pos, 16)
    mov = searcher.searchMain(64, 5000)
    return mov

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
