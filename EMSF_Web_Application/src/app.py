from common.database import Database
from models.portfolio import Portfolio
from models.asset import Asset
from models.user import User

__author__ = 'jslvtr'

from flask import Flask, render_template, request, session, make_response, url_for

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
    return redirect(url_for('home'))

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

@app.route('/backtesting', methods=['POST', 'GET'])
def user_portfolio():
    if request.method == 'GET':
        return render_template('Bbacktesting.html')
    
    #else:
    #    asset_name = request.form['asset']
    #    asset_weight = request.form['weight']
    #    starting_time = request.form['starting_time']
    #    ending_time = request.form['ending_time']

    #    asset_entry = asset(asset_name, asset_weight, starting_time, ending_time)
    #    asset_entry.save_to_mongo()

    #    return make_response()
    #request.form['assets']
    #request.form['portfolio weights']
    #request.form['starting date']
    #request.form['ending date']
    

@app.route('/portdomi', methods=['POST', 'GET'])
def user_portfolio_domi():
    if request.method == 'GET':
        return render_template('Pportdom.html')
    '''
    request.form['assets']
    request.form['portfolio weights']
    request.form['starting date']
    request.form['ending date']
    '''

@app.route('/port_construct', methods=['POST', 'GET'])
def user_portfolio_construct():
    if request.method == 'GET':
        return render_template('Pportcons.html')

    '''
    request.form['targeted return goal']
    request.form['starting date']
    request.form['ending date']
    '''

@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])

    blogs = user.get_blogs()

    return render_template("user_blogs.html", blogs=blogs, email=user.email)


@app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])

        new_blog = Blog(user.email, title, description, user._id)
        new_blog.save_to_mongo()

        return make_response(user_blogs(user._id))


@app.route('/asset/<string:blog_id>')
def portfolio_asset(portfolio_id):
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
