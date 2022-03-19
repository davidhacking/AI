import ai
import alpha_beta_ai
import min_max_ai


class RushReportNumNode(ai.BaseNode):
    def __init__(self, paces=None, steps=(1, 2, 3), total=6):
        super().__init__(paces)
        self.cur_sum = 0
        for p in paces:
            self.cur_sum += p.strategy
        self.steps = steps
        self.max_step = max(*steps)
        self.min_step = min(*steps)
        self.total = total

    def end(self):
        return self.cur_sum >= self.total

    def play(self, pace):
        super().play(pace)
        self.cur_sum += pace.strategy

    def next_all_nodes(self, maximizing_player):
        player = ai.player_type_player if maximizing_player else ai.player_type_ai
        nodes = []
        for s in self.steps:
            paces = ai.copy_pace(self._paces)
            node = RushReportNumNode(paces=paces, steps=self.steps, total=self.total)
            node.play(ai.Pace(player, s))
            nodes.append(node)
        return nodes

    # 评估玩家的收益
    def evaluate(self):
        cur_player = self.last_pace().player
        delta = self.total - self.cur_sum
        score = 0
        if delta <= 0:
            score = ai.max_value
        elif 0 < delta <= self.max_step:
            score = ai.min_value
        if cur_player == ai.player_type_player:
            return score
        return -score


def test_players():
    rrn = RushReportNumNode(paces=[], total=8)
    while not rrn.end():
        ai1 = alpha_beta_ai.AlphaBetaAI()
        # ai1 = min_max_ai.MinMaxAI()
        choice = ai1.next_pace(rrn, depth=10)
        if choice is None:
            return
        print("ai1 choice={}".format(choice))
        rrn.play(choice.pace)
        if rrn.end():
            print("ai1 win")
            return
        ai2 = alpha_beta_ai.AlphaBetaAI()
        choice = ai2.next_pace(rrn, depth=10, maximizing_player=False)
        if choice is None:
            return
        print("ai2 choice={}".format(choice))
        rrn.play(choice.pace)
        if rrn.end():
            print("ai2 win")
            return


def test_play2_report_3():
    rrn = RushReportNumNode(paces=[
        ai.Pace(ai.player_type_ai, 1),
        ai.Pace(ai.player_type_player, 1),
        ai.Pace(ai.player_type_ai, 1),
    ])
    a = min_max_ai.MinMaxAI()
    choice = a.next_pace(rrn)
    print(choice, choice.pace.strategy == 3)


class WinnerRes:
    def __init__(self, player, first_num):
        self.player = player
        self.first_num = first_num


# 玩家1、2轮流从steps里报数，sum为两人报数的和，谁先报数到>=total，谁获胜，玩家1先报
# 输出必胜的玩家，1或2，输出必胜玩家第一次报数是多少
class SolveRushReportNum:
    def __init__(self, steps=(1, 2, 3), total=6):
        self.steps = steps
        self.total = total

    # 记录1-n的所有状态
    def solve(self):
        max_step = max(*self.steps)


if __name__ == '__main__':
    test_play2_report_3()
    test_players()
