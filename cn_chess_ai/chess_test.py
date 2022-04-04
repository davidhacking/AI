import time

import cn_chess_ai.chess as chess
from ai import alpha_beta_ai_v2
from ai import ai

# ai_creator = min_max_ai.MinMaxAI
ai_creator = alpha_beta_ai_v2.AlphaBetaAIV2

init_chess_map_str = """
 [
     0,    1,    2,    3,    4,    5,    6,    7,    8,
 0, ["C0", 'M0', 'X0', 'S0', 'J0', 'S1', 'X1', 'M1', "C1"],
 1, [None, None, None, None, None, None, None, None, None],
 2, [None, 'P0', None, None, None, None, None, 'P1', None],
 3, ['Z0', None, 'Z1', None, 'Z2', None, 'Z3', None, 'Z4'],
 4, [None, None, None, None, None, None, None, None, None],
 5, [None, None, None, None, None, None, None, None, None],
 6, ['z0', None, 'z1', None, 'z2', None, 'z3', None, 'z4'],
 7, [None, 'p0', None, None, None, None, None, 'p1', None],
 8, [None, None, None, None, None, None, None, None, None],
 9, ["c0", 'm0', 'x0', 's0', 'j0', 's1', 'x1', 'm1', "c1"]
 ]
"""


def read_chess_map_from_str(s):
    s = s.replace(" ", "").replace("\n", "")
    chess_map = eval(s)
    chess_map = chess_map[9:]
    chess_map = [line for line in chess_map if not type(line) is int]
    pieces = []
    for i in range(0, 10):
        for j in range(0, 9):
            item = chess_map[i][j]
            if item is None:
                continue
            piece = chess.chess_pieces_dict[item].copy()
            piece._pos = chess.Position(j, i)
            pieces.append(piece)
    chess_map = chess.ChessMap(pieces)
    return chess_map


"""
[
     0,    1,    2,    3,    4,    5,    6,    7,    8,
 0, [None, None, None, None, None, None, None, None, None],
 1, [None, None, None, None, None, None, None, None, None],
 2, [None, None, None, None, None, None, None, None, None],
 3, [None, None, None, None, None, None, None, None, None],
 4, [None, None, None, None, None, None, None, None, None],
 5, [None, None, None, None, None, None, None, None, None],
 6, [None, None, None, None, None, None, None, None, None],
 7, [None, None, None, None, None, None, None, None, None],
 8, [None, None, None, None, None, None, None, None, None],
 9, [None, None, None, None, None, None, None, None, None]
]
"""


def test_play_last_stage1():
    chinese_chess = chess.ChessMap([
        chess.ChessJ(chess.red_camp, chess.piece_index0, chess.Position(4, 9)),
        chess.ChessJ(chess.black_camp, chess.piece_index0, chess.Position(3, 0)),
        chess.ChessC(chess.red_camp, chess.piece_index0, chess.Position(0, 9)),
    ])
    ab_ai = ai_creator()
    choice = ab_ai.next_pace(chinese_chess, depth=4)
    chinese_chess.play(choice.pace)
    ab_ai = ai_creator()
    choice = ab_ai.next_pace(chinese_chess, depth=4, maximizing_player=False)
    chinese_chess.play(choice.pace)
    ab_ai = ai_creator(debug=False)
    choice = ab_ai.next_pace(chinese_chess, depth=4)
    chinese_chess.play(choice.pace)
    assert chinese_chess.end()


def test_eat_J0():
    chinese_chess = chess.ChessMap([
        chess.ChessJ(chess.red_camp, chess.piece_index0, chess.Position(3, 9)),
        chess.ChessJ(chess.black_camp, chess.piece_index0, chess.Position(3, 0)),
        chess.ChessC(chess.red_camp, chess.piece_index0, chess.Position(0, 9)),
    ])
    piece = chinese_chess.get_piece(3, 9)
    chinese_chess.play(ai.Pace(ai.player_type_player, chess.PaceStrategy(piece, chess.Position(3, 0))))
    assert chinese_chess.J0 is None


# todo 循环检测
def play_by_ai(chinese_chess):
    pace_num = 0
    while not chinese_chess.end():
        start = time.time()
        chinese_chess.clear_paces()
        r_ai = ai_creator(debug=True)
        r_choice = r_ai.next_pace(chinese_chess, depth=7)
        if r_choice is None:
            break
        chinese_chess.play(r_choice.pace)
        b_ai = ai_creator(debug=True)
        b_choice = b_ai.next_pace(chinese_chess, depth=7, maximizing_player=False)
        if b_choice is None:
            break
        chinese_chess.play(b_choice.pace)
        pace_num += 1
        delta = time.time() - start
        print(
            "delta={}s, pace={}, red={}, black={}, \nmap={}".format(delta, pace_num, r_choice, b_choice, chinese_chess))
        pass
    print("the end")
    winner = chinese_chess.winner()
    return winner


