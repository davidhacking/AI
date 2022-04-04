# -*- coding: utf-8 -*-
from flask import Flask, request, redirect
import time

import cn_chess_ai.chess as chess
from ai import alpha_beta_ai_v2
from ai import ai

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


@app.route('/next_ai_play', methods=['GET', 'POST'])
def next_ai_play():
    start = time.time()
    x1 = int(request.args.get('x1'))
    y1 = int(request.args.get('y1'))
    x2 = int(request.args.get('x2'))
    y2 = int(request.args.get('y2'))
    print("red pace: ", x1, y1, x2, y2)
    piece = chinese_chess.get_piece(x1, y1)
    chinese_chess.play(ai.Pace(ai.player_type_player, chess.PaceStrategy(piece, chess.Position(x2, y2), chinese_chess)))
    if chinese_chess.end():
        winner = chinese_chess.winner()
        return {"code": -1, "msg": "winner: {}!".format("ai" if winner == ai.player_type_ai else "you")}
    ab_ai = alpha_beta_ai_v2.AlphaBetaAIV2()
    choice = ab_ai.next_pace(chinese_chess, depth=4, maximizing_player=False)
    chinese_chess.play(choice.pace)
    delta = time.time() - start
    print("process time: {}s".format(delta))
    print(choice.pace.strategy)
    print(chinese_chess)
    chinese_chess.clear_paces()
    s = choice.pace.strategy
    return {"code": 0, "msg": "success",
            "data": {"x1": s.from_pos.x, "y1": s.from_pos.y, "x2": s.to_pos.x, "y2": s.to_pos.y}}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1937, threaded=True)
