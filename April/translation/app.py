from flask import Flask, render_template, request, url_for, jsonify
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from flask_cors import CORS

DEBUG = True
app = Flask(__name__)
# https://stackoverflow.com/questions/37575089/disable-template-cache-jinja2
#app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

model = T5ForConditionalGeneration.from_pretrained("t5-base")
tokenizer = T5Tokenizer.from_pretrained("t5-base")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@app.route('/result', methods=['GET'])
def result():
    english = request.args.get('english')
    german = request.args.get('german')

    #encode english input with prefix
    input_ids = tokenizer.encode("translate English to German: " + english, return_tensors="pt")
    #encode user's german translation
    output_ids = tokenizer.encode(german, return_tensors='pt')

    #generate and decode machine translation of english input
    outputs1 = model.generate(input_ids, max_length=40, num_beams=4, early_stopping=True)
    machine_translation = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in outputs1]

    #I don't really understand this part to be honest, but it has to do with generating predictions
    outputs = model(input_ids=input_ids, lm_labels=output_ids)
    loss, prediction_scores = outputs[:2]

    all_predictions = []
    next_pos = 0
    colors = []
    decoded_tokens = []

    #loop through encoded lists of predictions
    for tok in prediction_scores[0]:

        #list of top 10 predictions for each token
        predicted_tokens = tok.topk(10).indices

        #current input token
        next_token = output_ids[0, next_pos]

        #decode current token and add to list
        decoded_token = tokenizer.convert_ids_to_tokens(next_token.item()).replace('\u2581', '\u00a0')
        decoded_tokens.append(decoded_token)

        encoded_predictions = []
        decoded_predictions = []

        #loop through each prediction for the current token
        for index in predicted_tokens:
            #convert ids to tokens to maintain word breaks; convert word break character to a space
            decoded_predictions.append(tokenizer.convert_ids_to_tokens(index.item()).replace('\u2581', '\u00a0'))
            encoded_predictions.append(index.item())

        #determine highlight color for each prediction
        if next_token in predicted_tokens:
            listpos = encoded_predictions.index(next_token)      
            if listpos == 0:
                colors.append("lime")
            else:
                colors.append("yellow")
        else:
            colors.append("red")

        #list of lists each containing top 10 predictions
        all_predictions.append(decoded_predictions[0:10])
        next_pos += 1
    return jsonify({
                    "translation": machine_translation[0],
                    "predictions": all_predictions,
                    "colors": colors,
                    "decoded_tokens": decoded_tokens
                    })

@app.route('/wholesentence', methods=['GET'])
def wholesentence():
    english = request.args.get('english')
    firstword = request.args.get('german')
    german = firstword + " fill fill fill fill fill fill fill fill"

    input_ids = tokenizer.encode("translate English to German: " + english, return_tensors="pt")
    
    output_ids = tokenizer.encode(german, return_tensors='pt')
    
    outputs1 = model.generate(input_ids, max_length=40, num_beams=4, early_stopping=True)
    machine_translation = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in outputs1]


    for x in range (1, 9):
        outputs = model(input_ids=input_ids, lm_labels=output_ids)

        loss, prediction_scores = outputs[:2]

        second_choice = prediction_scores[0][x].topk(1).indices[0]
        output_ids[0][x] = second_choice

    final = tokenizer.decode(output_ids[0])

    return jsonify({"translation": final,
                    "expected" : machine_translation[0]
    })



if __name__ == '__main__':
    app.run()