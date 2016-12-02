from pymongo import MongoClient
from bson import ObjectId
import time, datetime
from random import randint
from exceptions import Exception



collection_trade = MongoClient()['app'].trades
'''
'''
collection_seller = MongoClient()['app'].seller_database
'''
{
	"_id" : ObjectId("5834d009f99ce64b5a9b213f"),
	"user" : "582ec573f99ce6291025082c",
	"price" : 50000,
	"bitcoins" : 2.3,
	"time" : "2016-11-23 04:38:57"
	"transaction_id": 5834d009f99ce64b5a9b213f
}
'''

collection_buyer = MongoClient()['app'].buyers_database
'''
{
	"_id" : ObjectId("5834d009f99ce64b5a9b213f"),
	"user" : "582ec573f99ce6291025082c",
	"price" : 50000,
	"bitcoins" : 2.3,
	"time" : "2016-11-23 04:38:57"
	"transaction_id": 5834d009f99ce64b5a9b213f
}
'''

collection_account = MongoClient()['app'].account
'''
{
    "_id" : ObjectId("582ec573f99ce6291025082c"),
    "bitcoins" : 2.089,
    "account_balance" : 0,
    pending_orders :{
        selling : [{
            bitcoins:,
            price:,
            time:,
            transactionId:
        }],
        buying : [{
            bitcoins:,
            price:,
            time:,
            transactionId:
        }
    }],
    account_history : {
        sold : [{
            bitcoins:,
            price:,
            time:,
            transactionId:
        }],
        bought : [{
            bitcoins:,
            price:,
            time:,
            transactionId:
        }]
    }
}
'''




def create_key():
    x = ''
    for i in xrange(6):
        x += str(randint(0,9))
    return x



def trade_history(bitcoins,price,buyers_transaction_id,sellers_transaction_id):
    """
    {
        time: date_time,
        bitcoins: ,
        price: ,
        transaction_id:
    }
    :return:
    """
    trader_doc = {
        'time': st(),
        'bitcoins': bitcoins,
        'price': price,
        'buyers_transaction_id': buyers_transaction_id,
        'sellers_transaction_id': sellers_transaction_id
    }
    collection_trade.insert(trader_doc)
    return





