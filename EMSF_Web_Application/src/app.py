#import sys
#sys.path.insert(0,
#'C:/Users/hang/source/repos/EMSF_Web_Application-/EMSF_Web_Application/src')


#to do 
#insert png picture into the correct folder 
#search about store mongoDB keys with dot 
#retrieve the correct form of data/right ordering of from mongoDB
#clean up documents

from common.database import Database
from models.portfolio import Portfolio
from models.asset import Asset
from models.user import User
import json

from test import *
from test.main_engine import *

__author__ = 'hckerhx'

from flask import Flask, render_template, request, session, make_response, url_for, redirect

app = Flask(__name__)  # '__main__'
app.secret_key = "hckerhx"

@app.route('/')
def home_template():
    return render_template('home.html')

@app.route('/home', methods=['GET']) #get(read url from backend)/post(write data files or json to backend)
def home():
    return render_template("Pprofile.html", email=session['email']) #if not session/flask check session exists

@app.route('/login')
def login_template():
    return render_template('Llogin.html')

@app.route('/register')
def register_template():
    return render_template('Rregister.html')

@app.before_first_request
def initialize_database():
    Database.initialize()

@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email'] # HTML comment
    password = request.form['password'] # encryption (hash password/enter into database and compare)

    if User.login_valid(email, password):
        User.login(email)

    # if user account does not exist
    else:
        session['email'] = "this account does not exist"

    return render_template("Pprofile.html", email=session['email'])

@app.route('/logout')
def logout_user():  # Logs user out
    session['email'] = None
    #print(url_for('login'))
    return redirect(url_for('login_template'))

@app.route('/auth/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password'] # encryption (hash password)
    conf_password = request.form['conf_password'] 
    
    if password == conf_password:
        User.register(email, password)
    else:
        return render_template("Rregister.html", email=email, password=password,conf_password=conf_password)

    return render_template("Pprofile.html", email=session['email'])

@app.route('/bresult', methods=['POST', 'GET'])
def user_bresult():
    u_result = Database.find_one(collection='result',
                                      query={'user_email': session['email'], 'objective': 'b'})

    p_return = u_result['stats']['total_return']
    p_sharpe = u_result['stats']['sharpe']

    #display profit and sharpe ratio on the website 

    return render_template("Rresultb.html", p_return = p_return, p_sharpe = p_sharpe)#profit and sharpe ratio

@app.route('/backtesting', methods=['POST', 'GET'])
def user_portfolio():
    if request.method == 'POST':
        new_asset = {}
        new_asset['user_email'] = session['email']
        new_asset['weight'] = {}

        for i in range(1,501):
            if request.form.get('asset' + str(i)) != None:
                asset = request.form.get('asset' + str(i))
                weight = float(request.form.get('weight' + str(i)))
                new_asset['weight'][asset] = weight
            else:
                break

        new_asset['target_return'] = request.form.get('target_return')
        new_asset['start_date'] = request.form.get('start_date')
        new_asset['end_date'] = request.form.get('end_date')

        asset_data = None
        user_input = None
        id_ticker_mapping = None
        ticker_id_mapping = None
        factor_data = None

        with open("test/asset_data.json", "r") as asset_data_in:
            asset_data = json.load(asset_data_in)
        with open("test/user_input.json", "r") as user_input_in:
            user_input = json.load(user_input_in)
        with open("test/id_ticker_mapping.json", "r") as id_ticker_mapping_in:
            id_ticker_mapping = json.load(id_ticker_mapping_in)
        with open("test/ticker_id_mapping.json", "r") as ticker_id_mapping_in:
            ticker_id_mapping = json.load(ticker_id_mapping_in)
        with open("test/factor_data.json", "r") as factor_data_in:
            factor_data = json.load(factor_data_in)

        result = main_flow(asset_data, "Back-testing", new_asset, id_ticker_mapping, ticker_id_mapping, factor_data)
        result['user_email'] = session['email']
        
        Database.insert(collection='portfolio', data=new_asset)
        Database.insert(collection='result', data=result)
        
    return render_template('Bbacktesting.html')


@app.route('/dresult', methods=['POST', 'GET'])
def user_dresult():
    u_result = Database.find_one(collection='result',
                                      query={'user_email': session['email'], 'objective': 'd'})
    print('u_test =', u_result)
    p_return = u_result['original_value']['stats']['total_return']
    p_sharpe = u_result['original_value']['stats']['sharpe']

    #display profit and sharpe ratio on the website 

    return render_template("Rresultd.html", p_return = p_return, p_sharpe = p_sharpe)#profit and sharpe ratio

