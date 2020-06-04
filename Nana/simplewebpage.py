from flask import Flask, render_template, request
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

app = Flask(__name__)

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')


@app.route('/')
def form():
    return render_template("home.html")
@app.route('/', methods=["GET"])
def result():


	prompt_text = request.form["x"]
	#return prompt_text
	encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")

	num = int(request.form["Num"])
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
	    

	    if encoded_prompt[0, element_pos+1] in prediction_list:
	        predictability_rank = prediction_list.index(encoded_prompt[0, element_pos+1])
	        predictability += 1 - predictability_rank / vocab_size
	    
	    	if predictability >=0.8 in decoded_prediction_list:
	    		High_match = word in decoded_prediction_list

	    	elif predictability <0.8>=0.5 in decoded_prediction_list:
	    		Medium_match = word in decoded_prediction_list

	    	else:
	    		Low_match = word in decoded_prediction_lists

	    	return decoded_prediction_list

	    element_pos += 1

	    
	

	# return ("The predictability score for " + str(prompt_text) + " is: " + str(predictability/(encoded_prompt.numel()-1)))
	
	return render_template("home.html")