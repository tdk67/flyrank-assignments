FROM liquibase/liquibase:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /liquibase/jars

RUN curl -fsSL https://jdbc.postgresql.org/download/postgresql-42.7.4.jar -o /liquibase/jars/postgresql.jar

USER liquibase
