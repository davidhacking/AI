import chess
import alpha_beta_ai
import ai
import min_max_ai

# ai_creator = min_max_ai.MinMaxAI
ai_creator = alpha_beta_ai.AlphaBetaAI

"""
 chess_map = [
     0      1     2     3     4     5     6     7     8
 0 ["C0", 'M0', 'X0', 'S0', 'J0', 'S1', 'X1', 'M1', "C1"],
 1 [None, None, None, None, None, None, None, None, None],
 2 [None, 'P0', None, None, None, None, None, 'P1', None],
 3 ['Z0', None, 'Z1', None, 'Z2', None, 'Z3', None, 'Z4'],
 4 [None, None, None, None, None, None, None, None, None],
 5 [None, None, None, None, None, None, None, None, None],
 6 ['z0', None, 'z1', None, 'z2', None, 'z3', None, 'z4'],
 7 [None, 'p0', None, None, None, None, None, 'p1', None],
 8 [None, None, None, None, None, None, None, None, None],
 9 ["c0", 'm0', 'x0', 's0', 'j0', 's1', 'x1', 'm1', "c1"]
 ]
"""


def test_z():
    chess_map = chess.ChessMap([
        chess.ChessZ(chess.black_camp, chess.piece_index0, chess.Position(0, 3)),
        chess.ChessZ(chess.red_camp, chess.piece_index0, chess.Position(0, 6)),
    ])
    pos1 = chess_map.get_piece(0, 3).next_all_pos(chess_map)
    pos2 = chess_map.get_piece(0, 6).next_all_pos(chess_map)
    pass


def test_chess_map_str():
    chess_map = chess.ChessMap(chess.init_chess_pieces)
    print(chess_map)


def test_chess_c():
    chess_map = chess.ChessMap(chess.init_chess_pieces)
    piece = chess_map.get_piece(0, 9)
    camp_chess_name = piece.camp_chess_name()
    name = piece.name()
    pos = piece.next_all_pos(chess_map)
    assert len(pos) == 2
    assert pos[0].equal(chess.Position(0, 8)) or pos[0].equal(chess.Position(0, 7))
    assert pos[1].equal(chess.Position(0, 8)) or pos[1].equal(chess.Position(0, 7))


def test_chess_c2():
    chess_map = chess.ChessMap([
        chess.ChessC(chess.red_camp, chess.piece_index0, chess.Position(2, 8)),
        chess.ChessP(chess.black_camp, chess.piece_index0, chess.Position(2, 7)),
        chess.ChessP(chess.black_camp, chess.piece_index0, chess.Position(0, 8)),
        chess.ChessP(chess.black_camp, chess.piece_index1, chess.Position(2, 9)),
    ])
    piece = chess_map.get_piece(2, 8)
    pos = piece.next_all_pos(chess_map)
    assert len(pos) == 10


def test_chess_m():
    chess_map = chess.ChessMap([
        chess.ChessM(chess.red_camp, chess.piece_index0, chess.Position(2, 9)),
        chess.ChessP(chess.black_camp, chess.piece_index0, chess.Position(3, 9)),
        chess.ChessP(chess.black_camp, chess.piece_index0, chess.Position(1, 7)),
        chess.ChessP(chess.red_camp, chess.piece_index1, chess.Position(3, 7)),
    ])
    piece = chess_map.get_piece(2, 9)
    pos = piece.next_all_pos(chess_map)
    assert len(pos) == 2


def map_next_all_nodes():
    chess_map = chess.ChessMap(chess.init_chess_pieces)
    nodes = chess_map.next_all_nodes(True)
    print("node_len={}".format(len(nodes)))
    for i, node in enumerate(nodes):
        print(i, node)
    assert len(nodes) == 44


def test_play_chinese_chess():
    chinese_chess = chess.ChessMap(chess.init_chess_pieces)
    p = chinese_chess.get_piece(7, 7)
    chinese_chess.play(ai.Pace(ai.player_type_player, chess.PaceStrategy(p, chess.Position(4, 7))))
    piece = chinese_chess.get_piece(7, 0)
    chinese_chess.play(ai.Pace(ai.player_type_ai, chess.PaceStrategy(piece, chess.Position(6, 2))))
    ab_ai = alpha_beta_ai.AlphaBetaAI()
    choice = ab_ai.next_pace(chinese_chess, depth=20)
    chinese_chess.play(choice.pace)


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
    ab_ai = ai_creator(debug=True)
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


if __name__ == '__main__':
    # test_eat_J0()
    test_play_last_stage1()
    # test_play_chinese_chess()
    # test_z()
    # map_next_all_nodes()
    # test_chess_map_str()
    # test_chess_c()
    # test_chess_c2()
    # test_chess_m()
