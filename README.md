# 博弈AI
- 博弈：两个人的游戏，每个人都会做出基于当前状态最有利于自己的决定

## MinMax算法
- 一句话说清楚：将两位玩家的博弈过程看成一棵树，单双层分别代表一个玩家的行动，例如Play是单层。评估当前玩家的下一步哪里是最优的方法是通过搜索，
对于玩家决策时选择的节点应该是评分最高的，对于对手决策时选择的节点应该是评分最低的，因为这个评分是给你的

## 模块
- ai, 提供alpha beta剪枝 min max等搜索算法

## 中国象棋AI

### 当前状态
- 能够搜索4层500ms左右能返回，即两个回合

### TODO
- 如何在耗时不变的条件下搜索更多的层数？
- 加入棋谱搜索
- 修改Player 和 AI的称呼