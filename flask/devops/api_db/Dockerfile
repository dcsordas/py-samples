FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y postgresql-9.5 postgresql-client-9.5 postgresql-contrib-9.5

COPY devops/api_db/schema.sql /schema.sql

USER postgres

RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER api WITH SUPERUSER PASSWORD 'api';" &&\
    createdb -O api api &&\
    psql api < schema.sql &&\
    createdb -O api test &&\
    psql test < schema.sql

RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.5/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.5/main/postgresql.conf

CMD ["/usr/lib/postgresql/9.5/bin/postgres","-D", "/var/lib/postgresql/9.5/main","-c", "config_file=/etc/postgresql/9.5/main/postgresql.conf"]

EXPOSE 5432