FROM python:3

COPY main.py /app/
COPY requirements.txt /app/

WORKDIR /app

RUN chmod 740 ./main.pay && mkdir ./download/ && pip install -r requirements.txt
CMD ["main.py"]