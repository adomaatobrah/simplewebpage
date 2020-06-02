from flask import Flask, request, render_template
import torch
from transformers import *

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
    num = int(request.form['num'])
    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)

    score = 0;
    next_pos = 1;

    for word in prediction_scores[0]:
        if next_pos >= len(encoded_prompt[0]):
            break

        checklist = [index.item() for index in word.topk(num).indices]
        results = [tokenizer.decode(index.item()) for index in word.topk(num).indices]
        

        if encoded_prompt[0, next_pos] in word.topk(num).indices:
            listpos = checklist.index(encoded_prompt[0, next_pos])
            score = score + ((50257 - listpos)/50257)

        next_pos = next_pos + 1
    
    return "The predictability of \'" + prompt_text + "\' is: " + str(score / (len(encoded_prompt[0]) - 1))
