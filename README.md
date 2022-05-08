# Retail_Order_Assignment

Designed order processing REST Api's using python based web framework Flask. A NoSQL database MongoDB was used since it performs better on CRUD operations compared to other NoSQL db's. A Kafka messaging queue is used to send the events to consumer groups. SSL is enabled.

API:

   1. POST  /order
      
      DESCRIPTION  Takes inputs such as userid , cost, orderitems produces an event in kafka queue and also creates a record in mongodb collection with PLACED order status. Circuit breaker pattern is applied to handle connection errors to mongo or kafka broker.
      
      BODY  Mandatory Arguments: userid , cost , orderitems
      
      RESPONSE  200 Order reference number
      
      <img width="896" alt="Screenshot 2022-05-08 at 1 08 11 PM" src="https://user-images.githubusercontent.com/12572178/167289458-22ccdede-c0d3-4573-add2-242477ce8e72.png">

    
   2. GET /orderdetails
   
      DESCRIPTION Takes either orderid or userid as input and retrieves the orderdetails from database
      
      AUTHORIZATION  API_TOKEN generated
      
      BODY Either orderid or userid
      
      RESPONSE 200 JSON OUTPUT
      
      <img width="1015" alt="Screenshot 2022-05-08 at 1 07 53 PM" src="https://user-images.githubusercontent.com/12572178/167289468-04e1b22c-0f23-4517-b10d-67522210059e.png">

      
   3. POST /api/users
   
      DESCRIPTION Creates new users and stores in the DB
      
      BODY {username, password} 
      
      RESPONSE 201 username
      
      <img width="896" alt="Screenshot 2022-05-08 at 1 08 30 PM" src="https://user-images.githubusercontent.com/12572178/167289437-9cd43b0c-7c30-4c85-b5a8-2a73ca3e2931.png">

      
   4. GET /api/token
   
      DESCRIPTION Creates token for existing user
      
      AUTHORIZATION BASIC Auth
      
      BODY NONE
      
      RESPONSE 200 access_token, expiry
      
        <img width="924" alt="Screenshot 2022-05-08 at 1 08 47 PM" src="https://user-images.githubusercontent.com/12572178/167289389-5c136e7b-474a-4cea-a6bb-5860b4576d6b.png">
      
FLASK:
     DESCRIPTION Serves the apis
     
     conda activate my_env
     
     Install the requirements.txt
     
     python flask_app.py
     
     
KAFKA_BROKER
     Installed in local port 9092
     

KAFKA_CONSUMER

     DESCRIPTION receives the message event and processess the order. Updates the order status to PROCESSED.
     
     conda activate my_env
     
     python kafka_consumer.py


MONGODB
     Created cluster on cloud using Atlas
      


