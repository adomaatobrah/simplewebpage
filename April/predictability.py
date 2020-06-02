import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

prompt_text = input("text: ")
num_results = int(input("num results: "))

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
    
print(predictability/(encoded_prompt.numel()-1))