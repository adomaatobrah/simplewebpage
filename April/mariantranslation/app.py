# pylint: disable=E1101
from flask import Flask, render_template, request, url_for, jsonify
from flask_cors import CORS
import random
import string
import models

DEBUG = True
app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/result', methods=['GET'])
def result():
    skip = request.args.get("skip") == 'true'
    copy_input = request.args.get('copy') == 'true'
    english = request.args.get('english')

    if copy_input:
        start = english
    else:
        start = request.args.get('start')

    return jsonify(
        models.incremental_generation(
            english_only=skip,
            english=english, 
            start=start,
            prefix_only=False)
        )


@app.route('/rearrange', methods=['GET'])
def rearrange():
    english = request.args.get('english')
    start = request.args.get('start')
    auto = request.args.get('auto')

    return jsonify(
        models.rearrange(
            english=english,
            start=start,
            auto=auto
        )
    )

if __name__ == '__main__':
    app.run()