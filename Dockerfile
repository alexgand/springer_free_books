FROM python:3

COPY main.py /app/
COPY requirements.txt /app/

WORKDIR /app

RUN chmod 740 ./main.py && mkdir ./downloads/ && pip install -r requirements.txt
CMD ["/app/main.py"]
