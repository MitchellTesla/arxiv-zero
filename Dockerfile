# arxiv/zero

FROM ubuntu:zesty

RUN apt-get update && apt-get install -y \
    ca-certificates \
    wget \
    gcc \
    g++ \
    libpython3.6 \
    python3.6 \
    python3.6-dev \
    python3.6-venv \
 && rm -rf /var/lib/apt/lists/*

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
ADD requirements/prod.txt /opt/arxiv/requirements.txt
RUN pip install -U pip && pip install -r /opt/arxiv/requirements.txt

ENV PATH "/opt/arxiv:${PATH}"

ADD wsgi.py /opt/arxiv/
ADD zero/ /opt/arxiv/zero/

EXPOSE 8000

WORKDIR /opt/arxiv/
CMD uwsgi --http-socket :8000 -w wsgi -t 3000 --processes 8 --threads 1 -M --async 100 --ugreen --manage-script-name