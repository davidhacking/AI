# -*- coding: utf-8 -*-
from flask import Flask, request, redirect

import ai
import chess
import alpha_beta_ai_v2

app = Flask(__name__, static_folder='../chess_web', static_url_path='/chess_web')

chinese_chess = chess.ChessMap(chess.init_chess_pieces)


def get_or_post_data(param_name):
    if request.method == 'POST':
        return request.form[param_name]
    elif request.method == 'GET':
        return request.args.get(param_name)
    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/chess_web/index.html')


@app.route('/report_black_pace', methods=['GET', 'POST'])
def hello():
    x1 = int(request.args.get('x1'))
    y1 = int(request.args.get('y1'))
    x2 = int(request.args.get('x2'))
    y2 = int(request.args.get('y2'))
    print(x1, y1, x2, y2)
    piece = chinese_chess.get_piece(x1, y1)
    chinese_chess.play(ai.Pace(ai.player_type_ai, chess.PaceStrategy(piece, chess.Position(x2, y2), chinese_chess)))
    ab_ai = alpha_beta_ai_v2.AlphaBetaAIV2()
    choice = ab_ai.next_pace(chinese_chess, depth=5)
    chinese_chess.play(choice.pace)
    print(choice.pace.strategy)
    print(chinese_chess)
    chinese_chess.clear_paces()
    return {"code": 0, "msg": "success"}


if __name__ == '__main__':
    p = chinese_chess.get_piece(7, 7)
    chinese_chess.play(ai.Pace(ai.player_type_player, chess.PaceStrategy(p, chess.Position(4, 7), chinese_chess)))
    app.run(host='127.0.0.1', port=1937, threaded=True)
