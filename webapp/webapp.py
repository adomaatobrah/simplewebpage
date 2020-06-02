from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/predict')
def predict_form():
    return render_template('predict-form.html')

@app.route('/predict', methods=['POST'])
def predict_scoring():
    prompt_text = request.form['text']
    return 'prompt_text'
