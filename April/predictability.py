{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import torch\n",
    "from transformers import GPT2Tokenizer, GPT2LMHeadModel\n",
    "\n",
    "tokenizer = GPT2Tokenizer.from_pretrained('gpt2')\n",
    "model = GPT2LMHeadModel.from_pretrained('gpt2')\n",
    "\n",
    "prompt_text = input(\"text: \")\n",
    "num_results = int(input(\"num results: \"))\n",
    "\n",
    "encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors=\"pt\")\n",
    "prediction_scores, past = model.forward(encoded_prompt)\n",
    "\n",
    "num = 0\n",
    "predictability = 0\n",
    "for x in range(0, encoded_prompt.numel()-1):\n",
    "    prediction_list = [(index.item()) for index in prediction_scores[0, num].topk(num_results).indices]\n",
    "    print([tokenizer.decode(index.item()) for index in prediction_scores[0, num].topk(num_results).indices])\n",
    "    \n",
    "    if encoded_prompt[0, num+1] in prediction_list:\n",
    "        predictability = predictability + ((50257 - prediction_list.index(encoded_prompt[0, num+1]))/50257)\n",
    "        \n",
    "    num += 1\n",
    "    \n",
    "print(predictability/(encoded_prompt.numel()-1))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
