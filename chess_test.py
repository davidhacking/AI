import chess

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


if __name__ == '__main__':
    test_z()
    map_next_all_nodes()
    test_chess_map_str()
    test_chess_c()
    test_chess_c2()
    test_chess_m()
