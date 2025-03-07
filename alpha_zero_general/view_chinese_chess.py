import Arena
from chinese_chess.ChineseChessGame import ChineseChessGame, ChineseChessBoard
from chinese_chess.pytorch.NNet import NNetWrapper as NNet
from MCTS2 import MCTS
from utils import *
import numpy as np

g = ChineseChessGame()

class NNetPlayer():
    def __init__(self, game, model_path, model_file):
        self.game = game
        n1 = NNet(game)
        if model_file:
            n1.load_checkpoint(model_path, model_file)
        args1 = dotdict({'numMCTSSims': 1000, 'cpuct':1.5, 'max_mcts_depth': 500})
        self.mcts = MCTS(game, n1, args1)

    def play(self, board):
        # input("press enter to play")
        actions = self.mcts.getActionProb(board, temp=0)
        a = np.argmax(actions)
        move = self.game.action_to_move(board, a)
        x1, y1, x2, y2 = int(move[0]), int(move[1]), int(move[2]), int(move[3])
        print(f"action={a}, move={x1},{y1} -> {x2},{y2}")
        return a

player1 = NNetPlayer(g, './chinese_chess_models', 'temp.pth.tar').play
player2 = NNetPlayer(g, './chinese_chess_models', 'temp.pth.tar').play


arena = Arena.Arena(player1, player2, g, display=ChineseChessGame.display)

print(arena.playGames(2, verbose=True))
