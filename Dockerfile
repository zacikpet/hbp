FROM centos/python-36-centos7

WORKDIR /app

USER root

COPY ./requirements.txt ./

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

USER 1001

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
