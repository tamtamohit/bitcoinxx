"""

"""
from pymongo import MongoClient
collection_trade = MongoClient()['__init__'].trades
collection_seller = MongoClient()['__init__'].seller_database
collection_buyer = MongoClient()['__init__'].buyers_database
collection_account = MongoClient()['__init__'].account

def content(trade=False):
    basics = {"notification":[['BTC withdrawal timing has been reduced from 30 minutes to 10 minutes.','08-10-2016 12:33'],
             ["Autopay deposit facility using ICICI Eazypay is now resumed. Customers can avail this facility now.","08-10-2016 12:22"]]}
    if trade==True:
        values = collection_trade.find().limit(10)
        # response = requests.get('https://api.btcxindia.com/trades')
        #
        # values = json.loads(response.text)
        basics['trades'] = []
        for value in values:
            basics['trades'].append(value)

        sellers = collection_seller.find()
        basics['sellers'] = []
        for seller in sellers:
            basics['sellers'].append(seller)

        buyers = collection_buyer.find()
        basics['buyers'] = []
        for buyer in buyers:
            buyer['bitcoins'] =  buyer['deposit']/buyer['price']
            basics['buyers'].append(buyer)

    # print basics

    return basics





