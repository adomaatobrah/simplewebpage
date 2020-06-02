from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/predict', methods=['POST'])
def predict_scoring():
    return 'Your predicted score is 0.'
