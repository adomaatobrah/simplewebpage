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

    english = data["english"]

    return jsonify(
        models.generate_alternatives(english)
        )

@app.route('/api/incremental', methods=['GET'])
def incremental():
    content= request.args.get('q')
    data = json.loads(content)

    english = data["english"]
    prefix = data["prefix"]
    recalculation = data["recalculation"]

    return jsonify(
        models.incremental_alternatives(english, prefix, recalculation)
        )

@app.route('/api/completion', methods=['GET'])
def completion():
    content = request.args.get('q')
    data = json.loads(content)

    sentence = data['sentence']
    prefix = data['prefix']

    return jsonify(
        models.completion(sentence, prefix)
    )

if __name__ == '__main__':
    app.run(port=5009)