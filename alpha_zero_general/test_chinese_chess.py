import Arena
from chinese_chess.ChineseChessGame import ChineseChessGame
from chinese_chess.pytorch.NNet import NNetWrapper as NNet
from MCTS2 import MCTS
from utils import *
import numpy as np

g = ChineseChessGame()

# nnet players
n1 = NNet(g)
n1.load_checkpoint('./chinese_chess_models','best.pth.tar')
args1 = dotdict({'numMCTSSims': 50, 'cpuct':1.0})
mcts1 = MCTS(g, n1, args1)
player1 = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

n2 = NNet(g)
n2.load_checkpoint('./chinese_chess_models', 'best.pth.tar')
args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
mcts2 = MCTS(g, n2, args2)
player2 = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))


arena = Arena.Arena(player1, player2, g, display=ChineseChessGame.display, need_reverse_play=False)

print(arena.playGames(2, verbose=True))
