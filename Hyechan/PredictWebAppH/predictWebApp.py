from flask import Flask, request, render_template
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

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
    inputlist = [(tokenizer.decode(encoded_prompt[0, 0].item()), "white")]
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
        predicted_words = word.topk(max(1000, search_depth)).indices

        # initialize lists that will help with printing/indexing
        predicted_words_list = []
        results = []

        # for each index in predicted words, append to the lists
        for index in predicted_words:
            predicted_words_list.append(index.item())
            results.append(tokenizer.decode(index.item()))

        # append the necessary amount of results to the predictions
        #   2-d array, for displaying in html
        predictions.append(results[0:search_depth])
        
        # if the next word is within the topk predictions
        if next_word in predicted_words:
            # get the index of that word
            listpos = predicted_words_list.index(next_word)

            # if the index is less than the user-input depth value
            #   (i.e. we care about it for overall predictability calculations)
            if listpos < search_depth:
                # append it to a list of positions that will be sent to the html
                poslist.append(listpos)
                # increment the score (weighted by its position overall)
                score += 1 - listpos/vocab
            # otherwise append no value to the positions list
            else:
                poslist.append(None)

            # The below section is for color-coding the input
            if listpos < 10:
                inputlist.append((tokenizer.decode(next_word.item()), "lime"))
            elif listpos < 100:
                inputlist.append((tokenizer.decode(next_word.item()), "yellow"))
            elif listpos < 1000:
                inputlist.append((tokenizer.decode(next_word.item()), "red"))
            else:
                inputlist.append((tokenizer.decode(next_word.item()), "magenta"))
        # else (the word is not in the topk results) append a None position
        #   and color it magenta (not found)
        else:
            poslist.append(None)
            inputlist.append((tokenizer.decode(next_word.item()), "magenta"))

        # append the next word to a "word list" for display purposes
        wordlist.append(tokenizer.decode(next_word.item()))
        next_pos += 1
                             
    return render_template('result.html',
                           prompt = prompt_text,
                           final_score = score / (num_words - 1),
                           depth = search_depth,
                           predictions = predictions,
                           len = len(predictions),
                           inputs = inputlist,
                           positions = poslist,
                           words = wordlist)
