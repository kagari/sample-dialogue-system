import os
from abc import ABC
from typing import (
    Optional,
    List,
)

import torch
from transformers import (
    T5Tokenizer,
    AutoModelForCausalLM,
)

class BaseAgent(ABC):
    def __init__(self, name) -> None:
        self.name = name

    def reply(self, s: List[str]) -> str:
        pass


class EchoAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("Echo")

    def reply(self, s: List[str]) -> str:
        return '</s>'.join(s)


class DialoGPTAgent(BaseAgent):
    def __init__(self, model_path: str):
        super().__init__("DialoGPT")
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
        self.tokenizer.do_lower_case = True  # due to some bug of tokenizer config loading
        self.model = AutoModelForCausalLM.from_pretrained(model_path)

    def reply(self, s: List[str]) -> str:
        if not s.startswith(self.tokenizer.bos_token):
            s = self.tokenizer.bos_token + s
        if not s.endswith(self.tokenizer.sep_token):
            s += self.tokenizer.sep_token
        input_ids = self.tokenizer(s, return_tensors="pt")["input_ids"]
        output_sequences = self.model.generate(
            input_ids=input_ids, top_p=0.95, top_k=50, do_sample=True,
            max_length=128+input_ids.size(1), bos_token_id=self.tokenizer.bos_token_id,
            eos_token_id=self.tokenizer.eos_token_id, pad_token_id=self.tokenizer.pad_token_id,
            bad_words_ids=[[self.tokenizer.unk_token_id]]
        )
        generated = output_sequences.tolist()[0]
        generated = self.tokenizer.decode(generated)
        _, rep = generated.replace(' ', '').replace('<s>', '').replace('</s>', '').split('[SEP]')
        return rep

class GPT2Agent(BaseAgent):
    def __init__(self, model_name: str, model_checkpoint: Optional[str] = None, tokenizer_checkpoint: Optional[str] = None):
        super().__init__("GPT2")
        if tokenizer_checkpoint is not None:
            self.tokenizer = T5Tokenizer.from_pretrained(tokenizer_checkpoint)
        else:
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.tokenizer.do_lower_case = True  # due to some bug of tokenizer config loading
        self.model = self.__load_model(
            AutoModelForCausalLM.from_pretrained(model_name),
            model_checkpoint,
        )

    def reply(self, s: List[str]) -> str:
        max_length: int = 128
        top_p = 0.99
        top_k = 10
        s = self.tokenizer.eos_token.join(s)
        if not s.startswith(self.tokenizer.bos_token):
            s = self.tokenizer.bos_token + s
        if not s.endswith(self.tokenizer.sep_token):
            s += self.tokenizer.sep_token
        input_ids = self.tokenizer(s, return_tensors="pt")["input_ids"]
        output_sequences = self.model.generate(
            input_ids=input_ids,
            top_p=top_p,
            top_k=top_k,
            do_sample=True,
            max_length=max_length+input_ids.size(1),
            bos_token_id=self.tokenizer.bos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id,
            bad_words_ids=[[self.tokenizer.unk_token_id]]
        )
        generated = output_sequences.tolist()[0]
        generated = self.tokenizer.decode(generated)
        _, rep = generated.replace(' ', '').replace('<s>', '').replace('</s>', '').split('[SEP]')
        return rep
    
    def __load_model(self, model: str, checkpoint: Optional[str] = None):
        """https://github.com/microsoft/DialoGPT/blob/457835e7d8acd08acf7f6f0e980f36fd327ea37c/gpt2_training/train_utils.py#L18
        """
        if checkpoint is not None:
            if not os.path.exists(checkpoint):
                raise ValueError('checkpoint %s not exist' % checkpoint)
            model_state_dict = torch.load(checkpoint, map_location=torch.device('cpu'))

            model_state_dict = self.__fix_state_dict_namespace(model_state_dict)

            start_model = model
            if (hasattr(model, "transformer")
                and all(not s.startswith('transformer.')
                        for s in model_state_dict.keys())):
                print('loading transfomer only')
                start_model = model.transformer
            start_model.load_state_dict(model_state_dict, strict=False)
        return model

    def __fix_state_dict_namespace(self, model_state_dict: dict):
        """https://github.com/microsoft/DialoGPT/blob/457835e7d8acd08acf7f6f0e980f36fd327ea37c/gpt2_training/train_utils.py#L51
        """
        old_keys = []
        new_keys = []
        for t in model_state_dict:
            new_key = t
            if t.startswith('module.'):
                new_key = t.replace('module.', '')
            old_keys.append(t)
            new_keys.append(new_key)

        for old_key, new_key in zip(old_keys, new_keys):
            model_state_dict[new_key] = model_state_dict.pop(old_key)

        return model_state_dict
