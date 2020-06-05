from flask import Flask, render_template, request
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
app = Flask(__name__)

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')


@app.route('/')
def form():
    return render_template("home.html")

@app.route('/', methods=["POST"])
def result():
    # prompt_text holds the user input
    prompt_text = request.form["x"]
    # depth to search
    num = int(request.form["Num"])

    # encode and generate using the model
    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)
    
    # variables we need from the model
    size, words_input, vocab_size = prediction_scores.shape
    assert vocab_size == 50257

    # index of the word in the phrase
    element_pos= 0
    # score for each word (additive)
    predictability = 0

    # decoded prediction list used for indexing purposes
    decoded_prediction_list = []
    # used for color-coding purposes
    tuples = []
    prediction_str = ""

    # for each word in the encoded prompt
    for word in range(0, encoded_prompt.numel()-1):
        # create a list of predictions for the next word to that word
        prediction_list = [(index.item()) for index in prediction_scores[0, element_pos].topk(100).indices]
        # create a decoded version of the same list
        decoded_prediction_list=[tokenizer.decode(index.item()) for index in prediction_scores[0, element_pos].topk(100).indices]

        # if the next word of the encoded prompt is in the user-input range of the prediction_list
        if encoded_prompt[0, element_pos+1] in prediction_list[0:num]:
            # get the index of the encoded prompt within prediction_list
            predictability_rank = prediction_list.index(encoded_prompt[0, element_pos+1])
            # score it by dividing by vocab size
            predictability += 1 - predictability_rank / vocab_size

    
        next_word = tokenizer.decode(encoded_prompt[0, element_pos+1].item())
        if encoded_prompt[0, element_pos+1]  in prediction_list[0:10]:
            tuples.append((next_word, "green"))

        elif encoded_prompt[0, element_pos+1] in prediction_list:
            tuples.append((next_word, "yellow"))

        else:
            tuples.append((next_word, "red"))
            
        element_pos += 1

        # average score for the whole phrase
        score = str(predictability/(encoded_prompt.numel()-1))

    return render_template("home.html",
        text_output = tuples,
        score_output = score)
        

        