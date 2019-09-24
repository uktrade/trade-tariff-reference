FROM python:3.7

RUN apt-get update && apt-get install -y wget postgresql postgresql-contrib

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash && apt-get install -y nodejs
RUN pip install --upgrade pip &&  pip install pipenv


EXPOSE 8000

RUN mkdir -p /app/
WORKDIR /app

ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
RUN pipenv install --dev --system --deploy

ADD . /app/

CMD /app/scripts/start.sh