# 单兵孤将
def test01():
    chinese_chess = read_chess_map_from_str(
        """
        [
             0,    1,    2,    3,    4,    5,    6,    7,    8,
         0, [None, None, None, None, None, None, None, None, None],
         1, [None, None, None, None, 'J0', None, 'z4', None, None],
         2, [None, None, None, None, None, None, None, None, None],
         3, [None, None, None, None, None, None, None, None, None],
         4, [None, None, None, None, None, None, None, None, None],
         5, [None, None, None, None, None, None, None, None, None],
         6, [None, None, None, None, None, None, None, None, None],
         7, [None, None, None, None, None, None, None, None, None],
         8, [None, None, None, None, None, None, None, None, None],
         9, [None, None, None, None, None, 'j0', None, None, None]
        ]
        """
    )
    assert chess.red_camp == play_by_ai(chinese_chess)


# 双兵双仕 https://www.xiangqiqipu.com/Category/View-10242.html
def test02():
    chinese_chess = read_chess_map_from_str(
        """
        [
             0,    1,    2,    3,    4,    5,    6,    7,    8,
         0, [None, None, None, 'S1', None, None, None, None, None],
         1, [None, None, None, None, 'S0', 'J0', None, None, None],
         2, [None, None, 'z3', None, None, None, None, None, None],
         3, [None, None, None, 'z4', None, None, None, None, None],
         4, [None, None, None, None, None, None, None, None, None],
         5, [None, None, None, None, None, None, None, None, None],
         6, [None, None, None, None, None, None, None, None, None],
         7, [None, None, None, None, None, None, None, None, None],
         8, [None, None, None, None, None, None, None, None, None],
         9, [None, None, None, None, 'j0', None, None, None, None]
        ]
        """
    )
    assert chess.red_camp == play_by_ai(chinese_chess)


# 双象双兵 https://www.xiangqiqipu.com/Category/View-10235.html
def test03():
    chinese_chess = read_chess_map_from_str(
        """
        [
             0,    1,    2,    3,    4,    5,    6,    7,    8,
         0, [None, None, None, None, None, None, None, None, None],
         1, [None, 'z3', None, 'J0', None, None, None, None, None],
         2, [None, None, None, None, 'X0', None, None, None, None],
         3, [None, None, None, 'z4', None, None, None, None, None],
         4, [None, None, None, None, None, None, 'X0', None, None],
         5, [None, None, None, None, None, None, None, None, None],
         6, [None, None, None, None, None, None, None, None, None],
         7, [None, None, None, None, None, None, None, None, None],
         8, [None, None, None, None, None, None, None, None, None],
         9, [None, None, None, None, 'j0', None, None, None, None]
        ]
        """
    )
    assert chess.red_camp == play_by_ai(chinese_chess)


def test_next_all_nodes():
    chess_map = chess.ChessMap(chess.init_chess_pieces)
    nodes = chess_map.next_all_nodes(True)
    print("node_len={}".format(len(nodes)))
    for i, node in enumerate(nodes):
        print(i, node)
        node.rollback()
    assert len(nodes) == 44
    print(chess_map)


def test_p_pos():
    chinese_chess = read_chess_map_from_str(
        """
        [
             0,    1,    2,    3,    4,    5,    6,    7,    8,
         0, [None, None, None, None, None, None, None, None, None],
         1, [None, None, None, None, None, None, None, None, None],
         2, [None, None, None, None, None, None, None, None, None],
         3, [None, None, None, None, None, None, None, None, None],
         4, [None, None, None, None, 'Z0', None, None, None, None],
         5, [None, None, None, None, 'p1', None, None, None, None],
         6, [None, None, None, None, 'z3', None, None, None, None],
         7, [None, None, None, None, 'p0', None, None, None, None],
         8, [None, None, None, None, None, None, None, None, None],
         9, [None, None, None, None, None, None, None, None, None]
        ]
        """
    )
    piece = chinese_chess.get_piece(4, 7)
    pos = piece.next_all_pos(chinese_chess)
    pass


if __name__ == '__main__':
    # test_p_pos()
    # test_next_all_nodes()
    # test01()
    # test02()
    test03()