class buyer:
    def __init__(self,userId,price_per_btc,transact_amount,transaction_id=None):
        self.userId = str(userId)
        self.price_per_btc = float(price_per_btc)
        self.transact_amount = float(transact_amount)
        self.bitcoins = float(transact_amount)/float(price_per_btc)
        self.st = st()
        if transaction_id == None:
            self.transaction_id = userId + create_key()
            self.update = False
        else:
            self.transaction_id = transaction_id
            self.update = True
    def deduct_money(self,transact_amount):
        # print self.transact_amount
        collection_account.update({'_id':ObjectId(self.userId)},{'$inc':{'account_balance':-transact_amount}})

    # def transfer_money_to_seller(self,sellers_user_id, transfered_money, bitcoins, transaction_id, price_per_btc):

    def transfer_money_to_seller(self,seller_data,seller_ka_paisa,mera_paisa):
        '''
        paisa de do bitcoin ka
        '''
        remaning_money = seller_ka_paisa - mera_paisa
        print mera_paisa, self.price_per_btc
        bitcoin_purchased = float(mera_paisa)/float(self.price_per_btc)
        seller_account_info = collection_account.find_one({'_id':ObjectId( seller_data['user'])})
        pending_orders = seller_account_info['pending_orders']
        for num, order in enumerate(pending_orders['selling']):
            if order['transaction_id'] ==  seller_data['transaction_id']:
                if remaning_money == 0 or remaning_money < 0.000000001:
                    pending_orders['selling'] = []
                    print pending_orders
                elif remaning_money > 0:
                    # collection_buyer reduce bitcoins
                    order['bitcoins'] -= bitcoin_purchased

        collection_account.update({'_id':ObjectId( seller_data['user'])},{
            '$inc' : {
                'account_balance' : mera_paisa,
                'bitcoins' : -bitcoin_purchased
            },
            '$set' : {
                'pending_orders' : pending_orders
            },
            '$push' : {
                'account_history.sold' : {
                    'bitcoins': bitcoin_purchased,
                    'transaction_id' :  seller_data['transaction_id'],
                    'money_recived' : mera_paisa
                }
            }
        })
        # print 'here'
        print remaning_money
        if remaning_money == 0 or remaning_money < 0.000000001:
            collection_seller.remove({'transaction_id': seller_data['transaction_id']})
        elif remaning_money > 0:
            collection_seller.update({'transaction_id': seller_data['transaction_id']},{
                '$inc' : {
                    'bitcoins' : -bitcoin_purchased
                }
            })
        self.deduct_money(transact_amount=mera_paisa)

        trade_history(bitcoins=bitcoin_purchased,price=self.price_per_btc,
                      buyers_transaction_id=self.transaction_id,sellers_transaction_id= seller_data['transaction_id'])




    def market_processing_for_buyer(self):
        buyers_record = {
            "user": self.userId,
            "price": self.price_per_btc,
            "time": self.st,
            "transaction_id": self.transaction_id,
            'deposit': self.transact_amount
        }
        seller_data  = collection_seller.find_one({'price': self.price_per_btc,
                                             'user':{'$ne':str(self.userId)}})


        if seller_data == None:
            if self.update == False:
                collection_buyer.insert(buyers_record)
                del buyers_record['user']
                collection_account.update({'_id':ObjectId(self.userId)},{'$push':{
                    'pending_orders.buying' : buyers_record
                }})
                print 'Written on database'
            else:
                collection_buyer.update({'transaction_id':self.transaction_id},{
                    '$set': buyers_record
                })
                del buyers_record['user']
                collection_account.update({'_id': ObjectId(self.userId)}, {'$set': {
                    'pending_orders.buying': [buyers_record]
                }})
        else:
            seller_ask_total_money =  seller_data ['bitcoins'] * self.price_per_btc
            if seller_ask_total_money >= self.transact_amount:
                self.transfer_money_to_seller( seller_data = seller_data ,seller_ka_paisa=seller_ask_total_money,
                                              mera_paisa=self.transact_amount)
                collection_account.update({'_id':ObjectId(self.userId)},{
                    '$push': {
                        'account_history.bought':{
                                "price": self.price_per_btc,
                                "bitcoins": self.bitcoins,
                                "time": self.st,
                                "transaction_id": self.transaction_id,
                                'amount_paid' : self.transact_amount
                        }
                    },
                    '$inc': {
                        'bitcoins':self.bitcoins
                    }
                })
                print 'Transaction succesful completely'
                if self.update == True:
                    collection_buyer.remove({'transaction_id':self.transaction_id})
                    del buyers_record['user']
                    collection_account.update({'_id': ObjectId(self.userId)}, {'$set': {
                        'pending_orders.buying': []
                    }})
            else:
                #jitna hai utna le lo
                # self.bitcoins = self.bitcoins - seller['bitcoins']
                transfered_money =  seller_data ['bitcoins']*self.price_per_btc
                self.transfer_money_to_seller( seller_data = seller_data ,seller_ka_paisa=seller_ask_total_money,mera_paisa=seller_ask_total_money)
                self.transact_amount -= seller_ask_total_money
                self.bitcoins -= self.transact_amount * self.price_per_btc
                print 'seller bitcoin: ' ,  seller_data ['bitcoins']
                collection_account.update({'_id': ObjectId(self.userId)}, {'$push': {
                    'account_history.bought': {
                                "price": self.price_per_btc,
                                "bitcoins":  seller_data ['bitcoins'],
                                "time": self.st,
                                "transaction_id": self.transaction_id,
                                'amount_paid' : seller_ask_total_money
                    }},
                    '$inc': {
                        'bitcoins' : float( seller_data ['bitcoins'])
                    }
                })
                self.market_processing_for_buyer()

                print 'Transaction succesful Partially'




