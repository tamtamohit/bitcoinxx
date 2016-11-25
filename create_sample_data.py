import requests
import json
import flask
from pymongo import MongoClient


collection = MongoClient()['__init__'].trades

values = collection.find().limit(10)
# response = requests.get('https://api.btcxindia.com/trades')
#
# values = json.loads(response.text)
print values
for value in values:
    print value



