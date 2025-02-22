import sys
sys.path.append('..')
from utils import *

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class ChineseChessNNet(nn.Module):

    def __init__(self, game, args):
        # game params
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        super(ChineseChessNNet, self).__init__()

        self.conv1 = nn.Conv2d(1, args.num_channels, 3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(args.num_channels, args.num_channels, 3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(args.num_channels, args.num_channels, 3, stride=1)
        self.conv4 = nn.Conv2d(args.num_channels, args.num_channels, 3, stride=1)

        self.bn1 = nn.BatchNorm2d(args.num_channels)
        self.bn2 = nn.BatchNorm2d(args.num_channels)
        self.bn3 = nn.BatchNorm2d(args.num_channels)
        self.bn4 = nn.BatchNorm2d(args.num_channels)

        self.fc1 = nn.Linear(args.num_channels*(self.board_x-4)*(self.board_y-4), 1024)
        self.fc_bn1 = nn.BatchNorm1d(1024)

        self.fc2 = nn.Linear(1024, 512)
        self.fc_bn2 = nn.BatchNorm1d(512)

        self.fc3 = nn.Linear(512, self.action_size)

        self.fc4 = nn.Linear(512, 1)

    def forward(self, s):
        #                                                           s: batch_size x board_x x board_y
        s = s.view(-1, 1, self.board_x, self.board_y)                # batch_size x 1 x board_x x board_y
        s = F.relu(self.bn1(self.conv1(s)))                          # batch_size x num_channels x board_x x board_y
        s = F.relu(self.bn2(self.conv2(s)))                          # batch_size x num_channels x board_x x board_y
        s = F.relu(self.bn3(self.conv3(s)))                          # batch_size x num_channels x (board_x-2) x (board_y-2)
        s = F.relu(self.bn4(self.conv4(s)))                          # batch_size x num_channels x (board_x-4) x (board_y-4)
        s = s.view(-1, self.args.num_channels*(self.board_x-4)*(self.board_y-4))

        s = F.dropout(F.relu(self.fc_bn1(self.fc1(s))), p=self.args.dropout, training=self.training)  # batch_size x 1024
        s = F.dropout(F.relu(self.fc_bn2(self.fc2(s))), p=self.args.dropout, training=self.training)  # batch_size x 512

        pi = self.fc3(s)                                                                         # batch_size x action_size
        v = self.fc4(s)                                                                          # batch_size x 1

        return F.log_softmax(pi, dim=1), torch.tanh(v)

class ModelConfig:
    def __init__(self):
        self.cnn_filter_num = 192
        self.cnn_first_filter_size = 5
        self.cnn_filter_size = 3
        self.res_layer_num = 10
        self.l2_reg = 1e-4
        self.value_fc_size = 256
        self.input_depth = 14

class ResidualBlock(nn.Module):
    def __init__(self, mc):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(mc.cnn_filter_num, mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding=mc.cnn_filter_size // 2)
        self.bn1 = nn.BatchNorm2d(mc.cnn_filter_num)
        self.conv2 = nn.Conv2d(mc.cnn_filter_num, mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding=mc.cnn_filter_size // 2)
        self.bn2 = nn.BatchNorm2d(mc.cnn_filter_num)

    def forward(self, x):
        in_x = x
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = x + in_x
        x = F.relu(x)
        return x

class CChessModel(nn.Module):
    def __init__(self, game, args):
        super(CChessModel, self).__init__()
        self.piece_num, self.board_x, self.board_y = game.getBoardSize()
        self.model_config = ModelConfig()
        mc = self.model_config
        self.n_labels = game.getActionSize()
        # 输入层
        self.input_conv = nn.Conv2d(self.piece_num, mc.cnn_filter_num, kernel_size=mc.cnn_first_filter_size, padding=mc.cnn_first_filter_size // 2)
        self.input_bn = nn.BatchNorm2d(mc.cnn_filter_num)
        # 残差块
        self.residual_blocks = nn.ModuleList([self._build_residual_block(mc) for _ in range(mc.res_layer_num)])

        # 策略输出层
        self.policy_conv = nn.Conv2d(mc.cnn_filter_num, 4, kernel_size=1)
        self.policy_bn = nn.BatchNorm2d(4)
        self.policy_fc = nn.Linear(4 * self.board_y * self.board_x, self.n_labels)

        # 价值输出层
        self.value_conv = nn.Conv2d(mc.cnn_filter_num, 2, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(2)
        self.value_fc1 = nn.Linear(2 * self.board_y * self.board_x, mc.value_fc_size)
        self.value_fc2 = nn.Linear(mc.value_fc_size, 1)

    def forward(self, x):
        # 输入层
        x = self.input_conv(x)
        x = self.input_bn(x)
        x = F.relu(x)

        # 残差块
        for block in self.residual_blocks:
            x = block(x)

        res_out = x

        # 策略输出
        policy = self.policy_conv(res_out)
        policy = self.policy_bn(policy)
        policy = F.relu(policy)
        policy = policy.view(-1, 4 * self.board_y * self.board_x)
        policy = self.policy_fc(policy)
        policy = F.log_softmax(policy, dim=1)

        # 价值输出
        value = self.value_conv(res_out)
        value = self.value_bn(value)
        value = F.relu(value)
        value = value.view(-1, 2 * self.board_y * self.board_x)
        value = self.value_fc1(value)
        value = F.relu(value)
        value = self.value_fc2(value)
        value = torch.tanh(value)

        return policy, value

    def _build_residual_block(self, mc):
        return ResidualBlock(mc)