from flask import Flask, render_template, request, url_for, jsonify
import torch
from transformers import MarianMTModel, MarianTokenizer
from flask_cors import CORS
import random

DEBUG = True
app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

en_ROMANCE_model_name = 'Helsinki-NLP/opus-mt-en-ROMANCE'
en_ROMANCE_tokenizer = MarianTokenizer.from_pretrained(en_ROMANCE_model_name)
en_ROMANCE = MarianMTModel.from_pretrained(en_ROMANCE_model_name)

ROMANCE_en_model_name = 'Helsinki-NLP/opus-mt-ROMANCE-en'
ROMANCE_en_tokenizer = MarianTokenizer.from_pretrained(ROMANCE_en_model_name)
ROMANCE_en = MarianMTModel.from_pretrained(ROMANCE_en_model_name)


@app.route('/result', methods=['GET'])
def result():
    tokenizer = en_ROMANCE_tokenizer
    model = en_ROMANCE

    english = request.args.get('english')
    spanish = request.args.get('spanish')

    starting_word = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(spanish))

    batch = tokenizer.prepare_translation_batch([">>es<< " + english])
    eng_to_spanish = model.generate(**batch)
    machine_translation = tokenizer.decode(eng_to_spanish[0]).split("<pad>")[1]
    print("starting token: ", spanish, ": ", starting_word)

    english_encoded = model.get_encoder()(**batch)
    decoder_start_token = model.config.decoder_start_token_id
    # pylint: disable=E1101
    partial_decode = torch.LongTensor([decoder_start_token]).unsqueeze(0)
    past = (english_encoded, None)
    prefix = torch.LongTensor(starting_word)
    # pylint: enable=E1101
    next_token_to_add = torch.tensor(1)
    x = 0

    prediction_list = []

    while next_token_to_add.item() != 0 and x < 100:
        model_inputs = model.prepare_inputs_for_generation(
        partial_decode, past=past, attention_mask=batch['attention_mask'], use_cache=model.config.use_cache
        )
        with torch.no_grad():
            model_outputs = model(**model_inputs)

        next_token_logits = model_outputs[0][:, -1, :]
        past = model_outputs[1]
        
        if x < len(prefix):
            next_token_to_add = prefix[x]
        else:
            next_token_to_add = next_token_logits[0].argmax()
        decoded_predictions = []
        for tok in next_token_logits[0].topk(10).indices:
            decoded_predictions.append(tokenizer.convert_ids_to_tokens(tok.item()).replace('\u2581', '\u00a0'))
        
        prediction_list.append(decoded_predictions)

        partial_decode = torch.cat((partial_decode, next_token_to_add.unsqueeze(0).unsqueeze(0)), -1)
        x+= 1

    decoded_tokens = [sub.replace('\u2581', '\u00a0') for sub in tokenizer.convert_ids_to_tokens(partial_decode[0])]
    decoded_tokens.remove("<pad>")
    final = tokenizer.decode(partial_decode[0]).split("<pad>")[1]

    batch2 = ROMANCE_en_tokenizer.prepare_translation_batch([">>en<< " + final])
    spanish_to_english = ROMANCE_en.generate(**batch2)
    new_english = ROMANCE_en_tokenizer.decode(spanish_to_english[0]).split("<pad>")[1]

    return jsonify({"translation": final,
                    "expected" : machine_translation,
                    "newEnglish" : new_english,
                    "tokens" : decoded_tokens,
                    "predictions" : prediction_list
                })

@app.route('/auto', methods=['GET'])
def auto():
    tokenizer = en_ROMANCE_tokenizer
    model = en_ROMANCE

    english = ">>es<<" + request.args.get('english')
    #spanish = request.args.get('spanish')

    batch = tokenizer.prepare_translation_batch([english])
    eng_to_spanish = model.generate(**batch)
    machine_translation = tokenizer.decode(eng_to_spanish[0]).split("<pad>")[1]

    eng_to_spanish_withbeams = model.generate(num_beams=50, num_return_sequences=50, **batch)
    translations = []
    english_backtrans = []
    for x in range(0, 50):
        translation = tokenizer.decode(eng_to_spanish_withbeams[x]).replace("<pad>",'')
        translations.append(translation)
        batch2 = ROMANCE_en_tokenizer.prepare_translation_batch([">>en<< " + translation])
        spanish_to_english = ROMANCE_en.generate(**batch2)
        new_english = ROMANCE_en_tokenizer.decode(spanish_to_english[0]).replace("<pad>", '')
        english_backtrans.append(new_english)

    # english_encoded = model.get_encoder()(**batch)
    # decoder_start_token = model.config.decoder_start_token_id

    # starting_word = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(spanish))
    # # pylint: disable=E1101
    # prefix = torch.LongTensor(starting_word)
    #  # pylint: enable=E1101
    # alternatives = []

    # for x in range(0, 5):
    #     past = (english_encoded, None)
    #     partial_decode = torch.LongTensor([decoder_start_token]).unsqueeze(0)
    #     y = 0
    #     next_token_to_add = torch.tensor(1)
    #     while next_token_to_add.item() != 0 and y < 100:    
    #         model_inputs = model.prepare_inputs_for_generation(
    #         partial_decode, past=past, attention_mask=batch['attention_mask'], use_cache=model.config.use_cache
    #         )
    #         with torch.no_grad():
    #             model_outputs = model(**model_inputs)
    #         next_token_logits = model_outputs[0][:, -1, :]
    #         past = model_outputs[1]

    #         if y < len(prefix):
    #             next_token_to_add = prefix[y]
    #         else:
    #             next_token_to_add = next_token_logits[0].topk(4).indices[random.randint(0, 1)]

    #         partial_decode = torch.cat((partial_decode, next_token_to_add.unsqueeze(0).unsqueeze(0)), -1)
    #         y += 1
    
    #     final = tokenizer.decode(partial_decode[0]).replace("<pad>", '')
    #     alternatives.append(final)

    return jsonify({
                    "expected" : machine_translation,
                    "alternatives" : translations,
                    "engAlternatives" : english_backtrans,
                })

if __name__ == '__main__':
    app.run()