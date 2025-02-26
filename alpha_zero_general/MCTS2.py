import logging
import math

import numpy as np

EPS = 1e-8

log = logging.getLogger(__name__)

class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores game.getGameEnded ended for board s
        self.Vs = {}  # stores game.getValidMoves for board s

    def getActionProb(self, canonicalBoard, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        for i in range(self.args.numMCTSSims):
            self.search(canonicalBoard)

        s = self.game.stringRepresentation(canonicalBoard)
        counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(self.game.getActionSize())]

        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs

        counts = [x ** (1. / temp) for x in counts]
        counts_sum = float(sum(counts))
        probs = [x / counts_sum for x in counts]
        return probs

    def search(self, canonicalBoard):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propagated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propagated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """
        
        path = []
        current_state = canonicalBoard.copy()  # 确保不修改原始状态
        while True:
            s = self.game.stringRepresentation(current_state)
            
            # 检查是否终止状态
            if s not in self.Es:
                self.Es[s] = self.game.getGameEnded(current_state, 1)
            if self.Es[s] != 0:
                v = -self.Es[s]
                break
            
            # 检查是否叶子节点
            if s not in self.Ps:
                # 展开叶子节点
                self.Ps[s], v_nn = self.nnet.predict(current_state)
                valids = self.game.getValidMoves(current_state, 1)
                self.Ps[s] = self.Ps[s] * valids  # 应用有效动作掩码
                sum_Ps = np.sum(self.Ps[s])
                if sum_Ps > 0:
                    self.Ps[s] /= sum_Ps  # 重新归一化
                else:
                    # 处理所有有效动作被掩码的情况
                    log.error("All valid moves were masked, doing a workaround.")
                    self.Ps[s] = self.Ps[s] + valids
                    self.Ps[s] /= np.sum(self.Ps[s])
                self.Vs[s] = valids
                self.Ns[s] = 0
                v = -v_nn  # 与递归版本返回 -v 一致
                break
            
            # 选择动作
            valids = self.Vs[s]
            cur_best = -float('inf')
            best_act = -1
            
            # 计算所有动作的UCT值
            for a in range(self.game.getActionSize()):
                if valids[a]:
                    if (s, a) in self.Qsa:
                        u = self.Qsa[(s, a)] + self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (1 + self.Nsa[(s, a)])
                    else:
                        u = self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)
                    
                    if u > cur_best:
                        cur_best = u
                        best_act = a
            if best_act == -1:
                print(f"best_act=-1")
                continue
            
            a = best_act
            path.append((s, a))  # 记录路径
            
            # 转换到下一状态
            next_state, next_player = self.game.getNextState(current_state, 1, a)
            current_state = self.game.getCanonicalForm(next_state, next_player)
        
        # 反向传播更新统计信息
        for (s, a) in reversed(path):
            if (s, a) in self.Qsa:
                self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
                self.Nsa[(s, a)] += 1
            else:
                self.Qsa[(s, a)] = v
                self.Nsa[(s, a)] = 1
            
            self.Ns[s] += 1
            v = -v  # 重要：反向传播时需要取反
        
        return v  # 返回值虽不被外部使用，但保持接口一致