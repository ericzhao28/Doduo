# Doduo/Dockerfile
From ubuntu:17.10
MAINTAINER Eric Zhao "elzhao@caltech.edu"

# Install necessary packages on top of Ubuntu 17.10.
RUN apt update
RUN apt install gcc libc-dev g++ libssl-dev build-essential cmake make wget git -y
RUN apt install python3.6 python3.6-dev -y
RUN wget --no-verbose https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
RUN pip3 install --upgrade pip
RUN export C_INCLUDE_PATH=/usr/include
ENV LANG en_US.UTF-8

# All files under /Doduo.
WORKDIR /Doduo

# Install Python3.6 requirements.
COPY ./requirements.txt /Doduo/requirements.txt
RUN pip3 install -r /Doduo/requirements.txt
RUN python3.6 -m spacy download en_core_web_md

# Copy over Doduo files.
COPY ./dumps /Doduo/dumps
COPY ./configs /Doduo/configs
COPY ./Doduo /Doduo/Doduo

# Start the Flask server.
ENTRYPOINT ["sh", "-c", "python3.6 -m Doduo"]
