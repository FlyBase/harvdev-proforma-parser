FROM flybase/harvdev-docker:alpine_3.10.2

RUN mkdir -p /.cache && chmod 777 /.cache && mkdir -p /.cache/bioservices && chmod 777 /.cache/bioservices

RUN mkdir -p /.config && chmod 777 /.config && mkdir -p /.config/bioservices && chmod 777 /.config/bioservices

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "app.py"]
