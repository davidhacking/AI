import torch
import torch.multiprocessing as mp
from functools import partial
from tqdm import tqdm
from utils import *
from MCTS2 import MCTS as MCTS2
from MCTS import MCTS as MCTS1
from chinese_chess.pytorch.NNet import NNetWrapper as NNet
from chinese_chess.ChineseChessGame import ChineseChessGame, ChineseChessBoard


if __name__ == "__main__":
    game = ChineseChessGame()
    args = dotdict({'numMCTSSims': 1000, 'cpuct':1.5})
    board = [
        ['.', '.', '.', '.', 'K', '.', '.', '.', '.'],
        ['.', '.', '.', '.', 'A', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', 'k', '.', '.', '.', 'r']
    ]
    board = ChineseChessBoard(ChineseChessBoard.get_board_array(board)).board
    n = NNet(game)
    mcts1 = MCTS1(game, n, args)
    mcts2 = MCTS2(game, n, args)
    actions1 = mcts1.getActionProb(board, temp=1)
    actions2 = mcts2.getActionProb(board, temp=1)
    board = ChineseChessBoard(board)
    for a in range(len(actions1)):
        if actions1[a] != 0 or actions2[a] != 0:
            move = board.action_to_move(a)
            print(f"action={a}, move={move}, v1={actions1[a]}, v2={actions2[a]}")

        