@app.route('/portdomi', methods=['POST', 'GET'])
def user_portfolio_domi():
    
    if request.method == 'POST':
        new_asset = {}
        new_asset['user_email'] = session['email']
        new_asset['weight'] = {}

        for i in range(1,501):
            if request.form.get('asset' + str(i)) != None:
                asset = request.form.get('asset' + str(i))
                weight = float(request.form.get('weight' + str(i)))
                new_asset['weight'][asset] = weight
            else:
                break

        #new_asset['target_return'] = request.form.get('target_return')
        new_asset['start_date'] = request.form.get('start_date')
        new_asset['end_date'] = request.form.get('end_date')

        asset_data = None
        user_input = None
        id_ticker_mapping = None
        ticker_id_mapping = None
        factor_data = None

        with open("test/asset_data.json", "r") as asset_data_in:
            asset_data = json.load(asset_data_in)
        with open("test/user_input.json", "r") as user_input_in:
            user_input = json.load(user_input_in)
        with open("test/id_ticker_mapping.json", "r") as id_ticker_mapping_in:
            id_ticker_mapping = json.load(id_ticker_mapping_in)
        with open("test/ticker_id_mapping.json", "r") as ticker_id_mapping_in:
            ticker_id_mapping = json.load(ticker_id_mapping_in)
        with open("test/factor_data.json", "r") as factor_data_in:
            factor_data = json.load(factor_data_in)

        print(new_asset)
        result = main_flow(asset_data, "Portfolio-domi", new_asset, id_ticker_mapping, ticker_id_mapping, factor_data)
        result['user_email'] = session['email']
        print(result)
        
        Database.insert(collection='portfolio', data=new_asset)
        Database.insert(collection='result', data=result)

    return render_template('Pportdom.html')

@app.route('/cresult', methods=['POST', 'GET'])
def user_cresult():
    u_result = Database.find_one(collection='result',
                                      query={'user_email': session['email'], 'objective': 'c'})

    p_return = u_result['stats']['total_return']
    p_sharpe = u_result['stats']['sharpe']

    #display profit and sharpe ratio on the website 

    return render_template("Rresultc.html", p_return = p_return, p_sharpe = p_sharpe)#profit and sharpe ratio

@app.route('/port_construct', methods=['POST', 'GET'])
def user_portfolio_construct():
    if request.method == 'POST':
        new_asset = {}
        new_asset['user_email'] = session['email']
        #new_asset['weight'] = {}

        new_asset['target_return'] = float(request.form.get('target_return'))
        #new_asset['start_date'] = request.form.get('start_date')
        #new_asset['end_date'] = request.form.get('end_date')

        #new_asset['investment_length'] = int(request.form.get('investment_length'))

        asset_data = None
        user_input = None
        id_ticker_mapping = None
        ticker_id_mapping = None
        factor_data = None

        with open("test/asset_data.json", "r") as asset_data_in:
            asset_data = json.load(asset_data_in)
        with open("test/user_input.json", "r") as user_input_in:
            user_input = json.load(user_input_in)
        with open("test/id_ticker_mapping.json", "r") as id_ticker_mapping_in:
            id_ticker_mapping = json.load(id_ticker_mapping_in)
        with open("test/ticker_id_mapping.json", "r") as ticker_id_mapping_in:
            ticker_id_mapping = json.load(ticker_id_mapping_in)
        with open("test/factor_data.json", "r") as factor_data_in:
            factor_data = json.load(factor_data_in)

        print('new asset =', new_asset)
        result = main_flow(asset_data, "Portfolio-Construction", new_asset, id_ticker_mapping, ticker_id_mapping, factor_data)
        print('result = ', result)
        result['user_email'] = session['email']
        
        Database.insert(collection='portfolio', data=new_asset)
        Database.insert(collection='result', data=result)

    return render_template('Pportcons.html')
    #if request.method == 'GET':
    #    return render_template('Pportcons.html')


#@app.route('/blogs/<string:user_id>')
#@app.route('/blogs')
#def user_blogs(user_id=None):
#    if user_id is not None:
#        user = User.get_by_id(user_id)
#    else:
#        user = User.get_by_email(session['email'])

#    blogs = user.get_blogs()

#    return render_template("user_blogs.html", blogs=blogs, email=user.email)


#@app.route('/blogs/new', methods=['POST', 'GET'])
#def create_new_blog():
#    if request.method == 'GET':
#        return render_template('new_blog.html')
#    else:
#        title = request.form['title']
#        description = request.form['description']
#        user = User.get_by_email(session['email'])

#        new_blog = Blog(user.email, title, description, user._id)
#        new_blog.save_to_mongo()

#        return make_response(user_blogs(user._id))

@app.route('/asset/<string:portfolio_id>')
def portfolio_asset(portfolio_id=None):
    user = User.get_by_email(session['email'])

    portfolio = user.get_portfolio()
    portfolio = Portfolio.from_mongo(portfolio_id)
    asset = portfolio.get_asset()

    return render_template('Aasset.html', posts=posts, portfolio_title=portfolio.title, portfolio_id=portfolio._id)


@app.route('/asset/new/<string:portfolio_id>', methods=['POST', 'GET'])
def create_new_asset(portfolio_id):
    if request.method == 'GET':
        return render_template('Nnewasset.html', portfolio_id=portfolio_id)
    else:
        asset_name = request.form['asset_name']
        content = request.form['asset_weight']
        user = User.get_by_email(session['email'])

        new_asset = Post(portfolio_id, title, content, user.email)
        new_asset.save_to_mongo()

        return make_response(portfolio_posts(portfolio_id))


if __name__ == '__main__':
    app.run(port=4995, debug=True)
