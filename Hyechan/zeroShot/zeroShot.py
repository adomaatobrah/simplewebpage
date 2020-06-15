import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

prompt_text = """
It was a dark and stormy night.
Dark black crows fluttered from dead tree branch to dead tree branch.
Note: The weather is stormy.

The breeze was nice, the sun was shining.
A green turtle lazily swam across the surf.
Note:
"""

for i in range(0, 10):
    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    prediction_scores, past = model.forward(encoded_prompt)
    next_word = tokenizer.decode(prediction_scores[0, -1].topk(1).indices[0].item())
    prompt_text += next_word

print(prompt_text)