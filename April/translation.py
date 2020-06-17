import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config

model = T5ForConditionalGeneration.from_pretrained("t5-base")
tokenizer = T5Tokenizer.from_pretrained("t5-base")

words = []

input_ids = tokenizer.encode("translate English to German: When Liana Barrientos was 23 years old, she got married in Westchester County.", return_tensors="pt")
translation = 'Liana Barrientos heiratete sie in Westchester County als 23 Jahre alt war.'

outputs = model.generate(input_ids, max_length=40, num_beams=4, early_stopping=True)
machine_translation = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in outputs]
output_ids = tokenizer.encode(translation, return_tensors='pt')

lm_labels = tokenizer.encode(translation, return_tensors='pt')
outputs2 = model(input_ids=input_ids, lm_labels=lm_labels)

loss, prediction_scores = outputs2[:2]

all_predictions = []
next_pos = 0

for word in prediction_scores[0]:
    predicted_words = word.topk(5).indices
    next_word = output_ids[0, next_pos]
    predicted_words_list = []

    for index in predicted_words:
        predicted_words_list.append(tokenizer.decode(index.item()))
    all_predictions.append((tokenizer.decode(next_word.item()), predicted_words_list))
    next_pos += 1


print(all_predictions)
print(translation)



