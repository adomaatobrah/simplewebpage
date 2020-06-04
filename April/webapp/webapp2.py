from flask import Flask, render_template, request
import torch 
from transformers import GPT2Tokenizer, GPT2LMHeadModel

app = Flask(__name__)

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

@app.route('/')
def form():
    return render_template("home.html")

#calculate predictability score
def get_predictability_score(num_results, x, prediction_scores, 
                                prediction_list, encoded_prompt, 
                                vocabulary_size, prediction_dict, predictability):
    for index in prediction_scores[0, x].topk(num_results).indices:
        word = tokenizer.decode(index.item())
        if index.item() == encoded_prompt[0, x+1]:
            prediction_dict.update({word:"blue"})
            predictability_rank = prediction_list.index(encoded_prompt[0, x+1])
            predictability += 1 - predictability_rank / vocabulary_size
        else:
            prediction_dict.update({word : "black"})
    return predictability

#determine highlight color of each input word; add word and color tuple to list
def highlight_words(x, prediction_list, input_tuples, encoded_prompt):
    next_word = tokenizer.decode(encoded_prompt[0, x+1].item())
    if encoded_prompt[0, x+1] in prediction_list[0:10]:
        input_tuples.append((next_word, "aquamarine"))
    elif encoded_prompt[0, x+1] in prediction_list:
        input_tuples.append((next_word, "yellow"))
    else:
        input_tuples.append((next_word, "red"))

@app.route('/result')
def result():
    prompt_text = request.args['text']
    num_results = int(request.args['number'])

    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)
    
    batch_size, num_input_words, vocabulary_size = prediction_scores.shape
    assert batch_size == 1
    assert vocabulary_size == 50257
    
    list_of_dicts = []

    input_tuples = []
    #add first input word to tuple with no highlight
    first_word = tokenizer.decode(encoded_prompt[0, 0].item())
    input_tuples.append((first_word, "white"))

    predictability = 0

    #loop through input text word by word
    for x in range(0, encoded_prompt.numel()-1):
        prediction_list = [(index.item()) for index in prediction_scores[0, x].topk(100).indices]
        prediction_dict = {}

        predictability = get_predictability_score(num_results, x, prediction_scores, 
                                                    prediction_list, encoded_prompt, 
                                                    vocabulary_size, prediction_dict, predictability)
        list_of_dicts.append(prediction_dict)
        highlight_words(x, prediction_list, input_tuples, encoded_prompt)

    final_score = str(predictability/(encoded_prompt.numel()-1))

    return render_template("home.html", 
                            predictions = list_of_dicts,  
                            usertext = prompt_text, 
                            score = final_score,
                            inputwords = input_tuples)
