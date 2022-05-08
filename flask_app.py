from flask import Flask,request, jsonify, Response, g, url_for, abort
app = Flask(__name__)
import json

#Nosql database
from pymongo import MongoClient

client = MongoClient('mongodb://chownv:firstmongocluster@cluster0-shard-00-00.qtb4k.mongodb.net:27017,cluster0-shard-00-01.qtb4k.mongodb.net:27017,cluster0-shard-00-02.qtb4k.mongodb.net:27017/retail_order?ssl=true&replicaSet=atlas-73uabp-shard-0&authSource=admin&retryWrites=true&w=majority')
from bson import json_util, ObjectId

#Queue system
from kafka.producer import KafkaProducer
try:
    producer = KafkaProducer(bootstrap_servers=["localhost:9092"], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
except Exception as e:
    print("Exception getting the kafka producer")
    producer = None


#Other imports
from circuitbreaker import circuit
import time
from datetime import datetime as dt
import uuid
from time import sleep
import os


#Authetication
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

@app.before_first_request
def create_tables():
    db.create_all()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=1200):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    print (username)
    print(password)
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        print("Entered existing user")
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

"""
@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/')
def hello_world():
    return "Hello Chow"
"""

#design pattern - circuit breaker


@circuit(failure_threshold=10, expected_exception=ConnectionError)
@app.route('/order',methods=['POST'])
def placeorder():
    # create a record in elasticsearch
    data= request.get_json()
 
    #validation_step
    mandatory_keys = ['userid','cost','orderitems'] 
    for keyname in mandatory_keys:
        if keyname not in data:
            return jsonify(keyname +"is a mandatory argument. Please pass on the value.")



    latest_timestamp = dt.now().isoformat('T')
    orderid = str(uuid.uuid4())       

    mongo_doc = {"userid": data['userid'], "orderid":orderid, "orderstatus":"PLACED", "timestamp":latest_timestamp, "cost":data['cost'], "orderitems":data['orderitems'] }
    
    # Add any retry mechanism
    try:
        result = client['retail_order']['order_tracker'].insert_one(json.loads(json_util.dumps(mongo_doc)))
        print ("created the entry successfully")
    except Exception as e:
        print (e)
        # handle error messages to return to customer
    
    #send to kafka producer
    producer.send('order_details', mongo_doc)

    return jsonify("Order placed. Your reference number: " + str(orderid))    
   

@app.route('/orderdetails',methods=['GET'])
@auth.login_required
def getorderDetails():
    # diffent query params
    data= request.get_json()

    if 'orderid' in data:
        filter={
          'orderid': data['orderid']
         }

        result = client['retail_order']['order_tracker'].find_one(
            filter=filter
         )

        for item in result:
            print(item)

        if result:
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return jsonify("Order id not present in database. Please verify")
    elif 'userid' in data:

        filter={
          'orderid': orderid
         }

        result = client['retail_order']['order_tracker'].find_many(
            filter=filter
         )


        if result:
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return jsonify("User have not placed any orders")
    else:
        return jsonify("Atleast one of the argument orderid or userid required to process")


 
if __name__ == "__main__":
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(host='0.0.0.0', port=5008, debug=True, use_reloader=True, threaded=True,ssl_context=('server.crt','server.key')) 
