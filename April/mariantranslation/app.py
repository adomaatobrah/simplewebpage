# pylint: disable=E1101
from flask import Flask, render_template, request, url_for, jsonify
import torch
from transformers import MarianMTModel, MarianTokenizer
from flask_cors import CORS
import random
import string

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
    copy_input = request.args.get('copy')
    english = request.args.get('english')

    if copy_input == "true":
        start = english
    else:
        start = request.args.get('start')

    #english only- spanish behind the scenes
    if skip == "true":
        engbatch = en_ROMANCE_tokenizer.prepare_translation_batch([english])
        eng_to_spanish = en_ROMANCE.generate(**engbatch)
        machine_translation = en_ROMANCE_tokenizer.decode(eng_to_spanish[0])
        tokenizer = ROMANCE_en_tokenizer
        model = ROMANCE_en
        batchstr = ">>en<<" + machine_translation.replace("<pad> ", '')
        starting_word = tokenizer.convert_tokens_to_ids(en_ROMANCE_tokenizer.tokenize(start))

    #show spanish
    else:
        tokenizer = en_ROMANCE_tokenizer
        model = en_ROMANCE
        batchstr = ">>es<<" + english
        starting_word = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(start))

    prefix = torch.LongTensor(starting_word)

    batch = tokenizer.prepare_translation_batch([batchstr])
    eng_to_spanish = model.generate(**batch)
    machine_translation = tokenizer.decode(eng_to_spanish[0]).split("<pad>")[1]

    original_encoded = model.get_encoder()(**batch)
    decoder_start_token = model.config.decoder_start_token_id

    partial_decode = torch.LongTensor([decoder_start_token]).unsqueeze(0)
    past = (original_encoded, None)
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
        
        #start with designated beginning
        if x < len(prefix):
            next_token_to_add = prefix[x]
        else:
            next_token_to_add = next_token_logits[0].argmax()

        #append top 10 predictions for each token to list
        decoded_predictions = []
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

    if skip == "true":
        new_english = final
    #back translate spanish into english
    else:
        batch2 = ROMANCE_en_tokenizer.prepare_translation_batch([">>en<< " + final])
        spanish_to_english = ROMANCE_en.generate(**batch2)
        new_english = ROMANCE_en_tokenizer.decode(spanish_to_english[0]).replace("<pad>", '')

    return jsonify({"translation": final,
                    "expected" : machine_translation,
                    "newEnglish" : new_english,
                    "tokens" : decoded_tokens,
                    "predictions" : prediction_list
                })


@app.route('/rearrange', methods=['GET'])
def rearrange():
    english = request.args.get('english')
    start = request.args.get('start')
    auto = request.args.get('auto')

    print(start)

    tokenizer = ROMANCE_en_tokenizer
    model = ROMANCE_en

    wordlist = [''.join(x for x in par if x not in string.punctuation) for par in english.split(' ')]
    first_phrases = set([word.capitalize() for word in wordlist])
    print(first_phrases)

    engbatch = en_ROMANCE_tokenizer.prepare_translation_batch([">>es<<" + english])
    eng_to_spanish = en_ROMANCE.generate(**engbatch)
    machine_translation = en_ROMANCE_tokenizer.decode(eng_to_spanish[0])

    def get_alt(start, whole):
        if start in wordlist:
            pos = wordlist.index(start.lstrip())
        else:
            res = [i for i in wordlist if start.lstrip() in i]
            pos = wordlist.index(res[0])

        #word before selected word
        first_phrases.add(wordlist[pos - 1].capitalize())
        #2 words before selected word
        first_phrases.add(' '.join(wordlist[pos-2: pos]).capitalize())
        first_phrases.add('The')
        prefixes = [word + ' ' + start.lstrip() for word in first_phrases]
        prefixes.append(start.lstrip().capitalize())

        results = []
        scores = []

        for prefix in prefixes:
            tokenized_prefix = tokenizer.convert_tokens_to_ids(en_ROMANCE_tokenizer.tokenize(prefix.strip()))
            prefix = torch.LongTensor(tokenized_prefix)

            batch = tokenizer.prepare_translation_batch([machine_translation.replace("<pad> ", '')])
            english_encoded = model.get_encoder()(**batch)
            decoder_start_token = model.config.decoder_start_token_id
            partial_decode = torch.LongTensor([decoder_start_token]).unsqueeze(0)
            past = (english_encoded, None)

            num_tokens_generated = 0
            total = 0
            MAX_LENGTH = 100
            
            while True:
                model_inputs = model.prepare_inputs_for_generation(
                partial_decode, past=past, attention_mask=batch['attention_mask'], use_cache=model.config.use_cache
                )
                with torch.no_grad():
                    model_outputs = model(**model_inputs)

                next_token_logits = model_outputs[0][:, -1, :]
                past = model_outputs[1]

                #start with user inputted beginning
                if num_tokens_generated < len(prefix):
                    next_token_to_add = prefix[num_tokens_generated]
                else:
                    if whole:
                        next_token_to_add = next_token_logits[0].argmax()
                    else:
                        break        
                next_token_logprobs = next_token_logits - next_token_logits.logsumexp(1, True)
                token_score = next_token_logprobs[0][next_token_to_add].item()
                total += token_score

                #add new token to tokens so far
                partial_decode = torch.cat((partial_decode, next_token_to_add.unsqueeze(0).unsqueeze(0)), -1)
                num_tokens_generated+= 1

                if next_token_to_add.item() == 0 or not (num_tokens_generated < MAX_LENGTH):
                    break

            #list of tokens used to display sentence
            decoded_tokens = [sub.replace('\u2581', '\u00a0') for sub in tokenizer.convert_ids_to_tokens(partial_decode[0])]
            decoded_tokens.remove("<pad>")

            final = tokenizer.decode(partial_decode[0]).replace("<pad>", '')
            score = round(total/(len(decoded_tokens)), 3)
            results.append(final)
            scores.append(score)
            
        ind = scores.index(max(scores))
        winner = results[ind]
        winnerscore = scores[ind]
        print("\nMost likely: ", winner)
        return (winnerscore, winner)

    alternatives = []
    winner = ''
    if auto == 'true':
        for word in wordlist[3:]:
            alt = get_alt(word, True)
            if alt not in alternatives:
                alternatives.append(alt)
            sorted_scores = sorted(((score, result) for score, result in alternatives), reverse=True)
        alternatives = [pair[1] for pair in sorted_scores]

    else:
        winner = get_alt(start, False)[1]
    return jsonify({
        "newEnglish" : winner,
        "alternatives" : alternatives
    })
        

if __name__ == '__main__':
    app.run()