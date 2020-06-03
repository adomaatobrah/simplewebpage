from flask import Flask, render_template, request
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

app = Flask(__name__)

@app.route('/')
def form():
    return render_template("home.html")

@app.route('/result')
def result():
    prompt_text = request.args['text']
    num_results = int(request.args['number'])

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)

    num = 0
    predictability = 0
    decoded_prediction_list = []
    prediction_str = ""

    for x in range(0, encoded_prompt.numel()-1):
        prediction_list = [(index.item()) for index in prediction_scores[0, num].topk(num_results).indices]
        decoded_prediction_list.append([tokenizer.decode(index.item()) for index in prediction_scores[0, num].topk(num_results).indices])
    
        if encoded_prompt[0, num+1] in prediction_list:
            predictability = predictability + ((50257 - prediction_list.index(encoded_prompt[0, num+1]))/50257)
        
        num += 1

    wordnum = 2
    for ele in decoded_prediction_list:
        prediction_str = prediction_str + "\nword " + str(wordnum) + ": " + str(ele) 
        wordnum += 1
    
    resulttext = "Predictability score for \"" + prompt_text + "\": " + str(predictability/(encoded_prompt.numel()-1))
    
    return render_template("home.html", predictions = prediction_str, result = resulttext)