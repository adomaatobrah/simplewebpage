from flask import Flask, render_template, request, url_for, jsonify, make_response
from flask_cors import CORS
import json
import torch
import math
import wordfreq
from transformers import XLNetTokenizer, XLNetLMHeadModel

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

model = XLNetLMHeadModel.from_pretrained("xlnet-base-cased")
tokenizer = XLNetTokenizer.from_pretrained("xlnet-base-cased")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

PADDING_TEXT = """In 1991, the remains of Russian Tsar Nicholas II and his family
(except for Alexei and Maria) are discovered.
The voice of Nicholas's young son, Tsarevich Alexei Nikolaevich, narrates the
remainder of the story. 1883 Western Siberia,
a young Grigori Rasputin is asked by his father and a group of men to perform magic.
Rasputin has a vision and denounces one of the men as a horse thief. Although his
father initially slaps him for making such an accusation, Rasputin watches as the
man is chased outside and beaten. Twenty years later, Rasputin sees a vision of
the Virgin Mary, prompting him to become a priest. Rasputin quickly becomes famous,
with people, even a bishop, begging for his blessing. <eod> </s> <eos>"""
START_INDEX = 165 # TODO: change hard-coded value

def computeLogProb(original_text, index, tokens_tensor, perm_mask, target_mapping):        
    with torch.no_grad():
        outputs = model(tokens_tensor, perm_mask=perm_mask, target_mapping=target_mapping)
        next_token_logits = outputs[0][0, 0, :]

    preds = [tokenizer.convert_ids_to_tokens(index.item()) for index in next_token_logits.topk(5).indices]
    next_token_logprobs = next_token_logits - next_token_logits.logsumexp(0)
    logProb = next_token_logprobs[tokenizer.convert_tokens_to_ids(original_text[index])].item()

    return (preds, logProb, next_token_logprobs)

def computePredsLogProbs(preds, next_token_logprobs):
    predLogProbs = []
    for i in preds:
        predLogProbs.append(next_token_logprobs[tokenizer.convert_tokens_to_ids(i)].item())
    return predLogProbs

def bigContext(tokenized_text, index):
    encoded_ids = tokenizer.convert_tokens_to_ids(tokenized_text)
    tokens_tensor = torch.tensor([encoded_ids])
    perm_mask = torch.zeros((1, tokens_tensor.shape[1], tokens_tensor.shape[1]), dtype=torch.float)
    perm_mask[:, :, index] = 1.0
    target_mapping = torch.zeros((1, 1, tokens_tensor.shape[1]), dtype=torch.float)
    target_mapping[0, 0, index] = 1.0
    return computeLogProb(tokenized_text, index, tokens_tensor, perm_mask, target_mapping)

def smallContext(tokenized_text, index):
    tokens_tensor = torch.tensor([tokenizer.convert_tokens_to_ids(tokenized_text)])
    perm_mask = torch.zeros((1, tokens_tensor.shape[1], tokens_tensor.shape[1]), dtype=torch.float)
    for i in range(START_INDEX, len(tokenized_text) - 1):
        if i != index - 1 and i != index + 1:
            perm_mask[:, :, i] = 1.0
    target_mapping = torch.zeros((1, 1, tokens_tensor.shape[1]), dtype=torch.float)
    target_mapping[0, 0, index] = 1.0
    return computeLogProb(tokenized_text, index, tokens_tensor, perm_mask, target_mapping)

def noContext(word):
    if word in '.?,:!;\'\"‘’“”|-/\\':
        return -1 # FIXME
    freq = wordfreq.word_frequency(word, 'en')
    if freq == 0:
        print("word not found:", word)
        return -100
    return math.log(freq)

def compute_scores(input_text):
    tokenized_text = tokenizer.tokenize(PADDING_TEXT + " " + input_text + "</s>", add_special_tokens=False, return_tensors='pt')

    usedModels = ["bigContext", "smallContext", "noContext"]
    results = []
    compoundBigPreds = []
    compoundSmallPreds = []
    compoundBigLogProb = 0
    compoundSmallLogProb = 0
    currentWord = ""
    resultID = 0

    # For each token not in PADDING_TEXT
    for i in range(START_INDEX, len(tokenized_text) - 1):
        # Compute the top 5 model predictions, the log probability of the
        #   correct answer, and the next_token_logprobs
        bigPreds, bigLogProb, bigNextLogProbs = bigContext(tokenized_text, i)
        smallPreds, smallLogProb, smallNextLogProbs = smallContext(tokenized_text, i)

        # Generate the log probabilities of the top 5 small model predictions
        #   given big context vs. small context
        bigPredsLogProbs = computePredsLogProbs(smallPreds, bigNextLogProbs)
        smallPredsLogProbs = computePredsLogProbs(smallPreds, smallNextLogProbs)

        # if the current token is a start token
        if tokenized_text[i].startswith("▁"):
            compoundBigLogProb = bigLogProb
            compoundSmallLogProb = smallLogProb
            compoundBigPreds = bigPreds
            compoundSmallPreds = smallPreds
            currentWord = tokenized_text[i]
        # If the current token is a continuation token
        else:
            compoundBigLogProb += bigLogProb
            compoundSmallLogProb += smallLogProb
            currentWord += tokenized_text[i]
        
        # if the next token is not a start token or the end of sequence, don't do any more work
        #   because that means the next token is a continuation token
        if not (tokenized_text[i + 1].startswith("▁") or tokenized_text[i + 1] == "</s>"):
            continue
            
        currentWord = currentWord.replace("▁", "")
        
        # Compute the no-context log probabilities of the current word and
        #   the predictions generated by the small context model
        noContextLogProb = noContext(currentWord)
        noPredsLogProbs = []
        for j in smallPreds:
            processed_word = j.replace("▁", "")
            noPredsLogProbs.append(noContext(processed_word))

        results.append(dict(
            id = resultID,
            word=currentWord,
            src="original",
            model="smallContext",
            score=compoundSmallLogProb)
        )
        
        results.append(dict(
            id = resultID,
            word=currentWord,
            src="original",
            model="bigContext",
            score=compoundBigLogProb)
        )

        results.append(dict(
            id = resultID,
            word=currentWord,
            src="original",
            model="noContext",
            score=noContextLogProb)
        )

        for j in range(0, len(smallPreds)):
            results.append(dict(
                id = resultID,
                word=smallPreds[j],
                src="smallContext",
                model="smallContext",
                score=smallPredsLogProbs[j])
            )

            results.append(dict(
                id = resultID,
                word=smallPreds[j],
                src="smallContext",
                model="bigContext",
                score=bigPredsLogProbs[j])
            )
            
            results.append(dict(
                id = resultID,
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
        resultID += 1

    return (results, usedModels)

@app.route('/')
def form():
    return render_template("home.html")

@app.route('/', methods=['POST'])
def result():
    data = request.get_json()
    text = data["text"]

    results, usedModels = compute_scores(text)
        
    return {
        'results': results,
        'usedModels': usedModels
    }