FROM python:3

COPY *.py /app/
COPY requirements.txt /app/

WORKDIR /app

RUN chmod 740 ./*.py && mkdir ./downloads/ && pip install -r requirements.txt
CMD ["/app/main.py"]
