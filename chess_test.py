import chess


def test_chess_c():
    chess_map = chess.ChessMap(chess.init_chess_pieces)
    piece = chess_map.get_piece(0, 9)
    camp_chess_name = piece.camp_chess_name()
    name = piece.name()
    paces = piece.next_all_pos(chess_map)
    pass


if __name__ == '__main__':
    test_chess_c()
