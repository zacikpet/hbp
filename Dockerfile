FROM python:3.8

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

RUN python download_nltk.py

RUN python update_scheduler.py &

RUN chmod +x ./start_server.sh

USER 1001

CMD ./start_server.sh
