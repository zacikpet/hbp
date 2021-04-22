FROM python:3.8

WORKDIR /app

USER root

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
