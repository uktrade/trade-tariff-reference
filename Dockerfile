FROM python:3.8-slim

# PSQL is used at build time - so, upgrade Postgres to be compatible with the version specified in docker-compose.
RUN apt-get update && \
    apt-get install -y gnupg2 lsb-release curl

RUN curl -sL https://www.postgresql.org/media/keys/ACCC4CF8.asc | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1 apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" > /etc/apt/sources.list.d/pgdg.list

ENV DOCKERIZE_VERSION v0.6.1
RUN curl -LO https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash &&  apt-get install -y \
    nodejs \
    gcc \
    libpq-dev \
    postgresql-12 \
    postgresql-client-12 \
    postgresql-contrib-12

RUN pip install --upgrade pip &&  pip install poetry

EXPOSE 8000

RUN mkdir -p /app/
VOLUME ["/app"]
WORKDIR /app

ADD pyproject.toml pyproject.toml
ADD poetry.lock poetry.lock
RUN poetry config virtualenvs.create false && \
    poetry install

ADD . /app/

CMD /app/scripts/start.sh
