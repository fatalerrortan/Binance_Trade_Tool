FROM python:latest

COPY entrypoint.sh /opt/entrypoint.sh
COPY dist/server /opt/server

WORKDIR /opt

ENV LANG=C.UTF-8 \ 
    LC_ALL=C.UTF-8

RUN chmod 744 /opt/entrypoint.sh

ENTRYPOINT  ["/opt/entrypoint.sh"]