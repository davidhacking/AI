import Arena
from chinese_chess.ChineseChessGame import ChineseChessGame
from chinese_chess.ChineseChessPlayers import *

g = ChineseChessGame()

hp1 = HumanChineseChessPlayer(g).play
hp2 = HumanChineseChessPlayer(g).play

hp1 = TestChineseChessPlayer(g).play
hp2 = TestChineseChessPlayer(g).play

arena = Arena.Arena(hp1, hp2, g, display=ChineseChessGame.display)

print(arena.playGames(200, verbose=True))
