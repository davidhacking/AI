# -*- coding: utf-8 -*-
from flask import Flask, request, redirect
from flask import jsonify
import json
import sys
from flask import render_template

app = Flask(__name__, static_folder='chess_web', static_url_path='/chess_web')


def get_or_post_data(param_name):
    if request.method == 'POST':
        return request.form[param_name]
    elif request.method == 'GET':
        return request.args.get(param_name)
    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/chess_web/index.html')


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    return "nice"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1937, threaded=True)
