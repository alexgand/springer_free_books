FROM ubuntu:latest

COPY main.py /app/
COPY requirements.txt /app/
COPY run.sh /app/

WORKDIR /app

RUN apt update
RUN apt upgrade -y
RUN apt install -y python3-pip python3-setuptools python3.7-venv

RUN python3.7 -m venv .venv
RUN . .venv/bin/activate
RUN pip3 install -r requirements.txt

# CMD bash run.sh