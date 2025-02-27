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
        self.piece_num, self.board_x, self.board_y = game.getBoardSize()  # 修改为14,10,9
        self.action_size = game.getActionSize()
        self.args = args

        super(ChineseChessNNet, self).__init__()

        # 输入通道数改为piece_num(14)
        self.conv1 = nn.Conv2d(self.piece_num, args.num_channels, 3, stride=1, padding=1)  # 关键修改
        self.conv2 = nn.Conv2d(args.num_channels, args.num_channels, 3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(args.num_channels, args.num_channels, 3, stride=1)
        self.conv4 = nn.Conv2d(args.num_channels, args.num_channels, 3, stride=1)

        self.bn1 = nn.BatchNorm2d(args.num_channels)
        self.bn2 = nn.BatchNorm2d(args.num_channels)
        self.bn3 = nn.BatchNorm2d(args.num_channels)
        self.bn4 = nn.BatchNorm2d(args.num_channels)

        # 计算全连接层输入维度 (10-4)*(9-4)=6 * 5=30
        fc_input_dim = args.num_channels * (self.board_x-4) * (self.board_y-4)
        self.fc1 = nn.Linear(fc_input_dim, 1024)
        self.fc_bn1 = nn.BatchNorm1d(1024)

        self.fc2 = nn.Linear(1024, 512)
        self.fc_bn2 = nn.BatchNorm1d(512)

        self.fc3 = nn.Linear(512, self.action_size)
        self.fc4 = nn.Linear(512, 1)

    def forward(self, s):
        # 输入reshape修改为 (batch, 14, 10, 9)
        s = s.view(-1, self.piece_num, self.board_x, self.board_y)  # 关键修改
        
        # 卷积层维度变化：
        # conv1: [B,14,10,9] -> [B,ch,10,9] (padding=1保持尺寸)
        # conv2: [B,ch,10,9] -> [B,ch,10,9]
        # conv3: [B,ch,10,9] -> [B,ch,8,7] (无padding，尺寸-2)
        # conv4: [B,ch,8,7] -> [B,ch,6,5] (无padding，尺寸-2)
        s = F.relu(self.bn1(self.conv1(s)))
        s = F.relu(self.bn2(self.conv2(s)))
        s = F.relu(self.bn3(self.conv3(s)))
        s = F.relu(self.bn4(self.conv4(s)))
        
        # 展平后维度：ch * 6 * 5
        s = s.view(-1, self.args.num_channels * (self.board_x-4) * (self.board_y-4))

        s = F.dropout(F.relu(self.fc_bn1(self.fc1(s))), p=self.args.dropout, training=self.training)
        s = F.dropout(F.relu(self.fc_bn2(self.fc2(s))), p=self.args.dropout, training=self.training)

        pi = self.fc3(s)
        v = self.fc4(s)

        return F.log_softmax(pi, dim=1), torch.tanh(v)


class AlphaZeroNet(nn.Module):
    def __init__(self, input_channels=14, res_layers=10, filters=256, policy_shape=608):
        super().__init__()
        # 初始卷积层
        self.conv = nn.Sequential(
            nn.Conv2d(input_channels, filters, 3, padding=1, bias=False),
            nn.BatchNorm2d(filters),
            nn.ReLU(inplace=True)
        )
        
        # 残差块
        self.res_blocks = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(filters, filters, 3, padding=1, bias=False),
                nn.BatchNorm2d(filters),
                nn.ReLU(inplace=True),
                nn.Conv2d(filters, filters, 3, padding=1, bias=False),
                nn.BatchNorm2d(filters)
            ) for _ in range(res_layers)
        ])
        
        # 策略头
        self.policy_head = nn.Sequential(
            nn.Conv2d(filters, 4, 1, bias=False),
            nn.BatchNorm2d(4),
            nn.ReLU(inplace=True),
            nn.Flatten(),
            nn.Linear(4*10*9, policy_shape)
        )
        
        # 价值头
        self.value_head = nn.Sequential(
            nn.Conv2d(filters, 2, 1, bias=False),
            nn.BatchNorm2d(2),
            nn.ReLU(inplace=True),
            nn.Flatten(),
            nn.Linear(2*10*9, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 1),
            nn.Tanh()
        )
        # for m in self.modules():
        #     if isinstance(m, nn.Conv2d):
        #         nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')

    def forward(self, x):
        x = self.conv(x)
        for block in self.res_blocks:
            residual = x
            x = block(x)
            x += residual
            x = F.relu(x)
        
        policy = self.policy_head(x)
        value = self.value_head(x)
        return policy, value

