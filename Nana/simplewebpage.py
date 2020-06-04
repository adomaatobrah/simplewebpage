from flask import Flask, render_template, request
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
app = Flask(__name__)

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')


@app.route('/')
def form():
    return render_template("home.html")

@app.route('/', methods=["GET"])
def result():
    prompt_text = request.form["x"]
    #return prompt_text
    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)

    size, words_input, vocab_size = prediction_scores.shape

    assert vocab_size == 50257
    element_pos= 0
    predictability = 0
    decoded_prediction_list = []
    tuples = []
    prediction_str = ""

    for word in range (0, encoded_prompt.numel()-1):
        prediction_list = [(index.item()) for index in prediction_scores[0, element_pos].topk(100).indices]
        decoded_prediction_list=[tokenizer.decode(index.item()) for index in prediction_scores[0, element_pos].topk(100).indices]
        print(decoded_prediction_list)

    
        if encoded_prompt[0, element_pos+1] in prediction_list[0:num]:
            predictability_rank = prediction_list.index(encoded_prompt[0, element_pos+1])
            predictability += 1 - predictability_rank / vocab_size

        prediction_list_high = [(index.item()) for index in prediction_scores[0, element_pos].topk(10).indices]
        decoded_prediction_list_high=[tokenizer.decode(index.item()) for index in prediction_scores[0, element_pos].topk(10).indices]
        
        next_word = tokenizer.decode(encoded_prompt[0, element_pos+1].item())
        if encoded_prompt[0, element_pos+1]  in prediction_list[0:10]:
            tuples.append((next_word, "green"))

        elif encoded_prompt[0, element_pos+1] in prediction_list:
            tuples.append((next_word, "yellow"))

        else:
            tuples.append((next_word, "red"))
            
        element_pos += 1

        
        print("The predictability score for " + str(num) + " is: " + str(predictability/(encoded_prompt.numel()-1)))
        return render_template("home.html")