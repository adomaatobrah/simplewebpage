#from flask import Flask, render_template, request
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

#app = Flask(__name__)

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')


#@app.route('/')
#def form():
#    return render_template("home.html")

#@app.route('/result')
#def result():

prompt_text = input("x: ")
encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")

num = int(input("Number of characters: "))
prediction_scores, past = model.forward(encoded_prompt)

size, words_input, vocab_size = prediction_scores.shape

assert vocab_size == 50257
element_pos= 0
predictability = 0
decoded_prediction_list = []
prediction_str = ""

for word in range (0, encoded_prompt.numel()-1):
    prediction_list = [(index.item()) for index in prediction_scores[0, element_pos].topk(num).indices]
    decoded_prediction_list=[tokenizer.decode(index.item()) for index in prediction_scores[0, element_pos].topk(num).indices]
    print(decoded_prediction_list)

    if encoded_prompt[0, element_pos+1] in prediction_list:
        predictability_rank = prediction_list.index(encoded_prompt[0, element_pos+1])
        predictability += 1 - predictability_rank / vocab_size
        
    element_pos += 1

    
    

print("The predictability score for " + str(num) + " is: " + str(predictability/(encoded_prompt.numel()-1)))