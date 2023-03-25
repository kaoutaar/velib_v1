FROM mcr.microsoft.com/mssql/server:2022-latest
ENV ACCEPT_EULA=Y
ENV MSSQL_SA_PASSWORD=MY1password
EXPOSE 1433

WORKDIR /code
COPY . /code
USER root
RUN chmod +x /code/startup.sh

CMD ["./startup.sh"]
