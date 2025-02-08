# -*- coding: utf-8 -*-

from flask import Flask, send_from_directory, request
import os
from elephantfish.ai_play import predict_best_move_and_score, move2pos
from elephantfish.elephantfish import render

app = Flask(__name__)

# 定义静态文件夹路径
UI_FOLDER = '/home/david/MF/github/AI/chinese_chess_ui'

# 处理根路径请求，默认返回 index.html
@app.route('/')
def index():
    return send_from_directory(UI_FOLDER, 'index.html')

# 处理其他文件请求
@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(UI_FOLDER, path)

@app.route('/ai_play', methods=['POST'])
def ai_play_func():
    data = request.get_json()
    if data is None:
        return "请求数据不是有效的 JSON 格式", 400

    board = data.get('board')
    my = data.get('my')

    try:
        board = str(board)
        my = int(my)
    except ValueError:
        return "参数类型转换失败，my 必须能转换为整数", 400
    move, score = predict_best_move_and_score(board, my)
    if my == -1:
        move = 255 - move[0] - 1, 255 - move[1] - 1
    render_move = render(move[0]) + render(move[1])
    response = {
        "move": move2pos(render_move),
        "score": score,
        "my": my
    }
    return response, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)