# pylint: disable=E1101
from flask import Flask, render_template, request, url_for, jsonify
from flask_cors import CORS
import random
import string
import models
import json

DEBUG = True
app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/api/result', methods=['GET'])
def result():
    content= request.args.get('q')
    data = json.loads(content)
    print(data)
    print(type(data))

    english_only = data["skip"]
    english = data["english"]
    copy = data["copy"]
    if copy:
        print("wrong")
        start = english
    else:
        print("right")
        print(data['start'])
        start = data["start"]

    return jsonify(
        models.incremental_generation(
            english_only=english_only,
            english=english, 
            start=start,
            prefix_only=False
            )
        )


@app.route('/api/rearrange', methods=['GET'])
def rearrange():
    content= request.args.get('q')
    data = json.loads(content)
    english = data['english']
    start = data['start']
    auto = data['auto']

    return jsonify(
        models.rearrange(
            english=english,
            start=start,
            auto=auto
        )
    )

if __name__ == '__main__':
    app.run()