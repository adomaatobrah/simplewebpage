from flask import Flask, render_template, request, url_for, jsonify
import torch
from transformers import MarianMTModel, MarianTokenizer
from flask_cors import CORS
import random

DEBUG = True
app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

#english to spanish
en_ROMANCE_model_name = 'Helsinki-NLP/opus-mt-en-ROMANCE'
en_ROMANCE_tokenizer = MarianTokenizer.from_pretrained(en_ROMANCE_model_name)
en_ROMANCE = MarianMTModel.from_pretrained(en_ROMANCE_model_name)

#spanish to english
ROMANCE_en_model_name = 'Helsinki-NLP/opus-mt-ROMANCE-en'
ROMANCE_en_tokenizer = MarianTokenizer.from_pretrained(ROMANCE_en_model_name)
ROMANCE_en = MarianMTModel.from_pretrained(ROMANCE_en_model_name)


@app.route('/result', methods=['GET'])
def result():
    skip = request.args.get("skip")
    english = request.args.get('english')
    start = request.args.get('start')
    print(start)

    #english only- spanish behind the scenes
    if skip == "true":
        tokenizer = ROMANCE_en_tokenizer
        model = ROMANCE_en

    #show spanish
    else:
        tokenizer = en_ROMANCE_tokenizer
        model = en_ROMANCE

    starting_word = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(start))
    prefix = torch.LongTensor(starting_word)
    print(tokenizer.decode(prefix))

    #get auto translation
    batch = tokenizer.prepare_translation_batch([">>es<< " + english])
    eng_to_spanish = model.generate(**batch)
    machine_translation = tokenizer.decode(eng_to_spanish[0]).split("<pad>")[1]

    english_encoded = model.get_encoder()(**batch)
    decoder_start_token = model.config.decoder_start_token_id
    # pylint: disable=E1101
    partial_decode = torch.LongTensor([decoder_start_token]).unsqueeze(0)
    past = (english_encoded, None)
    # pylint: enable=E1101
    next_token_to_add = torch.tensor(1)
    x = 0

    prediction_list = []

    #stop when </s> token generated, or max num tokens exceded (just in case)
    while next_token_to_add.item() != 0 and x < 100:
        model_inputs = model.prepare_inputs_for_generation(
        partial_decode, past=past, attention_mask=batch['attention_mask'], use_cache=model.config.use_cache
        )
        with torch.no_grad():
            model_outputs = model(**model_inputs)

        next_token_logits = model_outputs[0][:, -1, :]
        past = model_outputs[1]
        
        #start with user inputted beginning
        if x < len(prefix):
            next_token_to_add = prefix[x]
            print(next_token_to_add)
        else:
            next_token_to_add = next_token_logits[0].argmax()
        decoded_predictions = []

        #append top 10 predictions for each token to list
        for tok in next_token_logits[0].topk(10).indices:
            decoded_predictions.append(tokenizer.convert_ids_to_tokens(tok.item()).replace('\u2581', '\u00a0'))
        
        #list of lists of predictions
        prediction_list.append(decoded_predictions)

        #add new token to tokens so far
        partial_decode = torch.cat((partial_decode, next_token_to_add.unsqueeze(0).unsqueeze(0)), -1)
        x+= 1

    #list of tokens used to display sentence
    decoded_tokens = [sub.replace('\u2581', '\u00a0') for sub in tokenizer.convert_ids_to_tokens(partial_decode[0])]
    decoded_tokens.remove("<pad>")

    final = tokenizer.decode(partial_decode[0]).replace("<pad>", '')

    #back translate spanish into english
    batch2 = ROMANCE_en_tokenizer.prepare_translation_batch([">>en<< " + final])
    spanish_to_english = ROMANCE_en.generate(**batch2)
    new_english = ROMANCE_en_tokenizer.decode(spanish_to_english[0]).replace("<pad>", '')

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
    skip = request.args.get("skip")

    #translate english input to spanish
    batch = tokenizer.prepare_translation_batch([english])
    eng_to_spanish = model.generate(**batch)
    machine_translation = tokenizer.decode(eng_to_spanish[0])

    english_backtrans = []

    #if only English results are requested
    if skip == "true":
        #translate spanish back to english
        batch2 = ROMANCE_en_tokenizer.prepare_translation_batch([">>en<<"+ machine_translation])
        back_to_english = ROMANCE_en.generate(num_beams=20, num_return_sequences=20, bad_words_ids=[[1695],[1973],[7927],[55],[23],[367],[51],[12390],[1172],[45351],[39]], **batch2)
        translations = []
        for x in range(0, 20):
            translations.append(ROMANCE_en_tokenizer.decode(back_to_english[x]).replace("<pad>", ''))

    #spanish results
    else:
        eng_to_spanish_withbeams = model.generate(num_beams=20, num_return_sequences=20, **batch)
        translations = []
        for x in range(0, 20):
            translations.append(tokenizer.decode(eng_to_spanish_withbeams[x]).replace("<pad>",''))
            
            #get english back translation of each result
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

