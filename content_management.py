"""

"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from operator import itemgetter


collection_trade = MongoClient()['app'].trades
collection_seller = MongoClient()['app'].seller_database
collection_buyer = MongoClient()['app'].buyers_database
collection_account = MongoClient()['app'].account

def content(trade=False):
    basics = {"notification":[['BTC withdrawal timing has been reduced from 30 minutes to 10 minutes.','08-10-2016 12:33'],
             ["Autopay deposit facility using ICICI Eazypay is now resumed. Customers can avail this facility now.","08-10-2016 12:22"]]}
    if trade==True:
        values = collection_trade.find().limit(10).sort('time',DESCENDING)
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

        basics['sellers'] = sorted(basics['sellers'],key=itemgetter('price'))
        basics['buyers'] = sorted(basics['buyers'], key=itemgetter('price'))
        basics['buyers'].reverse()
    # print basics

    return basics



def last_trade_price():
    for i in collection_trade.find().sort('time',DESCENDING):
        return i['price']


# if __name__ == '__main__':
    # print last_trade_price()