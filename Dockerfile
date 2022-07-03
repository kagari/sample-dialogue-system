From pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

RUN apt-get update && \
    apt-get install -y python-opengl xvfb git

RUN conda config --add channels conda-forge && \
    conda config --remove channels defaults && \
    conda install 'mamba>=0.22.1'

RUN mamba install -y \
        jupyterlab \
        matplotlib \
        ipywidgets \
        scikit-learn \
        transformers \
        sentencepiece \
        tensorboard \
        stable-baselines3 \
        'huggingface_hub==0.4.0'

RUN pip install trl
