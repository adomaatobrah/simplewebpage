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

    words = []

    input_ids = tokenizer.encode("translate English to German: " + english, return_tensors="pt")
    output_ids = tokenizer.encode(german, return_tensors='pt')


    outputs1 = model.generate(input_ids, max_length=40, num_beams=4, early_stopping=True)
    machine_translation = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in outputs1]

    lm_labels = tokenizer.encode(german, return_tensors='pt')
    outputs = model(input_ids=input_ids, lm_labels=lm_labels)

    loss, prediction_scores = outputs[:2]

    all_predictions = []
    next_pos = 0

    for word in prediction_scores[0]:
        predicted_words = word.topk(1000).indices
        next_word = output_ids[0, next_pos]
        encoded_predictions = []
        decoded_predictions = []
        colors = ()

        for index in predicted_words:
            decoded_predictions.append(tokenizer.decode(index.item()))
            encoded_predictions.append(index.item())
        if next_word in predicted_words:
            listpos = encoded_predictions.index(next_word)          
            if listpos == 0:
                colors = (tokenizer.decode(next_word.item()), "lime")
            elif listpos <= 10:
                colors = (tokenizer.decode(next_word.item()), "yellow")
            else:
                colors = (tokenizer.decode(next_word.item()), "magenta")

        all_predictions.append((colors, decoded_predictions[0:5]))
        next_pos += 1
    return jsonify({
                    "translation": machine_translation[0],
                    "predictions": all_predictions
                    })

if __name__ == '__main__':
    app.run()