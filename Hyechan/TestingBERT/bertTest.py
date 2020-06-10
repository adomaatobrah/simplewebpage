import torch
from transformers import BertTokenizer, BertForMaskedLM

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create some prompt text with appropriate tags
prompt_text = "[CLS] Where is the remote? [SEP] It is under the couch. [SEP]"
# Tokenize the text so the model can understand it
tokenized_text = tokenizer.tokenize(prompt_text)
# Print the tokenized text so I can read it and confirm the tokenization
print(tokenized_text)

# Mask one of the words (so that BERT has to guess what it is)
masked_index = 9
tokenized_text[masked_index] = "[MASK]"
print(tokenized_text)

# Convert tokens to vocab ids (for the model to understand)
indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
# Define sentence indices
segments_ids = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]

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
#   for the top 10 indices in the predictions tensor corresponding to the masked word:
#       Convert the id of the element in that index to a token
#           Confusing thing for me: what's that [0] doing there?
#       Once that id has been converted, append it to a list
predicted_outputs = [tokenizer.convert_ids_to_tokens([index.item()])[0] for index in predictions[0, masked_index].topk(10).indices]
# Print out the list of predicted outputs
print(predicted_outputs)