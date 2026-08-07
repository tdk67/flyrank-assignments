FROM liquibase/liquibase:4.27
USER root
RUN wget -q https://jdbc.postgresql.org/download/postgresql-42.7.3.jar -P /liquibase/internal/lib/
USER liquibase
COPY changelog /liquibase/changelog
