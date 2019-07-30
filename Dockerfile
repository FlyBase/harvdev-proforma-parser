FROM flybase/harvdev-docker:latest

WORKDIR /usr/src/app

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .

CMD ["python3", "-u", "src/app.py"]