import Arena
from chinese_chess.ChineseChessGame import ChineseChessGame
from chinese_chess.ChineseChessPlayers import *
from utils import *
from chinese_chess.pytorch.NNet import NNetWrapper as nn
from MCTS import MCTS

g = ChineseChessGame()

hp1 = HumanChineseChessPlayer(g).play
hp2 = TestChineseChessPlayer(g).play

class ModelPlayer():
    def __init__(self, game):
        self.game = game
        n1 = nn(game)
        # n1.load_checkpoint('./temp','best.pth.tar')
        args1 = dotdict({'numMCTSSims': 50, 'cpuct':1.0})
        self.mcts = MCTS(game, n1, args1)

    def play(self, board):
        actions = self.mcts.getActionProb(board, temp=0)
        a = np.argmax(actions)
        valids = self.game.getValidMoves(board, 1)
        if valids[a] == 0:
            self.game.display(board)
            move = self.game.action_to_move(board, a)
            x1, y1, x2, y2 = int(move[0]), int(move[1]), int(move[2]), int(move[3])
            print(f"ai play {a} {x1},{y1} -> {x2},{y2}")
            assert valids[a] > 0
        return a

hp1 = HumanChineseChessPlayer(g).play
hp2 = ModelPlayer(g).play

arena = Arena.Arena(hp1, hp2, g, display=ChineseChessGame.display)

print(arena.playGames(20, verbose=False))
