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





class buyer:
    def __init__(self,userId,price_per_btc,transact_amount):
        self.userId = userId
        self.price_per_btc = float(price_per_btc)
        self.transact_amount = float(transact_amount)
        self.bitcoins = float(transact_amount)/float(price_per_btc)
        self.st = st()
        self.transaction_id = userId + create_key()
    def deduct_money(self):
        # print self.transact_amount
        collection_account.update({'_id':ObjectId(self.userId)},{'$inc':{'account_balance':-self.transact_amount}})

    # def transfer_money_to_seller(self,sellers_user_id, transfered_money, bitcoins, transaction_id, price_per_btc):

    def transfer_money_to_seller(self,seller,seller_ka_paisa,mera_paisa):
        '''
        paisa de do bitcoin ka
        '''
        remaning_money = seller_ka_paisa - mera_paisa
        print mera_paisa, self.price_per_btc
        bitcoin_purchased = float(mera_paisa)/float(self.price_per_btc)
        seller_account_info = collection_account.find_one({'_id':ObjectId(seller['user'])})
        pending_orders = seller_account_info['pending_orders']
        for num, order in enumerate(pending_orders['selling']):
            if order['transaction_id'] == seller['transaction_id']:
                if remaning_money == 0:
                    pending_orders['selling'].pop(num)
                    print pending_orders
                elif remaning_money > 0:

                    # collection_buyer reduce bitcoins
                    order['bitcoins'] -= bitcoin_purchased

        collection_account.update({'_id':ObjectId(seller['user'])},{
            '$inc' : {
                'account_balance' : mera_paisa
            },
            '$set' : {
                'pending_orders' : pending_orders
            },
            '$push' : {
                'account_history.sold' : {
                    'bitcoins': bitcoin_purchased,
                    'transaction_id' : seller['transaction_id'],
                    'money_recived' : mera_paisa
                }
            }
        })
        print 'here'
        print remaning_money
        if remaning_money == 0:
            print 'here'
            collection_seller.remove({'transaction_id':seller['transaction_id']})
        elif remaning_money > 0:
            print 'here'
            print seller['transaction_id']
            print collection_seller.find_one({'transaction_id': seller['transaction_id']})
            print bitcoin_purchased
            collection_seller.update({'transaction_id':seller['transaction_id']},{
                '$inc' : {
                    'bitcoins' : -bitcoin_purchased
                }
            })


        #get account info
        #paisa deduct karo aur isko de do
        # seller_ask_price_total = seller['bitcoins'] * self.price_per_btc
        # if seller_ask_price_total
    # def look_for_selles(price_per_btc, bitcoins, userId, transferd_money):
    def market_processing_for_buyer(self):
        '''
        look for price match
        if price mached:
            condition 1: number of bitcoins available >= bitcoins asked for
                transfer_money_to_seller
                add bitcoins to account of buyer
            condition 2: number of bitcoins available < bitcoins asked for
                take available bit coins
                transfer money to seller
                look for another seller
        :param price_per_btc:
        :param bitcoins:
        :return:
        '''
        buyers_record = {
            "user": self.userId,
            "price": self.price_per_btc,
            "time": self.st,
            "transaction_id": self.transaction_id,
            'deposit': self.transact_amount
        }
        seller = collection_seller.find_one({'price': self.price_per_btc,
                                             'user':{'$ne':self.userId}})

        # exit()
        if seller == None:


            collection_buyer.insert(buyers_record)
            del buyers_record['user']
            collection_account.update({'_id':ObjectId(self.userId)},{'$push':{
                'pending_orders.buying' : buyers_record
            }})
            print 'Written on database'
            # print 'yes'
        else:
            seller_ask_total_money = seller['bitcoins'] * self.price_per_btc
            if seller_ask_total_money >= self.transact_amount:
                # do the transaction
                # transfer_money_to_seller(seller['user'], self.transact_amount, self.bitcoins, seller['transaction_id'],self.price_per_btc)
                self.transfer_money_to_seller(seller=seller,seller_ka_paisa=seller_ask_total_money,mera_paisa=self.transact_amount)
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
            else:
                #jitna hai utna le lo
                # self.bitcoins = self.bitcoins - seller['bitcoins']
                transfered_money = seller['bitcoins']*self.price_per_btc
                self.transfer_money_to_seller(seller=seller,seller_ka_paisa=seller_ask_total_money,mera_paisa=seller_ask_total_money)
                self.transact_amount -= seller_ask_total_money
                self.bitcoins -= self.transact_amount * self.price_per_btc
                print 'seller bitcoin: ' , seller['bitcoins']
                collection_account.update({'_id': ObjectId(self.userId)}, {'$push': {
                    'account_history.bought': {
                                "price": self.price_per_btc,
                                "bitcoins": seller['bitcoins'],
                                "time": self.st,
                                "transaction_id": self.transaction_id,
                                'amount_paid' : seller_ask_total_money
                    }},
                    '$inc': {
                        'bitcoins' : float(seller['bitcoins'])
                    }
                })
                self.market_processing_for_buyer()

                print 'Transaction succesful Partially'




