from kafka import KafkaProducer
import time
import urllib.request


key = "c1d0cfc0377b8d04d9179d1c3f7a80e2491b30c3"
url = f"https://api.jcdecaux.com/vls/v1/stations?&apiKey={key}"

server = "kafka" #localhost
topic = "stations_topic"
client = "JCDecaux API"
producer = KafkaProducer(bootstrap_servers=[f'{server}:9092'], client_id=client, acks=1)

print("data stream from %s" %client)
print("Sending orders data to Kafka topic %s" %topic)

try:
    while True:
        response = urllib.request.urlopen(url)
        stations = response.read().decode()  #
        producer.send(topic, stations.encode("UTF-8"))

        # stations = json.loads(response.read().decode())  #
        # for station in stations:
        #     producer.send(topic,
        #                   json.dumps(station).encode("UTF-8"),
        #                   key=str(station['contract_name']).encode())

        print("msg sent...")
        time.sleep(10)

except KeyboardInterrupt:
    print("Terminating ...")

finally:
    producer.close()