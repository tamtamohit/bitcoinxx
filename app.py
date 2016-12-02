# -*- coding: utf-8 -*-
"""
Flask API run file
"""
from flask import Flask, render_template, request, redirect,flash, session
from pymongo.errors import DuplicateKeyError
from content_management import content, last_trade_price
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from market import buyer,seller




TOPIC_DICT= content()

app = Flask(__name__)
app.secret_key = 'mohitdevops'
mongo = PyMongo(app)


@app.route('/')
def firstpage():
        return redirect('/home')

@app.route('/home')
def homepage():
    if not 'logged_in' in session:
        return render_template('home.html',TOPIC_DICT=content(),LoggedIN = True)
    elif session['logged_in'] == False:
        return render_template('home.html',TOPIC_DICT=content(),LoggedIN = True)
    else:
        return render_template('home.html',TOPIC_DICT=content(),LoggedIN = False)

@app.route('/trade')
def livemarket():
    if session['logged_in'] == True:
        PENDING_ORDERS = mongo.db.account.find_one({'_id':ObjectId(session['_id'])},{'pending_orders':1,'_id':0})['pending_orders']
        return render_template('trade.html',TOPIC_DICT=content(trade=True),PENDING_ORDERS=PENDING_ORDERS)
    else:
        return redirect('/login')


@app.route('/addmoney', methods=['GET','POST'])
def addbitcoin():
    if request.method == 'GET':
        if session['logged_in'] == True:
            return render_template('add_money.html', TOPIC_DICT=content())
        else:
            return redirect('/login')
    if request.method == 'POST':
        if session['logged_in'] == True:
            if request.form['payment'] == 'Pay':
                added_money = request.form.get('amount')
                person_account_details =  mongo.db.account.find_one({'_id':ObjectId(session['_id'])})
                person_account_details['account_balance'] = person_account_details['account_balance'] + int(added_money)
                del person_account_details['_id']
                mongo.db.account.update({'_id':ObjectId(session['_id'])},person_account_details)
                return redirect('/wallet')
            elif request.form['payment'] == 'Skip':
                return redirect('/wallet')



        else:
            return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        database_user = mongo.db.users.find_one({'email':email,'password':password})
        if database_user is None:
            # flash('Invalid Username/Password','error')
            return redirect('/login')
        session['logged_in'] = True
        session['_id'] = str(database_user['_id'])

        # flash('Loggedin Successfuly')
        return redirect('/wallet')

    if request.method == 'GET':
        return render_template('login.html',TOPIC_DICT=content())

@app.route('/newlogin')
def here_login():

    if session['logged_in'] == True:
        # flash(u'You are loggedin')
        print 'passed'

    else:
        flash('Login First')
    return render_template('test.html', TOPIC_DICT=content())


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['_id'] = None
    return redirect('/')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first = request.form.get('first')
        last = request.form.get('last')
        email =  request.form.get('email')
        password =  request.form.get('password')
        confirm =  request.form.get('confirm')
        if password == confirm:
            user = {'first': first, 'last': last, 'email': email, 'password': password, 'confirmed': False}
            # mongo.db.users.delete({u'email': u'mohit.tamta@grownout.com'})
            try:
                mongo.db.users.insert(user)
            except:
                return redirect('/login')


            user_id = mongo.db.users.find_one({'email': email, 'password': password})['_id']
            session['logged_in'] = True
            session['_id'] = str(user_id)

            mongo.db.account.insert({
                '_id':ObjectId(user_id),
                'account_balance':0,
                'bitcoins':0,
                'pending_orders': {
                    'selling': [],
                    'buying': []
                },
                'account_history':{
                    'sold':[],
                    'bought':[]
                }
            })
            return redirect('/home')
    return render_template('register.html', TOPIC_DICT=content())



@app.route('/confirm/<token>')
def confirm_email(token):
    try: email = confirm_email(token)
    except: flash('The confirmation link is invalid or has expired.', 'danger')


@app.route('/sellbtc',methods=['GET','POST'])
def sellbtc():
    account = account_details()
    if len(account['pending_orders']['selling']) == 0:
        if request.method == 'GET':
            # price_per_bitcoin = 50000
            return render_template('sell_btc.html',TOPIC_DICT=content(trade=True),person_account_details=account['bitcoins'],price_per_bitcoin=last_trade_price())
        if request.method == 'POST':
            if request.form.get('btcSellingVolume') < account['bitcoins']:
                return
            bitcoins =  request.form.get('btcSellingVolume')
            price_per_bitcoin = request.form.get('btcSellingPrice')
            new_sell = seller(userId=session['_id'],price_per_btc=price_per_bitcoin,bitcoins=bitcoins)
            new_sell.market_processing_for_seller()

            return redirect('/trade')
    else:
        return redirect('/updatesell')



