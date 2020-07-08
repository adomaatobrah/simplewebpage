from flask import Flask, render_template, request, url_for, jsonify, make_response
from flask_cors import CORS
import json
import torch
import math
import wordfreq
from transformers import BertTokenizer, BertForMaskedLM

app = Flask(__name__)

# https://stackoverflow.com/questions/37575089/disable-template-cache-jinja2
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

model = BertForMaskedLM.from_pretrained("bert-base-cased")
tokenizer = BertTokenizer.from_pretrained("bert-base-cased")
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
        elif i == len(prompt_text) - 1 and prompt_text[i] not in punc_list:
            prompt_text += " [SEP]"

    return prompt_text

def createSegIDs(tokenized_text):
    currentSeg = 0
    seg_ids = []
    for token in tokenized_text:
        seg_ids.append(currentSeg)
        if token == "[SEP]":
            currentSeg += 1

    return seg_ids

def computeLogProb(masked_text, original_text, segment_ids, index):
    indexed_tokens = tokenizer.convert_tokens_to_ids(masked_text)
    tokens_tensor = torch.tensor([indexed_tokens])
    segment_tensor = torch.tensor([segment_ids])
        
    with torch.no_grad():
        outputs = model(tokens_tensor, token_type_ids=segment_tensor)
        next_token_logits = outputs[0][0, index, :]

    preds = [tokenizer.convert_ids_to_tokens(index.item()) for index in next_token_logits.topk(5).indices]
    next_token_logprobs = next_token_logits - next_token_logits.logsumexp(0)
    logProb = next_token_logprobs[tokenizer.convert_tokens_to_ids(original_text[index])].item()

    return (preds, logProb)

def bigContext(tokenized_text, segment_ids, index):
    text = tokenized_text.copy()
    text[index] = "[MASK]"
    return computeLogProb(text, tokenized_text, segment_ids, index)

def smallContext(tokenized_text, segment_ids, index):
    text = tokenized_text.copy()
    for i in range(1, len(text) - 1):
        if i != index - 1 and i != index + 1:
            text[i] = "[MASK]"
    return computeLogProb(text, tokenized_text, segment_ids, index)

def noContext(word):
    if word in '.?,:!;\'\"‘’“”':
        return -1 # FIXME
    freq = wordfreq.word_frequency(word, 'en')
    if freq == 0:
        print("word not found:", word)
        return -100
    return math.log(freq)

def compute_ratios(input_text):
    prepped_text = prepareInputs(input_text)
    tokenized_text = tokenizer.tokenize(prepped_text)

    print(tokenized_text)

    segment_ids = createSegIDs(tokenized_text)

    results = []
    compoundBigPreds = []
    compoundSmallPreds = []
    compoundBigLogProb = 0
    compoundSmallLogProb = 0
    currentWord = ""

    for i in range(1, len(tokenized_text) - 1):
        bigPreds, bigLogProb = bigContext(tokenized_text, segment_ids, i)
        smallPreds, smallLogProb = smallContext(tokenized_text, segment_ids, i)

        if tokenized_text[i + 1].startswith("##"):
            compoundBigLogProb += bigLogProb
            compoundSmallLogProb += smallLogProb
            compoundBigPreds = bigPreds
            compoundSmallPreds = smallPreds
            currentWord += tokenized_text[i]
            continue
        elif compoundBigLogProb != 0 or compoundSmallLogProb != 0:
            compoundBigLogProb += bigLogProb
            compoundSmallLogProb += smallLogProb
            currentWord += tokenized_text[i]
            currentWord = currentWord.replace("##", "")
        else:
            compoundBigLogProb = bigLogProb
            compoundSmallLogProb = smallLogProb
            compoundBigPreds = bigPreds
            compoundSmallPreds = smallPreds
            currentWord = tokenized_text[i]
        
        noContextLogProb = noContext(currentWord)

        if tokenized_text[i + 1] not in "[SEP]":
            currentWord += " "

        # High ratio = knowing more words helped prediction a lot
        results.append(dict(
            word=currentWord,
            bigContextLogProb=compoundBigLogProb,
            smallContextLogProb=compoundSmallLogProb,
            noContextLogProb=noContextLogProb,
            bigContextPreds = compoundBigPreds,
            smallContextPreds = compoundSmallPreds))
        
        compoundBigLogProb = 0
        compoundSmallLogProb = 0
        compoundBigPreds = []
        compoundSmallPreds = []
        currentWord = ""

    return results

@app.route('/')
def form():
    return render_template("home.html")

@app.route('/', methods=['POST'])
def result():
    data = request.get_json()
    text = data["text"]

    print(text)
    results = compute_ratios(text)
        
    return {
        'results': results,
    }