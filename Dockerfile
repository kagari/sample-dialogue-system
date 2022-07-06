# docker build . -t dialog-system

FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

RUN conda config --add channels conda-forge && \
    conda config --remove channels defaults && \
    conda install 'mamba>=0.22.1'

# to avoid mamba install error that timeout runtime error
# RuntimeError: Download error (28) Timeout was reached \
# [https://conda.anaconda.org/conda-forge/linux-64/xxhash-0.8.0-h7f98852_3.tar.bz2]
# Operation too slow. Less than 30 bytes/sec transferred the last 60 seconds
RUN mamba install -y \
        fastapi \
        uvicorn

RUN mamba install -y \
        transformers \
        sentencepiece

RUN mamba install -y \
        scikit-learn

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

RUN pip install line-bot-sdk
