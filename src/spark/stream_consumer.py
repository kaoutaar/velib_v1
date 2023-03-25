from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructField, StructType, StringType, IntegerType, BooleanType, TimestampType, LongType

server = "kafka" #localhost
topic = "stations_topic"
client = "JCDecaux API"
print("data stream from %s" %client)
print("Receiving orders data from Kafka topic %s" %topic)

schema = StructType(
    [StructField("number",IntegerType(),True),
     StructField("contract_name",StringType(),True),
     StructField("name",StringType(),True),
     StructField("banking",BooleanType(),True),
     StructField("bonus",BooleanType(),True),
     StructField("bike_stands",IntegerType(),True),
     StructField("available_bike_stands",IntegerType(),True),
     StructField("available_bikes",IntegerType(),True),
     StructField("status",StringType(),True),
     StructField("last_update",LongType(),True)])

spark = SparkSession\
    .builder\
    .master('local[*]')\
    .appName('velib_stream_consumer')\
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")\
    .config("spark.dynamicAllocation.enabled", True)\
    .config("spark.dynamicAllocation.shuffleTracking.enabled", True)\
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
spark.conf.set("spark.sql.shuffle.partitions", 1)


df = spark.readStream\
    .format("kafka")\
    .option("kafka.group.id	", "streamspark")\
    .option("kafka.bootstrap.servers", f"{server}:9092")\
    .option("subscribe", topic)\
    .option("startingOffsets", "latest")\
    .option("failOnDataLoss", False)\
    .load()

df = df.select( df.timestamp, F.explode(F.from_json(F.decode(df.value, "UTF-8").alias("value"), "ARRAY<STRING>")))
df = df.select(df.timestamp,F.from_json(df.col, schema).alias("value"))
df = df.select(df.timestamp,F.col("value.*"))
df = df.filter(df.contract_name=="bruxelles")\
    .withColumn("last_update", (df.last_update/F.lit(1000)).cast(TimestampType()))


def last_update(pdf):
    return pdf.sort_values(by="last_update", ascending=False).iloc[0].to_frame().T
stream = df.withWatermark("timestamp", "0 seconds").groupBy("number", F.window("timestamp","10 seconds")).applyInPandas(last_update, df.schema)

dir = "./streampool/data"

def write_2_loc(batchdata, batchId):
    batchdata.persist()
    print(batchdata.count())
    batchdata.write.format("parquet").mode("overwrite").save(dir)
    batchdata.unpersist()

q = stream.writeStream.foreachBatch(write_2_loc).trigger(processingTime="10 seconds").start()

try:
    q.awaitTermination()
except KeyboardInterrupt:
    print("test terminating...")