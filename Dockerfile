FROM ubuntu:latest

LABEL app="btt"

# RUN mkdir /app

COPY entrypoint.sh /app/entrypoint.sh
COPY dist/server /app/server

WORKDIR /app

ENV LANG=C.UTF-8 \ 
    LC_ALL=C.UTF-8

RUN chmod 555 /app/entrypoint.sh

ENTRYPOINT  ["/app/entrypoint.sh"]