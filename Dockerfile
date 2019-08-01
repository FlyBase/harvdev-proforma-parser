FROM flybase/harvdev-docker:latest

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-u", "src/app.py"]
