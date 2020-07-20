import torch
from transformers import MarianMTModel, MarianTokenizer
import string
import pandas as pd
import spacy
from spacy import displacy
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

en_ROMANCE_model_name = 'Helsinki-NLP/opus-mt-en-ROMANCE'
en_ROMANCE_tokenizer = MarianTokenizer.from_pretrained(en_ROMANCE_model_name)
en_ROMANCE = MarianMTModel.from_pretrained(en_ROMANCE_model_name).to(device)

ROMANCE_en_model_name = 'Helsinki-NLP/opus-mt-ROMANCE-en'
ROMANCE_en_tokenizer = MarianTokenizer.from_pretrained(ROMANCE_en_model_name)
ROMANCE_en = MarianMTModel.from_pretrained(ROMANCE_en_model_name).to(device)

original_postprocess = True

class CustomMTModel(MarianMTModel):
    def postprocess_next_token_scores(self, scores, input_ids, *a, **kw):
        if not ROMANCE_en.original_postprocess:
            batch_size, vocab_size = scores.shape
            cur_len = input_ids.shape[1]
            for hypothesis_idx in range(batch_size):
                cur_hypothesis = input_ids[hypothesis_idx]

            if 0 < cur_len <= len(ROMANCE_en.selected_tokens):
                force_token_id = ROMANCE_en.selected_tokens[cur_len-1]
                self._force_token_ids_generation(scores, token_ids=[force_token_id])

        return MarianMTModel.postprocess_next_token_scores(self, scores, input_ids, *a, **kw)

ROMANCE_en.__class__ = CustomMTModel

def score_prefix(machine_translation, prefix):
    tokenizer = ROMANCE_en_tokenizer
    model = ROMANCE_en
    tokenized_prefix = tokenizer.convert_tokens_to_ids(en_ROMANCE_tokenizer.tokenize(prefix.strip()))
    prefix = torch.LongTensor(tokenized_prefix).to(device)

    batch = tokenizer.prepare_translation_batch([machine_translation.replace("<pad> ", '')]).to(device)
    english_encoded = model.get_encoder()(**batch)
    decoder_start_token = model.config.decoder_start_token_id
    partial_decode = torch.LongTensor([decoder_start_token]).to(device).unsqueeze(0)
    past = (english_encoded, None)
    num_tokens_generated = 0
    total = 0
    MAX_LENGTH = 100
    
    #stop when </s> token generated, or max num tokens exceded (just in case)
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
            next_token_to_add = next_token_logits[0].argmax()
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

    return (score, final.lstrip())

def translate(tokenizer, model, text, num_outputs):   
    """Use beam search to get a reasonable translation of 'text'"""
    # Tokenize the source text
    tokenizer.current_spm = tokenizer.spm_source ### HACK!
    batch = tokenizer.prepare_translation_batch([text]).to(model.device)
    
    # Run model
    num_beams = num_outputs
    translated = model.generate(**batch, num_beams=num_beams, num_return_sequences=num_outputs, max_length=40, no_repeat_ngram_size=5)
    
    # Untokenize the output text.
    tokenizer.current_spm = tokenizer.spm_target
    return [tokenizer.decode(t, skip_special_tokens=True, clean_up_tokenization_spaces=False) for t in translated]

#https://stackoverflow.com/questions/39100652/python-chunking-others-than-noun-phrases-e-g-prepositional-using-spacy-etc
def get_pps(doc):
    pps = []
    for token in doc:
        if token.pos_ == 'ADP':
            pp = ' '.join([tok.orth_ for tok in token.subtree])
            pps.append(pp)
        if token.dep_ == 'prep':
            ROMANCE_en.off_limits.append(' '.join([tok.orth_ for tok in token.subtree]))
    return pps

def get_adv_clause(doc):
    clauses = []
    for token in doc:
        if token.dep_ == 'advcl' or token.dep_ == 'npadvmod' or token.dep_ == 'advmod':
            clause = ' '.join([tok.orth_ for tok in token.subtree])
            clauses.append(clause)
    return clauses

