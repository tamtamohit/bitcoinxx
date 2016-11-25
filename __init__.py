# -*- coding: utf-8 -*-
"""
Flask API run file
"""
from flask import Flask, render_template, request, redirect, url_for,flash, session
from pymongo.errors import DuplicateKeyError
# from flask_login import LoginManager,login_user, logout_user, current_user, login_required
from content_management import content
from flask_pymongo import PyMongo
from itsdangerous import URLSafeTimedSerializer
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from User import User
import datetime, time
from bson.objectid import ObjectId
from market import buyer,seller




TOPIC_DICT= content()

app = Flask(__name__)
app.secret_key = 'mohitdevops'
mongo = PyMongo(app)


# if session['logged_in'] == None:
#     session['logged_in'] = False






@app.route('/')
def firstpage():
        return render_template('home.html',TOPIC_DICT=content())

@app.route('/home')
def homepage():
    if not 'logged_in' in session:
        session['logged_in'] = False

    return render_template('home.html',TOPIC_DICT=content())

@app.route('/trade')
def livemarket():
    PENDING_ORDERS = mongo.db.account.find_one({'_id':ObjectId(session['_id'])},{'pending_orders':1,'_id':0})['pending_orders']
    print PENDING_ORDERS
    return render_template('trade.html',TOPIC_DICT=content(trade=True),PENDING_ORDERS=PENDING_ORDERS)


@app.route('/addmoney', methods=['GET','POST'])
def addbitcoin():
    if request.method == 'GET':
        if session['logged_in'] == True:
            return render_template('add_money.html', TOPIC_DICT=content())
        else:
            return redirect('/login')
    if request.method == 'POST':
        # print request.method
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
        return redirect('/newlogin')

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
    if request.method == 'GET':
        person_account_details = mongo.db.account.find_one({'_id': ObjectId(session['_id'])})['bitcoins']
        price_per_bitcoin = 50000
        return render_template('sell_btc.html',TOPIC_DICT=content(),person_account_details=person_account_details,price_per_bitcoin=price_per_bitcoin)
    if request.method == 'POST':
        # dbs_sellers_market.insert({})
        bitcoins =  request.form.get('btcSellingVolume')
        price_per_bitcoin = request.form.get('btcSellingPrice')
        new_sell = seller(userId=session['_id'],price_per_btc=price_per_bitcoin,bitcoins=bitcoins)
        new_sell.deduct_bitcoins()
        new_sell.market_processing_for_seller()

        return redirect('/wallet')


# def pending_orders():




@app.route('/wallet',methods=['GET','POST'])
def wallet():
    if not 'logged_in' in session:
        session['logged_in'] = False
    if session['logged_in'] == True:
        account = account_details()
        return render_template('wallet.html',TOPIC_DICT=TOPIC_DICT,account=account)
    else:
        return redirect('/login')


@app.route('/buybtc',methods=['GET','POST'])
def buy_request():
    price_per_bitcoin = 500000
    if request.method == 'GET':
        if session['logged_in'] == True:
            account_balance = mongo.db.account.find_one({'_id': ObjectId(session['_id'])},{'account_balance':1})
            return render_template('buy_btc.html',TOPIC_DICT=content(),price_per_bitcoin=price_per_bitcoin,account_balance=account_balance['account_balance'])
        else:
            return redirect('/login')
    if request.method == 'POST':
        price_per_bitcoin = request.form.get('price')
        amount = request.form.get('amount')
        buying_request = buyer(userId=session['_id'],price_per_btc=price_per_bitcoin,transact_amount=amount)
        buying_request.deduct_money()
        buying_request.market_processing_for_buyer()

        # account_balance = mongo.db.account.find_one({'_id': ObjectId(session['_id'])}, {'account_balance': 1})
        # new_balance = account_balance['account_balance'] - float(amount)
        # mongo.db.account.update({'_id': ObjectId(session['_id'])}, {'$set': {'account_balance': new_balance}})
        # ts = time.time()
        # st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        # mongo.db.buyers_database.insert({'bitcoins':bitcoins,'price':price,'time':st,'user':session['_id']})

        return redirect('/wallet')




def account_details():
    return mongo.db.account.find_one({'_id':ObjectId(session['_id'])})





if __name__ == "__main__":
        app.run(debug= True,threaded=True)
