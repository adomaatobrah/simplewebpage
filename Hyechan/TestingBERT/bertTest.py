import torch
from transformers import BertTokenizer, BertModel

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

prompt_text = input("Input something: ")
encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
num = int(input("How deep to search? "))

prediction_scores, past = model.forward(encoded_prompt)
print([tokenizer.decode(index.item()) for index in prediction_scores[0, -1].topk(num).indices])