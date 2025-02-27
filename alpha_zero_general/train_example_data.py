from pickle import Pickler, Unpickler
import numpy as np
from chinese_chess.ChineseChessGame import ChineseChessBoard, ChineseChessGame
from chinese_chess.pytorch.NNet import AlphaZeroWrapper

if __name__ == '__main__':
    with open(r'/workspace/alpha_zero/chinese_chess_models/checkpoint_3.pth.tar.examples', "rb") as f:
        trainExamplesHistory = Unpickler(f).load()
        trainExamples = []
        for examples in trainExamplesHistory:
            trainExamples.extend(examples)
        game = ChineseChessGame()
        net = AlphaZeroWrapper(game)
        net.train(trainExamples)
        net.save_checkpoint('/workspace/alpha_zero/chinese_chess_models/', 'checkpoint_3.pth.tar')
