from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructField, StructType, StringType, IntegerType, TimestampType, LongType
import datetime

server = "kafka" #localhost
topic = "stations_topic"
client = "JCDecaux API"
print("data stream from %s" %client)
print("Receiving orders data from Kafka topic %s" %topic)

spark = SparkSession\
    .builder\
    .master('local[*]')\
    .appName('velib_batch_consumer')\
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")\
    .config("spark.dynamicAllocation.enabled", True)\
    .config("spark.dynamicAllocation.shuffleTracking.enabled", True)\
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
spark.conf.set("spark.sql.shuffle.partitions", 1)


now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
start = datetime.datetime(year, month, day,0,0)
end = datetime.datetime(year, month, day,23,59,59)
start_timestamp = int(datetime.datetime.timestamp(start))*1000 #millisecond
end_timestamp = int(datetime.datetime.timestamp(end))*1000

df = spark.read\
    .format("kafka")\
    .option("kafka.group.id	", "batchspark")\
    .option("kafka.bootstrap.servers", f"{server}:9092")\
    .option("subscribe", topic)\
    .option("failOnDataLoss", False)\
    .option("startingTimestamp",  start_timestamp)\
    .option("endingTimestamp",end_timestamp)\
    .load()


schema = StructType(
    [StructField("number",IntegerType(),True),
     StructField("contract_name",StringType(),True),
     StructField("bike_stands",IntegerType(),True),
     StructField("available_bike_stands",IntegerType(),True),
     StructField("available_bikes",IntegerType(),True),
     StructField("status",StringType(),True),
     StructField("last_update",LongType(),True)])

df = df.select(df.timestamp, F.explode(F.from_json(F.decode(df.value, "UTF-8").alias("value"), "ARRAY<STRING>")))
df = df.select(df.timestamp,F.from_json(df.col, schema).alias("value"))
df = df.select(df.timestamp,F.col("value.*"))
df = df.filter(df.contract_name.isin("bruxelles","namur"))\
    .withColumn("last_update", (df.last_update/F.lit(1000)).cast(TimestampType()))
df = df.withColumn("hour", F.hour(df.last_update))\
    .withColumn("date", F.to_date(df.last_update,"yyyy-MM-dd"))

agg_df = df.groupby(["date","contract_name", "number", "hour"])\
    .agg(F.max(df.bike_stands).alias("bike_stands"),
        F.mean(df.available_bikes).cast("int").alias("mean_available_bikes"),
        F.mean(df.available_bike_stands).cast("int").alias("mean_available_stands"))

print(agg_df.show())


#connection
dbserver_name = "mssql" #"LAPTOP-VUDKOBLS\SQLEXPRESS" 
database_name = "jcdeco"
jdbcUrl = f"jdbc:sqlserver://{dbserver_name}:1433;DatabaseName={database_name}"+ ";encrypt=true;trustServerCertificate=true;integratedSecurity=true;"
driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"



table_name = "bikes"
agg_df.write.format("jdbc").option("url", jdbcUrl).option("driver", driver).option("dbtable", table_name).mode("append").save()