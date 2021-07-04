import os
import MeCab
from gensim.models.word2vec import Word2Vec

arg = f'-Owakati -d {os.getenv("MECAB_CONFIG_DICDIR")}'
tagger = MeCab.Tagger(arg)

model_path = '/app/data/latest-ja-word2vec-gensim-model/word2vec.gensim.model'
model = Word2Vec.load(model_path)

class Agent():
    def __init__(self) -> None:
        pass

    def reply(self, s: str) -> str:
        """応答を生成する関数
        Args:
            s (str): ユーザ入力文字列
        Returns:
            str: システムの応答文
        """
        # 入力文を分かち書きにする
        words = tagger.parse(s).split(' ')

        # Word2Vecで分散表現を得る
        vec = []
        for w in words:
            try:
                vec.append(model[w])
            except KeyError:
                if w != '':
                    print(f'{w}')
        rep = ','.join([str(v) for v in vec])
        
        return rep