import time
import random
import numpy as np

class TestChineseChessPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        # input("按回车继续")
        a = self.game.getSearchAIAction(board, need_random=True)
        valids = self.game.getValidMoves(board, 1)
        if valids[a] == 0:
            self.game.display(board)
            move = self.game.action_to_move(board, a)
            x1, y1, x2, y2 = int(move[0]), int(move[1]), int(move[2]), int(move[3])
            print(f"ai play {a} {x1},{y1} -> {x2},{y2}")
            assert valids[a] > 0
        return a

class HumanChineseChessPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valids = self.game.getValidMoves(board, 1)
        actions = []
        for i in range(len(valids)):
            if valids[i]:
                actions.append(i)
        action = random.choice(actions)
        return action
