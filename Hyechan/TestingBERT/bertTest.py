import torch
from transformers import BertTokenizer, BertForMaskedLM

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create some prompt text with appropriate tags
prompt_text = input("Please input something (2 sentences max): ")
# List of punctuation to determine where segments end
punc_list = [".", "?", "!"]
# Prepend the [CLS] tag
prompt_text = "[CLS] " + prompt_text
# Insert the [SEP] tags
for i in range(0, len(prompt_text)):
    if prompt_text[i] in punc_list:
        prompt_text = prompt_text[:i + 1] + " [SEP]" + prompt_text[i + 1:]
        
# Tokenize the text so the model can understand it
tokenized_text = tokenizer.tokenize(prompt_text)
# Assign segment ids
currentSeg = 0
segments_ids = []
for token in tokenized_text:
    segments_ids.append(currentSeg)
    if token == "[SEP]":
        currentSeg += 1
# Print the tokenized text so I can read it and confirm the tokenization
print(tokenized_text)
# Print the segment ids so I can confirm them too
print(segments_ids)

# Mask one of the words (so that BERT has to guess what it is)
masked_word = input("What token do you want to [MASK]? ")
masked_word.lower()
# List to hold indices of masked words
mask_indices = []
for i in range(0, len(tokenized_text)):
    if tokenized_text[i] == masked_word:
        tokenized_text[i] = "[MASK]"
        mask_indices.append(i)
print(tokenized_text)

# Convert tokens to vocab ids (for the model to understand)
indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)

# Convert inputs to tensors
tokens_tensor = torch.tensor([indexed_tokens])
segments_tensor = torch.tensor([segments_ids])

# invoke the no_grad function, which is necessary for the model
#   (although I still don't know why)
with torch.no_grad():
    # Get the model outputs
    outputs = model(tokens_tensor, token_type_ids=segments_tensor)
    # The first item in the output will be the "layer" with the predictions
    predictions = outputs[0]

# Get the prediction for the mask
# This is a fairly dense statement, so here's what it's doing:
#   for the top 10 indices in the predictions tensor corresponding to each instance of the masked word:
#       Convert the id of the element in that index to a token
#           Confusing thing for me: what's that [0] doing there?
#       Once that id has been converted, append it to a list
for i in mask_indices:
    predicted_outputs = [tokenizer.convert_ids_to_tokens([index.item()])[0] for index in predictions[0, i].topk(10).indices]
    # Print out the list of predicted outputs
    print(predicted_outputs)