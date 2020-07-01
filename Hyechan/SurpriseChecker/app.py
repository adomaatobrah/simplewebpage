from flask import Flask, render_template, request, url_for, jsonify, make_response
from flask_cors import CORS
import json
import torch
import wordfreq
from transformers import BertTokenizer, BertForMaskedLM

app = Flask(__name__)

# https://stackoverflow.com/questions/37575089/disable-template-cache-jinja2
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

tokenizer = GPT2Tokenizer.from_pretrained('bert-base-multilingual-cased')
model = GPT2LMHeadModel.from_pretrained('bert-base-multilingual-cased')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def prepareInputs(init_text):
    # List of punctuation to determine where segments end
    punc_list = [".", "?", "!"]
    # Prepend the [CLS] tag
    prompt_text = "[CLS] " + init_text
    # Insert the [SEP] tags
    for i in range(0, len(prompt_text)):
        if prompt_text[i] in punc_list:
            prompt_text = prompt_text[:i + 1] + " [SEP]" + prompt_text[i + 1:]

    return prompt_text

def createSegIDs(tokenized_text):
    currentSeg = 0
    seg_ids = []
    for token in tokenized_text:
        seg_ids.append(currentSeg)
        if token == "[SEP]":
            currentSeg += 1

    return seg_ids

def addMask(unmasked_tokenized_text, mask_word):
    tokenized_text = unmasked_tokenized_text
    mask_indices = []
    for i in range(0, len(tokenized_text)):
        if tokenized_text[i] == mask_word:
            tokenized_text[i] = "[MASK]"
            mask_indices.append(i)

    return (tokenized_text, mask_indices)

@app.route('/')
def form():
    text = "es un árbol hermoso."
    prepped_text = prepareInputs(text)
    tokenized_text = tokenizer.tokenize(prepped_text)
    segment_ids = createSegIDs(tokenized_text)
    word_to_mask = "árbol"
    masked_text, mask_indices = addMask(tokenized_text, word_to_mask)

    indexed_tokens = tokenizer.convert_tokens_to_ids(masked_text)
    masked_token_id = tokenizer.convert_tokens_to_ids(word_to_mask)

    tokens_tensor = torch.tensor([indexed_tokens])
    segment_tensor = torch.tensor([segment_ids])

    with torch.no_grad():
        outputs = model(tokens_tensor, token_type_ids=segment_tensor)
        prediction_scores = outputs[0]

    for i in mask_indices:
        next_token_logits = prediction_scores[0, i, :]
        prob = torch.softmax(next_token_logits, 0)[masked_token_id]
        
    return {
        'surprise_score': prob
    }