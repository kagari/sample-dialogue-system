import os


class BaseAgent():
    def __init__(self) -> None:
        pass

    def reply(self, s: str) -> str:
        return s


class GPT2Agent(BaseAgent):
    def __init__(self, model_path: str):
        from transformers import T5Tokenizer, GPT2LMHeadModel
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
        self.tokenizer.do_lower_case = True  # due to some bug of tokenizer config loading
        self.model = GPT2LMHeadModel.from_pretrained(model_path)

    def reply(self, s: str) -> str:
        if not s.startswith(self.tokenizer.bos_token):
            s = self.tokenizer.bos_token + s
        if not s.endswith(self.tokenizer.sep_token):
            s += self.tokenizer.sep_token
        input_ids = self.tokenizer(s, return_tensors="pt")["input_ids"]
        output_sequences = self.model.generate(input_ids=input_ids, top_p=0.95, top_k=50, do_sample=True,
                                               max_length=128+input_ids.size(1), bos_token_id=self.tokenizer.bos_token_id,
                                               eos_token_id=self.tokenizer.eos_token_id, pad_token_id=self.tokenizer.pad_token_id,
                                               bad_words_ids=[[self.tokenizer.unk_token_id]])
        generated = output_sequences.tolist()[0]
        generated = self.tokenizer.decode(generated)
        _, rep = generated.replace(' ', '').replace('<s>', '').replace('</s>', '').split('[SEP]')
        return rep


class Word2VecAgent(BaseAgent):
    import MeCab
    from gensim.models.word2vec import Word2Vec

    def __init__(self) -> None:
        arg = f'-Owakati -d {os.getenv("MECAB_CONFIG_DICDIR")}'
        self.tagger = MeCab.Tagger(arg)

        model_path = '/app/data/latest-ja-word2vec-gensim-model/word2vec.gensim.model'
        self.model = Word2Vec.load(model_path)

    def reply(self, s: str) -> str:
        """応答を生成する関数
        Args:
            s (str): ユーザ入力文字列
        Returns:
            str: システムの応答文
        """
        # 入力文を分かち書きにする
        words = self.tagger.parse(s).split(' ')

        # Word2Vecで分散表現を得る
        vec = []
        for w in words:
            try:
                vec.append(self.model[w])
            except KeyError:
                if w != '':
                    print(f'{w}')
        rep = ','.join([str(v) for v in vec])
        
        return rep