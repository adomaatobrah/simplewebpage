from transformers import TokenClassificationPipeline, pipeline
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "./speakVerbsTestModel"

nlp = pipeline(
    "ner",
    model=MODEL_PATH,
    tokenizer=MODEL_PATH,
)

print(nlp("I said, 'Tyler said he wasn't fine.' She yelled, 'I told you to not worry about it.' 'Have it your way,' I groaned."))
