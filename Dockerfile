FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    pkg-config \
    libpng-dev \
    libjpeg8-dev \
    libfreetype6-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran \
    python \
    python-dev \
    python-pip \
    curl && \
    curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash - && \
    apt-get install -y nodejs

RUN npm install webpack -g

RUN pip install -U https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.12.0-cp27-none-linux_x86_64.whl && \
    pip install magenta ipython

COPY ./server/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY . /src/

WORKDIR /src/static/
RUN npm install && webpack -p

WORKDIR /src/server/

EXPOSE 8080
ENTRYPOINT python server.py