@app.route('/updatesell', methods=['GET', 'POST'])
def update_sell_btc():
    # price_per_bitcoin = 50000
    account = account_details()
    if len(account['pending_orders']['selling']) > 0:
        if request.method == 'GET':
            return render_template('update_sell.html',TOPIC_DICT=content(trade=True),
                 person_account_details=account['bitcoins'], price_per_bitcoin = account['pending_orders']['selling'][0]['price'])
        else:

            if request.form.get('submit') == 'update':
                if request.form.get('btcSellingVolume') < account['bitcoins']:
                    return
                price =  request.form.get('btcSellingPrice')
                volume =  request.form.get('btcSellingVolume')
                update_sell_bid(price=price,volume=volume,
                                transactionId=account['pending_orders']['selling'][0]['transaction_id'])
                return redirect('/trade')
            elif request.form.get('submit') == 'cancel':
                return redirect('/wallet')
    else:
        return redirect('/sellbtc')




def update_sell_bid(price,volume,transactionId):
    seller_updater = seller(userId=ObjectId(session['_id']),price_per_btc=price,
                            bitcoins=volume,transactionId=transactionId)
    seller_updater.market_processing_for_seller()





@app.route('/wallet',methods=['GET','POST'])
def wallet():
    if not 'logged_in' in session:
        session['logged_in'] = False
        return redirect('/login')
    elif session['logged_in'] == True:
        if request.method == 'GET':
            account = account_details()
            return render_template('wallet.html',TOPIC_DICT=content(trade=True),account=account)
        else:
            if request.form.get('submit') == 'add_money':
                return redirect('/addmoney')
            elif request.form.get('submit') == 'buy_bitcoins':
                return redirect('/buybtc')
            return redirect('/wallet')
    else:
        return redirect('/login')


@app.route('/buybtc',methods=['GET','POST'])
def buy_request():
    if request.method == 'GET':
        if session['logged_in'] == True:
            account = account_details()
            if len(account['pending_orders']['buying']) == 0:
                return render_template('buy_btc.html',TOPIC_DICT=content(trade=True),price_per_bitcoin=last_trade_price(),
                                       account_balance=account['account_balance'])
            else:
                return redirect('/updatebuy')
        else:
            return redirect('/login')
    if request.method == 'POST':
        #verify he is not making another transaction
        price_per_bitcoin = request.form.get('price')
        amount = request.form.get('amount')
        buying_request = buyer(userId=session['_id'],price_per_btc=price_per_bitcoin,transact_amount=amount)
        buying_request.market_processing_for_buyer()

        return redirect('/trade')


def update_buying_bid(transaction_id,price,deposit):
    buying = buyer(userId=session['_id'],price_per_btc=price,
                   transact_amount=deposit,transaction_id=transaction_id)
    buying.market_processing_for_buyer()



@app.route('/updatebuy',methods=['GET','POST'])
def update_buy():
    account = account_details()
    if len(account['pending_orders']['buying']) == 0:
        return redirect('/buybtc')
    else:
        if request.method == 'GET':
            return render_template('update_buy.html', TOPIC_DICT=content(trade=True), price_per_bitcoin=account['pending_orders']['buying'][0]['price'],
                               PENDING_ORDER=account['pending_orders']['buying'][0],account_balance=account['account_balance'])

        if request.method == "POST":
            if request.form.get('button') == 'cancel':
                return redirect('/wallet')
            elif request.form.get('button') == 'update':
                price = request.form.get('price')
                print price
                deposit = request.form.get('amount')
                update_buying_bid(transaction_id=account['pending_orders']['buying'][0]['transaction_id'],
                                  price=float(price),deposit=float(deposit))
                return redirect('/trade')




def account_details():
    return mongo.db.account.find_one({'_id':ObjectId(session['_id'])})

@app.route('/charts',methods=['GET'])
def chart():
    return render_template('charts.html',TOPIC_DICT=content())



if __name__ == "__main__":
        app.run(debug= True,threaded=True)