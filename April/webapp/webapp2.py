from flask import Flask, render_template, request
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

app = Flask(__name__)

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')


@app.route('/')
def form():
    return render_template("home.html")


@app.route('/result')
def result():
    prompt_text = request.args['text']
    num_results = int(request.args['number'])

    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)
    
    batch_size, num_input_words, vocabulary_size = prediction_scores.shape
    assert batch_size == 1
    assert vocabulary_size == 50257

    num = 0
    predictability = 0
    list_of_dicts = []

    for x in range(0, encoded_prompt.numel()-1):
        prediction_dict = {}
        prediction_list = [(index.item()) for index in prediction_scores[0, num].topk(num_results).indices]

        for index in prediction_scores[0, num].topk(num_results).indices:
            word = tokenizer.decode(index.item())
            if index.item() == encoded_prompt[0, num+1]:
                prediction_dict.update({word:"blue"})
                predictability_rank = prediction_list.index(encoded_prompt[0, num+1])
                predictability += 1 - predictability_rank / vocabulary_size
            else:
                prediction_dict.update({word : "black"})

        list_of_dicts.append(prediction_dict)
        
        num += 1

    final_score = str(predictability/(encoded_prompt.numel()-1))
    
    return render_template("home.html", 
                            predictions = list_of_dicts,  
                            usertext = prompt_text, 
                            score = final_score)


