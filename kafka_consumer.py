from kafka import KafkaConsumer
import json
from time import sleep

#Nosql database
from pymongo import MongoClient

client = MongoClient('mongodb://chownv:firstmongocluster@cluster0-shard-00-00.qtb4k.mongodb.net:27017,cluster0-shard-00-01.qtb4k.mongodb.net:27017,cluster0-shard-00-02.qtb4k.mongodb.net:27017/retail_order?ssl=true&replicaSet=atlas-73uabp-shard-0&authSource=admin&retryWrites=true&w=majority')
  
consumer = KafkaConsumer(
    'order_details',
     bootstrap_servers=['0.0.0.0:9092'],
     value_deserializer=lambda m: json.loads(m.decode('utf-8')))

for message in consumer:
    print (message.value)
    # update the elastic
    orderid = message.value['orderid']
    #Do some processing
    sleep(10)

    filter={
    'orderid': orderid
    }

    result = client['retail_order']['order_tracker'].find_one(
      filter=filter
    )

    for item in result:
        print(item)

    newvalues = { "$set": {"orderstatus": "PROCESSED"} }
    
    try:
        result = client['retail_order']['order_tracker'].update_one(filter, newvalues)
        print (result)
    except Exception as e:
        print (e)
        print ("ERROR:Error in processing order")
