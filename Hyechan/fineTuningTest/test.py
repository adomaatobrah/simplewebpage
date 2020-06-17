from transformers import TokenClassificationPipeline, pipeline
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "./wnut-17-model-1"

nlp = pipeline(
    "ner",
    model=MODEL_PATH,
    tokenizer=MODEL_PATH,
)

print(nlp("Apple developed an apple charger that uses apples to power the Apple phone."))
