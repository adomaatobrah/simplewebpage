from transformers import TokenClassificationPipeline, pipeline
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "./models/speakVerbsTestModel30100"

nlp = pipeline(
    "ner",
    model=MODEL_PATH,
    tokenizer=MODEL_PATH,
)

test_list = [
    "'Don't do it!' I said.",
    "'But soft! What light through yonder window breaks?' said I.",
    "Stephanie cried, 'No! This cannot be!'",
    "'What's the matter?' I asked.",
    "She screamed, 'I don't want to die!'",
    "'Go back to the slums, loser!' he hooted.",
    "'Frankly, my dear,' he crooned, 'I don't give a damn.'",
    "'Stop it...' she mumbled. 'Please...'",
    "After a stunned silence, Joey yelled, 'It wasn't me!'",
    "'Going about our daily lives is quite useless,' she groaned.",
    "When all's said and done, I think we did well.",
    "He said he'd be fine, and I told him he was crazy.",
    "He never answered the phone.",
    "What was she saying?",
    "I've cried out to the Lord.",
    "I have no mouth and I wish to scream.",
    "She has lied to this court!",
    "I'm here! You hollered?",
    "Forget it! I'll never spill the secrets!",
    "Howdy. I heard someone shrieking up in these parts."
]

for a_str in test_list:
    print(nlp(a_str))
