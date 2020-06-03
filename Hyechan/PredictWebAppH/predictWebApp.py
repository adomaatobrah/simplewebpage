from flask import Flask, request, render_template
import torch
from transformers import *

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = Flask(__name__)

@app.route('/')
def predict_form():
    return render_template('predict-form.html')

@app.route('/', methods=['POST'])
def predict_scoring():
    prompt_text = request.form['text']
    search_depth = int(request.form['num'])
    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)
    batch_size, num_words, vocab = prediction_scores.shape

    score = 0
    next_pos = 1

    # Used for returning to html
    twodresults = []
    poslist = []
    wordlist = []
    
    for word in prediction_scores[0]:
        if next_pos >= len(encoded_prompt[0]):
            break
        
        next_word = encoded_prompt[0, next_pos]
        predicted_words = word.topk(search_depth).indices
        predicted_words_list = []
        results = []

        for index in predicted_words:
            predicted_words_list.append(index.item())
            results.append(tokenizer.decode(index.item()))

        twodresults.append(results)
        
        if next_word in predicted_words:
            listpos = predicted_words_list.index(next_word)
            poslist.append(listpos)
            wordlist.append(tokenizer.decode(next_word.item()))
            score += 1 - listpos/vocab
        else:
            wordlist.append(tokenizer.decode(next_word.item()))
            poslist.append(None)
            
        next_pos = next_pos + 1
                             
    return render_template('result.html',
                           prompt = prompt_text,
                           final_score = score / (num_words - 1),
                           depth = search_depth,
                           twodarray = twodresults,
                           len = len(twodresults),
                           positions = poslist,
                           words = wordlist)
