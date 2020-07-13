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

tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
model = BertForMaskedLM.from_pretrained('bert-base-multilingual-cased')
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

def addMask(tokenized_text, mask_word):
    mask_word_tokens = tokenizer.tokenize(mask_word)
    mask_indices = []
    for i in range(0, len(tokenized_text)):
        if tokenized_text[i] in mask_word_tokens:
            tokenized_text[i] = "[MASK]"
            mask_indices.append(i)

    return (tokenized_text, mask_indices)

def compute_model_score(text, word_to_mask):
    # Preparing input and segments
    prepped_text = prepareInputs(text)
    tokenized_text = tokenizer.tokenize(prepped_text)
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    segment_ids = createSegIDs(tokenized_text)

    # Masking
    masked_text, mask_indices = addMask(tokenized_text, word_to_mask)
    indexed_masked_tokens = tokenizer.convert_tokens_to_ids(masked_text)

    # Mutable result variables
    totalPreds = []
    totalProbs = []
    nextSentences = []

    getPreds(indexed_tokens,
             indexed_masked_tokens,
             masked_text, segment_ids,
             mask_indices,
             totalPreds,
             totalProbs,
             nextSentences,
             0)
    
    return (totalPreds, totalProbs, nextSentences)

def getSinglePred(indexed_tokens, indexed_masked_tokens, segment_ids, mask_index):
    tokens_tensor = torch.tensor([indexed_masked_tokens])
    segment_tensor = torch.tensor([segment_ids])

    with torch.no_grad():
        outputs = model(tokens_tensor, token_type_ids=segment_tensor)
        prediction_scores = outputs[0]

    next_token_logits = prediction_scores[0, mask_index, :]
    preds = ([tokenizer.convert_ids_to_tokens(index.item()) for index in next_token_logits.topk(5).indices])
    prob = torch.softmax(next_token_logits, 0)[indexed_tokens[mask_index]].item()

    return (preds, prob)

def getPreds(indexed_tokens,
             indexed_masked_tokens,
             masked_text,
             segment_ids,
             mask_indices,
             totalPreds,
             totalProbs,
             nextSentences,
             index):
    preds, prob = getSinglePred(indexed_tokens, indexed_masked_tokens, segment_ids, mask_indices[index])
    totalPreds.append(preds)
    totalProbs.append(prob)

    for next_word in preds:
        masked_text[mask_indices[index]] = next_word
        indexed_masked_tokens = tokenizer.convert_tokens_to_ids(masked_text)
        if (index == len(mask_indices) - 1):
            result = [indexed_masked_tokens[i] for i in mask_indices]
            nextSentences.append(tokenizer.decode(result))
        else:
            getPreds(indexed_tokens,
                        indexed_masked_tokens,
                        masked_text,
                        segment_ids,
                        mask_indices,
                        totalPreds,
                        totalProbs,
                        nextSentences,
                        index + 1)

def compute_wordfreq_score(masked_word, lang):
    freqs = wordfreq.get_frequency_dict(lang)
    return freqs[masked_word]

@app.route('/')
def form():
    return render_template("home.html")

@app.route('/', methods=['POST'])
def result():
    data = request.get_json()
    text = data["text"]
    word_to_mask = data["mask"]

    preds, probs, sentences = compute_model_score(text, word_to_mask)
        
    return {
        'model_score': probs,
        'predictions': preds,
        'sentences': sentences,
        'wordfreq_score': compute_wordfreq_score(word_to_mask, 'es')
    }