@app.route('/rearrange', methods=['GET'])
def rearrange():
    english = request.args.get('english')
    start = request.args.get('start')

    tokenizer = ROMANCE_en_tokenizer
    model = ROMANCE_en

    first_words = ["The", "All", "", "It", "An", "A"]

    # wordlist = english.split(' ')
    # for word in wordlist:
    #     first_words.append(word.capitalize())

    results = []
    scores = []
        
    for word in first_words:
        join_prefix_str = word + " " + start
        tokenized_prefix = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(join_prefix_str))
        prefix = torch.LongTensor(tokenized_prefix)
        
        batch = tokenizer.prepare_translation_batch([">>es<<" + english])
        english_encoded = model.get_encoder()(**batch)
        decoder_start_token = model.config.decoder_start_token_id
        # pylint: disable=E1101
        partial_decode = torch.LongTensor([decoder_start_token]).unsqueeze(0)
        past = (english_encoded, None)
        # pylint: enable=E1101
        next_token_to_add = torch.tensor(1)
        x = 0
        
        prediction_list = []
        total = 0
        #stop when </s> token generated, or max num tokens exceded (just in case)
        while next_token_to_add.item() != 0 and x < 100:
            model_inputs = model.prepare_inputs_for_generation(
            partial_decode, past=past, attention_mask=batch['attention_mask'], use_cache=model.config.use_cache
            )
            with torch.no_grad():
                model_outputs = model(**model_inputs)

            next_token_logits = model_outputs[0][:, -1, :]
            past = model_outputs[1]

            #start with user inputted beginning
            if x < len(prefix):
                next_token_to_add = prefix[x]
                if next_token_to_add in next_token_logits[0].topk(1000).indices:
                    index = ((next_token_logits[0].topk(1000).indices == next_token_to_add).nonzero())[0][0].item()
                    value = next_token_logits[0].topk(1000).values[index].item()
                    total += value
                    
                    if x == 0:
                        save = next_token_logits
            else:
                next_token_to_add = next_token_logits[0].argmax()
                if x == len(prefix):
                    total += next_token_logits[0].topk(10).values[0].item()

            #add new token to tokens so far
            partial_decode = torch.cat((partial_decode, next_token_to_add.unsqueeze(0).unsqueeze(0)), -1)
            x+= 1

        #list of tokens used to display sentence
        decoded_tokens = [sub.replace('\u2581', '\u00a0') for sub in tokenizer.convert_ids_to_tokens(partial_decode[0])]
        decoded_tokens.remove("<pad>")

        final = tokenizer.decode(partial_decode[0]).replace("<pad>", '')
        score = round(total/(len(prefix)), 3)
        results.append(final)
        scores.append(score)
        
        print("\n" + final)
        print(score)
        
    ind = scores.index(max(scores))
    winner = results[ind]
    print("\nMost likely: ", winner)
    return jsonify({
        "newEnglish" : winner,
    })
        

if __name__ == '__main__':
    app.run()