def generate_alternatives(english):
    nlp = spacy.load("en_core_web_sm")
    sentence = english
    doc = nlp(sentence)
    phrases = []


    #get prepositional phrases and blacklist OPs 
    ROMANCE_en.off_limits = []
    for pphrase in get_pps(doc):
        #messy way to capitalize the first word without lowercasing the others
        capitalized = pphrase.split(' ')[0].capitalize() + ' ' + ' '.join(pphrase.split(' ')[1:])
        phrases.append(capitalized)

    #get noun chunks that aren't OPs
    for chunk in doc.noun_chunks:
        valid = True
        for phr in ROMANCE_en.off_limits:
            if chunk.text in phr:
                valid = False
        if valid:
            capitalized = chunk.text.split(' ')[0].capitalize() + ' ' + ' '.join(chunk.text.split(' ')[1:])
            phrases.append(capitalized)

    #get adverbial modifiers and clauses
    for clause in get_adv_clause(doc):
        capitalized = clause.split(' ')[0].capitalize() + ' ' + ' '.join(clause.split(' ')[1:])
        phrases.append(capitalized)
        
    #get clause beginnings
    wordlist = [t.orth_ for t in doc]
    for token in doc:
        if token.dep_ == 'nsubj':
            mystr = ' '.join([t.orth_ for t in token.lefts]) + token.text + ' ' + token.head.orth_

            phraselist = wordlist[wordlist.index(token.orth_):wordlist.index(token.head.orth_)+1]
            phrases.append(' '.join(phraselist).capitalize())

            wordlist.remove(token.orth_)
        
    print(phrases)

    #prepare input for translation
    ROMANCE_en.original_postprocess = True
    english = ">>es<<" + sentence
    engbatch = en_ROMANCE_tokenizer.prepare_translation_batch([english]).to(device)
    eng_to_spanish = en_ROMANCE.generate(**engbatch).to(device)
    machine_translation = en_ROMANCE_tokenizer.decode(eng_to_spanish[0]).replace("<pad> ", '')

    #generate alternatives starting with each selected phrase
    results = []
    for selection in set(phrases):
        ROMANCE_en_tokenizer.current_spm = ROMANCE_en_tokenizer.spm_target
        tokens = ROMANCE_en_tokenizer.tokenize(selection)
        ROMANCE_en.selected_tokens = ROMANCE_en_tokenizer.convert_tokens_to_ids(tokens)

        ROMANCE_en.original_postprocess = False
        top50 = translate(ROMANCE_en_tokenizer, ROMANCE_en, ">>en<<" + machine_translation, 50)
        for element in top50[0:3]:
            results.append(score_prefix(machine_translation, element))

    #count content words in original and each alternative to catch options that repeat or leave off important phrases
    important_words = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    wordcount = []
    for word in important_words:
        wordcount.append((word, sentence.count(word))) 
    idx = 0
    for score, sen in results:
        resdoc = nlp(sen)
        important = [token.text for token in resdoc if token.is_stop != True and token.is_punct != True]
        if len(important) - len(important_words) not in [-1, 0, 1]:
            results[idx] = (score-10, sen)
        else:
            for el in wordcount:
                if sen.count(el[0]) > el[1]:
                    results[idx] = (score-10, sen)
        idx += 1
        
    #sort results with highest score first                
    all_sorted = sorted(((score, result) for score, result in results), reverse=True)
    print(all_sorted)

    #select prepositional and noun phrases to be highlighted 
    top = nlp(all_sorted[0][1])
    highlight = []
    for pphrase in get_pps(top):
        highlight.append(pphrase)
    for chunk in doc.noun_chunks:
        if chunk.text not in ' '.join(highlight):
            highlight.append(chunk.text)

    color_code_chunks = []
    for score, text in all_sorted:
        if score > -10:
            ph_and_idx = []
            for ph in highlight:
                starting_idx = text.lower().find(ph.lower())
                ph_and_idx.append((ph, starting_idx))

            order = sorted((score, text) for text, score in ph_and_idx)
            ordered_phrases = [phrase for score, phrase in order]
            print(ordered_phrases)

            new_sentence = text
            print(new_sentence)
            final_sentence = []
            x = 0
            for phrase in ordered_phrases:
                if phrase.lower() in text.lower():
                    print(phrase)
                    starting_idx = text.lower().find(phrase.lower())
                    print("test: ",(new_sentence.lower().split(phrase.lower())))

                    final_sentence.append((new_sentence.lower().split(phrase.lower())[0], 0))
                    print(final_sentence)
                    new_sentence = new_sentence.lower().split(phrase.lower())[1]
                    final_sentence.append((phrase, highlight.index(phrase) + 1))
                x += 1
            final_sentence.append((new_sentence, 0))
            color_code_chunks.append(final_sentence)
    
    #messy way to capitalize sentences
    for chunk in color_code_chunks:
        if chunk[0][0] == '':
            first = chunk[1][0]
            capitalized = first.split(' ')[0].capitalize() + ' ' + ' '.join(first.split(' ')[1:])
            chunk[1] = (capitalized, chunk[1][1])
        else:
            first = chunk[0][0]
            capitalized = first.split(' ')[0].capitalize() + ' ' + ' '.join(first.split(' ')[1:])
            chunk[0] = (capitalized, chunk[0][1])

    return {"alternatives" : [result for score, result in all_sorted],
            "scores" : [score for score, result in all_sorted],
            "colorCoding" : color_code_chunks
        }