FROM python:3.6.3-alpine3.6

RUN apk add --no-cache \
    postgresql-dev \
    gcc \ 
    python3-dev \
    musl-dev 

WORKDIR /usr/src/app

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .

CMD ["python3", "-u", "src/app.py"]