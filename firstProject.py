import torch
from transformers import *

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

prompt_text = input("Input something: ")
encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")

num = int(input("How deep to search? "))

prediction_scores, past = model.forward(encoded_prompt)

prediction_scores.shape

score = 0;
next_pos = 1;
print("The given sentence was: " + prompt_text + "\n")
for word in prediction_scores[0]:
    if next_pos >= len(encoded_prompt[0]):
        break
    
    checklist = [index.item() for index in word.topk(num).indices]
    results = [tokenizer.decode(index.item()) for index in word.topk(num).indices]
    print(results)
    
    if encoded_prompt[0, next_pos] in word.topk(num).indices:
        listpos = checklist.index(encoded_prompt[0, next_pos])
        print(listpos)
        print("\n----- \'" + tokenizer.decode(encoded_prompt[0, next_pos].item()) + "\' found in top " + str(num) + " results -----\n")
        score = score + ((50257 - listpos)/50257)
    else:
        print("\n----- \'" + tokenizer.decode(encoded_prompt[0, next_pos].item()) + "\' not found in top " + str(num) + " results -----\n")
        
    next_pos = next_pos + 1
    
print("The predictability score for the top " + str(num) + " results is: " + str(score / (len(encoded_prompt[0]) - 1)))