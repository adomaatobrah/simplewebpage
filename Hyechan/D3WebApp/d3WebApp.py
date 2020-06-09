from flask import Flask, render_template, request, url_for, jsonify
import json
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

app = Flask(__name__)
# https://stackoverflow.com/questions/37575089/disable-template-cache-jinja2
app.config['TEMPLATES_AUTO_RELOAD'] = True

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@app.route('/')
def form():
    return render_template("home.html", len = 0)

@app.route('/result', methods=["POST"])
def result():
    # Get the user input
    prompt_text = request.form['text']
    # Get the search depth (a.k.a. number of results per word)
    num_results = int(request.form['number'])

    # encode prompt and generate predictions
    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)

    # get useful data from the generated predictions
    batch_size, num_input_words, vocabulary_size = prediction_scores.shape
    assert batch_size == 1
    assert vocabulary_size == 50257

    score = 0
    next_pos = 1

    inputlist = [(tokenizer.decode(encoded_prompt[0, 0].item()), 'white')]
    predictions = []
    poslist = []
    wordlist = []

    # for each word of the sentence
    for word in prediction_scores[0]:
        # if the word is out of bounds, break
        if next_pos >= len(encoded_prompt[0]):
            break
        
        # set the next word to the next word of the phrase
        next_word = encoded_prompt[0, next_pos]
        # get the tensor containing the indices of the topk predicted words,
        #   taking k to be the max of either 1000 or the search depth
        predicted_words = word.topk(max(1000, num_results)).indices

        # initialize lists that will help with printing/indexing
        predicted_words_list = []
        results = []

        # for each index in predicted words, append to the lists
        for index in predicted_words:
            predicted_words_list.append(index.item())
            results.append(tokenizer.decode(index.item()))

        # append the necessary amount of results to the predictions
        #   2-d array, for displaying in html
        predictions.append(results[0:num_results])
        
        # if the next word is within the topk predictions
        if next_word in predicted_words:
            # get the index of that word
            listpos = predicted_words_list.index(next_word)

            # if the index is less than the user-input depth value
            #   (i.e. we care about it for overall predictability calculations)
            if listpos < num_results:
                # append it to a list of positions that will be sent to the html
                poslist.append(listpos)
                # increment the score (weighted by its position overall)
                score += 1 - listpos/vocabulary_size
            # otherwise append no value to the positions list
            else:
                poslist.append(None)

            # The below section is for color-coding the input
            if listpos < 10:
                inputlist.append((tokenizer.decode(next_word.item()), 'lime'))
            elif listpos < 100:
                inputlist.append((tokenizer.decode(next_word.item()), 'yellow'))
            elif listpos < 1000:
                inputlist.append((tokenizer.decode(next_word.item()), 'red'))
            else:
                inputlist.append((tokenizer.decode(next_word.item()), 'magenta'))
        # else (the word is not in the topk results) append a None position
        #   and color it magenta (not found)
        else:
            poslist.append(None)
            inputlist.append((tokenizer.decode(next_word.item()), 'magenta'))

        # append the next word to a "word list" for display purposes
        wordlist.append(tokenizer.decode(next_word.item()))
        next_pos += 1
                             
    return render_template('home.html',
                           final_score = score / (num_input_words - 1),
                           depth = num_results,
                           predictions = predictions,
                           inputs = inputlist,
                           positions = poslist)