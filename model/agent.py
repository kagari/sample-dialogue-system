import os
import MeCab

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
        tagger = MeCab.Tagger(f'-Owakati -d {os.getenv("MECAB_CONFIG_DICDIR")}')
        rep = tagger.parse(s)

        # TODO: Word2Vecで分散表現を得る
        
        return rep