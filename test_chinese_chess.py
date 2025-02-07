from alpha_zero_general import Arena
from alpha_zero_general.chinese_chess.ChineseChessGame import ChineseChessGame
from alpha_zero_general.chinese_chess.ChineseChessPlayers import *

g = ChineseChessGame()

# hp1 = HumanChineseChessPlayer(g).play
# hp2 = HumanChineseChessPlayer(g).play

hp1 = TestChineseChessPlayer(g).play
hp2 = TestChineseChessPlayer(g, -1).play

arena = Arena.Arena(hp1, hp2, g, display=ChineseChessGame.display)

print(arena.playGames(2, verbose=True))
