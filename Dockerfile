FROM python:3.7

RUN apt-get update && apt-get install -y wget postgresql postgresql-contrib

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash && apt-get install -y nodejs && npm install

EXPOSE 8000

RUN mkdir -p /app/
WORKDIR /app

ADD requirements.txt requirements.txt
ADD development.txt development.txt
RUN pip install --no-cache-dir -r development.txt

ADD . /app/

CMD /app/start.sh
