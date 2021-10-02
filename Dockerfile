RUN apt-get update && apt-get install -y mecab libmecab-dev sudo

RUN pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html

RUN cd /usr/local/etc/ && \
    git clone --depth 1 https://github.com/neologd/mecab-unidic-neologd.git && \
    cd mecab-unidic-neologd && \
    echo yes | ./bin/install-mecab-unidic-neologd -n && \
    echo 'export MECAB_CONFIG_DICDIR=$(mecab-config --dicdir)/mecab-unidic-neologd' >> ~/.bashrc
# RUN python -m unidic download  # 上記で最新の辞書をダウンロードしているので、古い辞書はダウンロードしない