class seller:
    def __init__(self, userId, price_per_btc, bitcoins):
        self.userId = userId
        self.price_per_btc = float(price_per_btc)
        self.bitcoins = float(bitcoins)
        self.transactionId = userId + create_key()
        self.st = st()

    def deduct_bitcoins(self):
        collection_account.update({'_id':ObjectId(self.userId)},{'$inc':{'bitcoins':-self.bitcoins}})

    def give_bitcoin(self,bitcoins,buyer,amount_paid):
        buyer_acount_info = collection_account.find_one({'_id':ObjectId(buyer['user'])})
        # buyer_acount_info['a']
        bitcoins_remaning = buyer['bitcoins'] - bitcoins
        print 'bitcoin remaning', bitcoins_remaning
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        order_recived = {
            'price': self.price_per_btc,
            'bitcoins': bitcoins,
            'amount_paid' : amount_paid,
            'transaction_id' : buyer['transaction_id'],
            'time' : st
        }
        print 'order recived', bitcoins
        print buyer_acount_info
        pending_orders = buyer_acount_info['pending_orders']
        for num,order in enumerate(pending_orders['buying']):
            if order['transaction_id'] == buyer['transaction_id']:
                if bitcoins_remaning == 0 :
                    pending_orders['buying'].pop(num)
                    print pending_orders
                elif bitcoins_remaning > 0:
                    #collection_buyer reduce bitcoins
                    order['bitcoins'] = bitcoins_remaning
                    order['deposit'] -= amount_paid
        print 'pending orders:', pending_orders
        print 'orders:', order_recived
        collection_account.update({'_id':ObjectId(buyer['user'])},{
            '$inc':{
                'bitcoins' : bitcoins
            },
            '$set': {
                'pending_orders' : pending_orders
            },
            '$push' : {
                'account_history.bought' : order_recived
            }
        })
        print 'yaha tak aaya'
        print bitcoins_remaning, buyer['transaction_id']
        if bitcoins_remaning == 0:
            print 'bitcoin uda diya'
            collection_buyer.remove({'transaction_id':buyer['transaction_id']})
            print 'removed'
        elif bitcoins_remaning > 0:
            print 'bitcoin ghata diya'
            print bitcoins, amount_paid
            collection_buyer.update({'transaction_id':buyer['transaction_id']},{
                '$inc' : {
                    'deposit': -amount_paid
                }
            })
        # , {'$inc': {'bitcoins': self.bitcoins}}
        else:
            raise Exception('Bitcoin Is Negative')




    def market_processing_for_seller(self):
        buyer = collection_buyer.find_one({'price':self.price_per_btc,
                                           'user':{'$ne':self.userId}})
        seller_record = {
            'user' : self.userId,
            'price' : self.price_per_btc,
            'bitcoins' : self.bitcoins,
            'transaction_id' : self.transactionId
        }
        if buyer == None:
            collection_seller.insert(seller_record)
            del seller_record['user']
            collection_account.update({'_id':ObjectId(self.userId)},{'$push':{'pending_orders.selling':seller_record}})
        else:
            i_can_only_buy = buyer['deposit'] / self.price_per_btc
            buyer['bitcoins'] = i_can_only_buy
            if i_can_only_buy >= self.bitcoins:
                #give bitcoins
                amount_paid = self.bitcoins * self.price_per_btc
                self.give_bitcoin(bitcoins=self.bitcoins,buyer=buyer,amount_paid=amount_paid)
                #take money
                print amount_paid
                seller_record['amount_recieved'] = amount_paid
                collection_account.update({'_id':ObjectId(self.userId)},{
                    '$inc' : {'account_balance':amount_paid},
                    '$push' : {
                        'account_history.sold' : seller_record
                    }
                })
                print 'poora ho gya'
            else:
                #jitna hai utna le lo
                remaning_bitcoin = self.bitcoins - i_can_only_buy
                amount_paid = i_can_only_buy * self.price_per_btc
                self.give_bitcoin(bitcoins=i_can_only_buy, buyer=buyer, amount_paid=amount_paid)
                seller_record['amount_recieved'] = amount_paid
                seller_record['bitcoins'] = buyer['bitcoins']
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
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':


    mohit = seller(userId='582ec729f99ce62a1ac41ee4',price_per_btc=5000,bitcoins=0.8,st= st)
    mohit.market_processing_for_seller()
    mohit = buyer("582ec573f99ce6291025082c",5000,transact_amount=8000,st=st)
    mohit.market_processing_for_buyer()

    #
    # mohit = seller(userId='582ec729f99ce62a1ac41ee4',price_per_btc=5000,bitcoins=0.8,st= st)
    # collection_account.update({'_id':ObjectId(mohit.userId)},{'account_balance':0,
    #                 'bitcoins':2.089,
    #                 'pending_orders': {
    #                     'selling': [],
    #                     'buying': []
    #                 },
    #                 'account_history':{
    #                     'sold':[],
    #                     'bought':[]
    #                 }})
    # mohit = buyer("582ec573f99ce6291025082c",5000,transact_amount=8000,st=st)
    # collection_account.update({'_id':ObjectId(mohit.userId)},{'account_balance':0,
    #                 'bitcoins':2.089,
    #                 'pending_orders': {
    #                     'selling': [],
    #                     'buying': []
    #                 },
    #                 'account_history':{
    #                     'sold':[],
    #                     'bought':[]
    #                 }})
    # collection_seller.drop()
    # collection_buyer.drop()
