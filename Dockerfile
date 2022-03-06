FROM fatalerrortxl/modi_ubuntu:abbt

LABEL app="abtt"

WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh
COPY dist/server /app/server
COPY config.ini /app/config.ini

ENV LANG=C.UTF-8 \ 
    LC_ALL=C.UTF-8

RUN chmod 555 /app/entrypoint.sh

ENTRYPOINT  ["/app/entrypoint.sh"]
