# end to end data pipeline/ batch + stream/ dashboard

## The data pipeline

![image](https://user-images.githubusercontent.com/51215027/227733027-650cadf6-cc61-4712-ab7a-71f4dae02949.png)


let's break down the diagram above to elementary pieces and try to understand what's going on under the hood of each one:

### Jcdecaux API:
a single call of this API returns the most recent information about all the existing stations, "the most recent " here could be the last update got 1–2 min ago, which doesn't really mean real-time data, we can do nothing to improve it, this is how the API works. And to make the API act like a stream source, we'll call it in a loop mode with a time sleep of few seconds between calls, so as not to overload the server.

### kafka:
using a kafka producer, the kafka cluster will receive the messages (data) coming from the stream source and store them in a topic called "stations_topic", this data could be filtered before sending it, but  we'll just keep all information here, this is beneficial especially if we're planning to expand our work later and do additional analytics for other locations.
kafka gives us the possibility to send and consume data in order within the same topic partition, however, this is not guaranteed across partitions, in our case we have time series data, so we do care about the order, at this stage we have 2 possibilities:

a) we can filter out only data related to Belgium country and create as many partitions as the number of cities, and then use the city name as a key to garanthee that the messages of the same city go in order to the same partition.

b) or we can create one partition (we loose parallelism benefits in this case) and send all data there. And as you would have probably guessed, this is our choice, since we'll keep all information.

kafka can have more than one consumer group, each group can read the messages only once, in parallel with the others, in each group we can have as many consumers as partitions in the topic, but this scenario is more applicable in production environments where we have clusters of machines that can run in parallel. In our case, we'll go with two consumer groups one for batch-spark and the other for spark structured streaming  jobs, the two can consume data in parallel, but to make them share ressources (RAM and cpu) we should set the config spark.dynamicAllocation.enabled to True.

### Chaine 1:
as stated before, we use spark to perform an ETL job, it's a batch script that polls data of the previous day (00:00:00 am => 23:59:59 pm) from the kafka cluster, transform it and load it to the datawarehouse, the script is scheduled to run each day at 5am.

### Datawarehouse:
the choice of the right datawarehouse depends on the data type and the business needs, in our case, the choice of SQLserver is totally random, you can change it if you want.

### Chaine 2:
spark structured streaming is used here to trigger a spark job (poll + process) each 10 seconds and write the results to a parquet datafile, this choice of the sink is again not the perfect, and might be changed to reach the lowest latency. the "10 seconds" here doesn't really sound as to be a real-time job, this window is configurable and can be shortened if you have a powerful machine. 

### Dashboard:
to create an interactive real time dashboard, you have a plenty of choices, the easiest one (to learn and implement) IMHO is streamlit, you don't need to be a web developer to use it. All you have to do is to write your python script that reads and shows data and hop! your application is ready on your localhost:8501 via the following command:

streamlit run myapp.py


![image](https://user-images.githubusercontent.com/51215027/227733343-a770d829-fe5d-4af3-b99a-e724adbecc99.png)

![image](https://user-images.githubusercontent.com/51215027/227733351-dd032eda-0020-4bc6-a062-32b512b17552.png)

![image](https://user-images.githubusercontent.com/51215027/227733356-0fe99884-701a-4d9d-a553-c9ef1dd885ec.png)


Here we go.. the app shows that the station Jardin Aux Fleurs in Brussels has 5 bikes availables, 15 free docks and it's open, but there's no banking service 💰.

## Deployment
to deploy the whole architecture, i've used docker images, one for each service, and docker-compose to make all the containers run in the same network and can talk to each others.

## On your machine
to try this pipeline in your machine all you have to do is to clone this repository
build the following images using their dockerfiles. But before that, cd to the project folder using the command-line, and if you're on windows try starting docker desktop first.

# pyspark
docker build -t pyspark src/spark

# mssqlapp
docker build -t mssqlapp src/mssql

# pyapp
docker build -t pyapp src/app


and finally run the docker-compose command to build the whole architecture, you can then visit the application at localhost:8501

docker-compose -f dockercompose.yaml up
