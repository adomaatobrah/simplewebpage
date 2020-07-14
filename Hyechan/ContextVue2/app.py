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
CORS(app, resources={r'/*': {'origins': '*'}})

jinja_options = app.jinja_options.copy()

jinja_options.update(dict(
    block_start_string='<%',
    block_end_string='%>',
    variable_start_string='%%',
    variable_end_string='%%',
    comment_start_string='<#',
    comment_end_string='#>'
))
app.jinja_options = jinja_options

model = BertForMaskedLM.from_pretrained("bert-base-cased")
tokenizer = BertTokenizer.from_pretrained("bert-base-cased")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def computeLogProb(masked_text, original_text, index):
    indexed_tokens = tokenizer.convert_tokens_to_ids(masked_text)
    tokens_tensor = torch.tensor([indexed_tokens])
        
    with torch.no_grad():
        outputs = model(tokens_tensor)
        next_token_logits = outputs[0][0, index, :]

    preds = [tokenizer.convert_ids_to_tokens(index.item()) for index in next_token_logits.topk(5).indices]
    next_token_logprobs = next_token_logits - next_token_logits.logsumexp(0)
    logProb = next_token_logprobs[tokenizer.convert_tokens_to_ids(original_text[index])].item()

    return (preds, logProb, next_token_logprobs)

def computePredsLogProbs(preds, next_token_logprobs):
    predLogProbs = []
    for i in preds:
        predLogProbs.append(next_token_logprobs[tokenizer.convert_tokens_to_ids(i)].item())
        print(i)
        print(predLogProbs)
    return predLogProbs

def bigContext(tokenized_text, index):
    text = tokenized_text.copy()
    text[index] = "[MASK]"
    return computeLogProb(text, tokenized_text, index)

def smallContext(tokenized_text, index):
    text = tokenized_text.copy()
    for i in range(1, len(text) - 1):
        if i != index - 1 and i != index + 1:
            text[i] = "[MASK]"
    return computeLogProb(text, tokenized_text, index)

def noContext(word):
    if word in '.?,:!;\'\"‘’“”|-/\\':
        return -1 # FIXME
    freq = wordfreq.word_frequency(word, 'en')
    if freq == 0:
        print("word not found:", word)
        return -100
    return math.log(freq)

def compute_scores(input_text):
    # Prepend and append tags and tokenize text
    prepped_text = "[CLS] " + input_text + " [SEP]"
    tokenized_text = tokenizer.tokenize(prepped_text)

    usedModels = ["bigContext", "smallContext", "noContext"]
    results = []
    compoundBigPreds = []
    compoundSmallPreds = []
    compoundBigLogProb = 0
    compoundSmallLogProb = 0
    currentWord = ""

    # For each token
    for i in range(1, len(tokenized_text) - 1):
        # Compute the top 5 model predictions, the log probability of the
        #   correct answer, and the next_token_logprobs
        bigPreds, bigLogProb, bigNextLogProbs = bigContext(tokenized_text, i)
        smallPreds, smallLogProb, smallNextLogProbs = smallContext(tokenized_text, i)

        # Generate the log probabilities of the top 5 small model predictions
        #   given big context vs. small context
        bigPredsLogProbs = computePredsLogProbs(smallPreds, bigNextLogProbs)
        smallPredsLogProbs = computePredsLogProbs(smallPreds, smallNextLogProbs)

        # If the immediate next token is a continuation of the current one,
        #   add its log probability to a compound logProb and concatenate
        #   the token to the currentWord string, then return control to the
        #   beginning of the loop
        if tokenized_text[i + 1].startswith("##"):
            compoundBigLogProb += bigLogProb
            compoundSmallLogProb += smallLogProb
            compoundBigPreds = bigPreds
            compoundSmallPreds = smallPreds
            currentWord += tokenized_text[i]
            continue
        # If either the compound large-context logprob or the compound
        #   small-context logprob is not equal to zero (i.e. they currently
        #   hold the value of an incomplete multi-token word), add the final
        #   token's logprob and concatenate it to currentWord
        if compoundBigLogProb != 0 or compoundSmallLogProb != 0:
            compoundBigLogProb += bigLogProb
            compoundSmallLogProb += smallLogProb
            currentWord += tokenized_text[i]
            currentWord = currentWord.replace("##", "")
        # If the next token does not start with "##" and the current token is
        #   not part of a multi-token word, simply assign the predictions and
        #   log probabilities
        else:
            compoundBigLogProb = bigLogProb
            compoundSmallLogProb = smallLogProb
            compoundBigPreds = bigPreds
            compoundSmallPreds = smallPreds
            currentWord = tokenized_text[i]
        
        # Compute the no-context log probabilities of the current word and
        #   the predictions generated by the small context model
        noContextLogProb = noContext(currentWord)
        noPredsLogProbs = []
        for j in smallPreds:
            noPredsLogProbs.append(noContext(j))

        results.append(dict(
            id = i - 1,
            word=currentWord,
            src="original",
            model="smallContext",
            score=compoundSmallLogProb)
        )
        
        results.append(dict(
            id = i - 1,
            word=currentWord,
            src="original",
            model="bigContext",
            score=compoundBigLogProb)
        )

        results.append(dict(
            id = i - 1,
            word=currentWord,
            src="original",
            model="noContext",
            score=noContextLogProb)
        )

        for j in range(0, len(smallPreds)):
            results.append(dict(
                id = i - 1,
                word=smallPreds[j],
                src="smallContext",
                model="smallContext",
                score=smallPredsLogProbs[j])
            )

            results.append(dict(
                id = i - 1,
                word=smallPreds[j],
                src="smallContext",
                model="bigContext",
                score=bigPredsLogProbs[j])
            )
            
            results.append(dict(
                id = i - 1,
                word=smallPreds[j],
                src="smallContext",
                model="noContext",
                score=noPredsLogProbs[j])
            )
        
        compoundBigLogProb = 0
        compoundSmallLogProb = 0
        compoundBigPreds = []
        compoundSmallPreds = []
        currentWord = ""

    return (results, usedModels)

@app.route('/')
def form():
    return render_template("home.html")

@app.route('/', methods=['POST'])
def result():
    data = request.get_json()
    text = data["text"]

    print(text)
    results, usedModels = compute_scores(text)
    print(results)
        
    return {
        'results': results,
        'usedModels': usedModels
    }