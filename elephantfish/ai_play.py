# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import time
from elephantfish.elephantfish import Position, Searcher, initial, parse, render

MY_THINK_TIME = 5


def get_best_move_and_score(board, move_str):
    # 初始化历史记录列表
    hist = [Position(board, 0)]
    searcher = Searcher()

    # 解析用户输入的行动指令
    match = re.match('([a-i][0-9])'*2, move_str)
    if match:
        print("g1={}".format(match.group(1)))
        print("g2={}".format(match.group(2)))
        move = parse(match.group(1)), parse(match.group(2))
    else:
        raise ValueError("Invalid move format. Please enter a move like b9c7.")

    # 检查行动是否合法
    valid_moves = list(hist[-1].gen_moves())
    print("move_str={}".format(move))
    print("valid_moves={}".format(
        [render(m[0])+render(m[1]) for m in valid_moves]))
    if move not in hist[-1].gen_moves():
        raise ValueError("Invalid move.")

    # 执行用户的行动
    hist.append(hist[-1].move(move))

    # 旋转棋盘以获取对方视角
    rotated_position = hist[-1].rotate()

    # 启动引擎寻找最佳行动
    start = time.time()
    best_move = None
    best_score = None
    for _depth, move, score in searcher.search(rotated_position, hist):
        if time.time() - start > MY_THINK_TIME:
            break
        best_move = move
        best_score = score

    # 反向旋转行动以便正确显示
    best_move_str = render(
        255 - best_move[0] - 1) + render(255 - best_move[1] - 1)

    # 获取红黑双方的打分
    red_score = hist[-1].score
    black_score = rotated_position.score

    return best_move_str, red_score, black_score


def move_in_board(board, move):
    i, j = move
    p, q = board[i], board[j]
    def put(board, i, p): return board[:i] + p + board[i+1:]
    # Copy variables and reset ep and kp
    new_board = board
    # Actual move
    new_board = put(new_board, j, board[i])
    new_board = put(new_board, i, '.')
    return new_board


def move2pos(move):
    x1 = ord(move[0]) - ord('a')
    y1 = 9 - int(move[1])
    x2 = ord(move[2]) - ord('a')
    y2 = 9 - int(move[3])
    return str(x1) + str(y1) + str(x2) + str(y2)


def predict_best_move_and_score(board, my=1):
    pos = Position(board, 0)
    if my == -1:
        pos = pos.rotate()
    searcher = Searcher()
    start = time.time()
    best_move = None
    best_score = None
    for _depth, move, score in searcher.search(pos):
        if time.time() - start > MY_THINK_TIME:
            break
        best_move = move
        best_score = score
    return best_move, best_score


# 示例用法
if __name__ == "__main__":
    my = 1
    board = initial
    for i in range(10):
        move, score = predict_best_move_and_score(board, my)
        if my == -1:
            move = 255 - move[0] - 1, 255 - move[1] - 1
        render_move = render(move[0]) + render(move[1])
        print("my={}, move={}, move2pos={}, score={}".format(
            my, render_move, move2pos(render_move), score))
        board = move_in_board(board, move)
        my *= -1
