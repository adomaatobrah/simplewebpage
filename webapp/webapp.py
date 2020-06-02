from flask import Flask, render_template, request
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
app = Flask(__name__)

@app.route('/')
def form():
     return """
         <html><body>
             <h2>text predictability</h2>
             <form action="/result">
                 Text: <input type='text' name='text'><br><br>
                 <input type='submit' value='Continue'>
             </form>
         </body></html>
        """

@app.route('/result')
def result():
    prompt_text = request.args.get('text')
    #return render_template("home.html")

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    num_results = 10

    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)

    num = 0
    predictability = 0
    for x in range(0, encoded_prompt.numel()-1):
        prediction_list = [(index.item()) for index in prediction_scores[0, num].topk(num_results).indices]
        print([tokenizer.decode(index.item()) for index in prediction_scores[0, num].topk(num_results).indices])
    
        if encoded_prompt[0, num+1] in prediction_list:
            predictability = predictability + ((50257 - prediction_list.index(encoded_prompt[0, num+1]))/50257)
        
        num += 1
    
    return "Predictability score for \"" + prompt_text + "\": " + str(predictability/(encoded_prompt.numel()-1))