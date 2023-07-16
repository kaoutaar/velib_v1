# end to end data pipeline/ batch + stream/ dashboard

## The data pipeline

![image](https://user-images.githubusercontent.com/51215027/227733027-650cadf6-cc61-4712-ab7a-71f4dae02949.png)

![image](https://user-images.githubusercontent.com/51215027/227733343-a770d829-fe5d-4af3-b99a-e724adbecc99.png)

![image](https://user-images.githubusercontent.com/51215027/227733351-dd032eda-0020-4bc6-a062-32b512b17552.png)

![image](https://user-images.githubusercontent.com/51215027/227733356-0fe99884-701a-4d9d-a553-c9ef1dd885ec.png)


The app shows that the station Jardin Aux Fleurs in Brussels has 5 bikes availables, 15 free docks and it's open, but there's no banking service 💰.

## Deployment
to deploy the whole architecture, i've used docker images, one for each service, and docker-compose to make all the containers run in the same network and contact each others

## On your machine
To try this pipeline in your machine all you have to do is to
1) clone this repository
2) cd to the project folder using you terminal
3) if you're on windows try starting docker desktop,
4) in terminal, build the following images using their dockerfiles.

# pyspark
docker build -t pyspark src/spark

# mssqlapp
docker build -t mssqlapp src/mssql

# pyapp
docker build -t pyapp src/app


And finally run the docker-compose command to build the whole architecture.

docker-compose -f dockercompose.yaml up

The web application is available at localhost:8501 in your browser