class seller:
    def __init__(self, userId, price_per_btc, bitcoins,transactionId=None):
        self.userId = str(userId)
        self.price_per_btc = float(price_per_btc)
        self.bitcoins = float(bitcoins)
        if transactionId == None:
            self.transactionId = userId + create_key()
            self.update = False
        else:
            self.transactionId = transactionId
            self.update = True
        self.st = st()

    def deduct_bitcoins(self,bitcoins):
        collection_account.update({'_id':ObjectId(self.userId)},{'$inc':{'bitcoins':-bitcoins}})

    def give_bitcoin(self,bitcoins,buyer_data,amount_paid):
        buyer_acount_info = collection_account.find_one({'_id':ObjectId(buyer_data['user'])})
        # buyer_acount_info['a']
        bitcoins_remaning = buyer_data['bitcoins'] - bitcoins
        # print 'bitcoin remaning', bitcoins_remaning
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        order_recived = {
            'price': self.price_per_btc,
            'bitcoins': bitcoins,
            'amount_paid' : amount_paid,
            'transaction_id' : buyer_data['transaction_id'],
            'time' : st
        }
        print 'order recived', bitcoins
        print buyer_acount_info
        pending_orders = buyer_acount_info['pending_orders']
        for num,order in enumerate(pending_orders['buying']):
            if order['transaction_id'] == buyer_data['transaction_id']:
                if bitcoins_remaning == 0 :
                    pending_orders['buying'] = []
                    print pending_orders
                elif bitcoins_remaning > 0:
                    #collection_buyer reduce bitcoins
                    # order['bitcoins'] = bitcoins_remaning
                    order['deposit'] -= amount_paid
        print 'pending orders:', pending_orders
        print 'orders:', order_recived
        collection_account.update({'_id':ObjectId(buyer_data['user'])},{
            '$inc':{
                'bitcoins' : bitcoins,
                'account_balance' : -amount_paid
            },
            '$set': {
                'pending_orders' : pending_orders
            },
            '$push' : {
                'account_history.bought' : order_recived
            }
        })
        print 'yaha tak aaya'
        # print bitcoins_remaning, buyer_data['transaction_id']
        if bitcoins_remaning == 0:
            print 'bitcoin uda diya'
            collection_buyer.remove({'transaction_id':buyer_data['transaction_id']})
            print 'removed'
        elif bitcoins_remaning > 0:
            print 'bitcoin ghata diya'
            print bitcoins, amount_paid
            collection_buyer.update({'transaction_id':buyer_data['transaction_id']},{
                '$inc' : {
                    'deposit': -amount_paid
                }
            })
        # , {'$inc': {'bitcoins': self.bitcoins}}
        else:
            raise Exception('Bitcoin Is Negative')

        self.deduct_bitcoins(bitcoins=bitcoins)

        trade_history(bitcoins=bitcoins,price=self.price_per_btc,
                      buyers_transaction_id=buyer_data['transaction_id'],sellers_transaction_id=self.transactionId)




    def market_processing_for_seller(self):
        seller_pending_orders = collection_account.find_one({
            '_id': ObjectId(self.userId)
        },
            {
                'pending_orders' : 1
            }
        )


        buyer_data = collection_buyer.find_one({'user':{'$ne':str(self.userId)},'price':self.price_per_btc})

        seller_record = {
            'user' : self.userId,
            'price' : self.price_per_btc,
            'bitcoins' : self.bitcoins,
            'transaction_id' : self.transactionId
        }
        print buyer_data
        if buyer_data == None:
            if self.update == False:
                collection_seller.insert(seller_record)
                del seller_record['user']
                collection_account.update({'_id':ObjectId(self.userId)},{'$push':{'pending_orders.selling':seller_record}})
            else:
                collection_seller.update({'transaction_id':self.transactionId},{
                    '$set': seller_record
                })
                del seller_record['user']
                collection_account.update({'_id': ObjectId(self.userId)},
                                          {'$set': {'pending_orders.selling': [seller_record]}})

        else:
            this_user_can_buy = buyer_data['deposit'] / self.price_per_btc
            buyer_data['bitcoins'] = this_user_can_buy
            if this_user_can_buy >= self.bitcoins:
                #give bitcoins
                amount_paid = self.bitcoins * self.price_per_btc
                self.give_bitcoin(bitcoins=self.bitcoins,buyer_data=buyer_data,amount_paid=amount_paid)
                seller_record['amount_recieved'] = amount_paid
                collection_account.update({'_id':ObjectId(self.userId)},{
                    '$inc' : {
                        'account_balance':amount_paid
                    },
                    '$push' : {
                        'account_history.sold' : seller_record
                    }
                })
                print 'poora ho gya'
                if self.update == True:
                    collection_account.update({'_id': ObjectId(self.userId)},
                                              {'$set': {'pending_orders.selling': []}})
            else:
                #jitna hai utna le lo
                remaning_bitcoin = self.bitcoins - this_user_can_buy
                amount_paid = this_user_can_buy * self.price_per_btc
                self.give_bitcoin(bitcoins=this_user_can_buy, buyer_data=buyer_data, amount_paid=amount_paid)
                seller_record['amount_recieved'] = amount_paid
                seller_record['bitcoins'] = buyer_data['bitcoins']
                collection_account.update({'_id': ObjectId(self.userId)}, {
                    '$inc': {'account_balance': amount_paid},
                    '$push': {
                        'account_history.sold': seller_record
                    }
                })
                self.bitcoins = remaning_bitcoin
                self.market_processing_for_seller()
                print 'poora nahi huwa'



def st():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')



def update_buying_bid(account,price,deposit):
    buying = account['pending_orders']['buying'][0]
    buying['price'] = price
    buying['deposit'] = deposit
    collection_account.update({'_id':account['_id']},)


if __name__ == '__main__':


    mohit = seller(userId='582ec729f99ce62a1ac41ee4',price_per_btc=5000,bitcoins=0.8,st= st)
    mohit.market_processing_for_seller()
    mohit = buyer("582ec573f99ce6291025082c",5000,transact_amount=8000,st=st)
    mohit.market_processing_for_buyer()