import os
import sys
import time

import numpy as np
from tqdm import tqdm
import multiprocessing as mp

sys.path.append('../../')
from utils import *
from NeuralNet import NeuralNet

import torch
import torch.optim as optim
import torch.nn as nn

try:
    from .ChineseChessNNet import CChessModel as ccnet
except ImportError:
    from ChineseChessNNet import CChessModel as ccnet

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': torch.cuda.is_available(),
    'num_channels': 512,
})


class NNetWrapper(NeuralNet):
    _lock = mp.Lock()
    def __init__(self, game):
        self.nnet = ccnet(game, args)
        self.game = game
        self.piece_num, self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        if args.cuda:
            self.nnet.cuda()

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        optimizer = optim.Adam(self.nnet.parameters())

        for epoch in range(args.epochs):
            print('EPOCH ::: ' + str(epoch + 1))
            self.nnet.train()
            pi_losses = AverageMeter()
            v_losses = AverageMeter()

            batch_count = int(len(examples) / args.batch_size)

            t = tqdm(range(batch_count), desc='Training Net')
            for _ in t:
                sample_ids = np.random.randint(len(examples), size=args.batch_size)
                boards, pis, vs = list(zip(*[examples[i] for i in sample_ids]))
                boards = torch.FloatTensor(np.array(boards).astype(np.float64))
                target_pis = torch.FloatTensor(np.array(pis))
                target_vs = torch.FloatTensor(np.array(vs).astype(np.float64))

                # predict
                if args.cuda:
                    boards, target_pis, target_vs = boards.contiguous().cuda(), target_pis.contiguous().cuda(), target_vs.contiguous().cuda()

                # compute output
                out_pi, out_v = self.nnet(boards)
                l_pi = self.loss_pi(target_pis, out_pi)
                l_v = self.loss_v(target_vs, out_v)
                total_loss = l_pi + l_v

                # record loss
                pi_losses.update(l_pi.item(), boards.size(0))
                v_losses.update(l_v.item(), boards.size(0))
                t.set_postfix(Loss_pi=pi_losses, Loss_v=v_losses)

                # compute gradient and do SGD step
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()

    def predict(self, board):
        """
        board: np array with board
        """
        with self._lock:
            board = self.game.convert_predict_board(board)
            # timing
            start = time.time()

            # preparing input
            board = torch.FloatTensor(board.astype(np.float64))
            if args.cuda: board = board.contiguous().cuda()
            board = board.view(1, self.piece_num, self.board_x, self.board_y)
            self.nnet.eval()
            with torch.no_grad():
                pi, v = self.nnet(board)

            # print('PREDICTION TIME TAKEN : {0:03f}'.format(time.time()-start))
            return torch.exp(pi).data.cpu().numpy()[0], v.data.cpu().numpy()[0]

    def loss_pi(self, targets, outputs):
        return -torch.sum(targets * outputs) / targets.size()[0]

    def loss_v(self, targets, outputs):
        return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size()[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        torch.save({
            'state_dict': self.nnet.state_dict(),
        }, filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise ("No model in path {}".format(filepath))
        map_location = None if args.cuda else 'cpu'
        checkpoint = torch.load(filepath, map_location=map_location)
        self.nnet.load_state_dict(checkpoint['state_dict'])

# 添加 MockGame 类
class MockGame:
    def getBoardSize(self):
        return (14, 10, 9)

    def getActionSize(self):
        return 284

    def convert_predict_board(self, board):
        return board

# 添加测试函数
def test_train_and_predict():
    game = MockGame()
    nnet = NNetWrapper(game)
    
    # 创建一些示例数据
    examples = [
        (np.random.rand(14, 10, 9), np.random.rand(284), np.random.rand(1)) for _ in range(100)
    ]
    
    # 训练模型
    nnet.train(examples)
    
    # 创建一个示例棋盘
    board = np.random.rand(14, 10, 9)
    
    # 预测
    pi, v = nnet.predict(board)
    print(f"Predicted policy: {pi}")
    print(f"Predicted value: {v}")

# 修改 main 函数
if __name__ == '__main__':
    test_train_and_predict()