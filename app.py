
from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup

nav = Nav()

# Navbar for Web app
@nav.navigation()
def mynavbar():
    if 'username' in login_session:
        return Navbar(
            'Item Catalog',
            View('Home', 'mainPage'),
            Subgroup(login_session['username'],
                View('Create Item', 'createItem'),
                View('My Items', 'showUserItems', user_id=getUserId(login_session['email'])),
                View('Logout', 'disconnect')
            )
        )

    return Navbar(
        'Item Catalog',
        View('Home', 'mainPage'),
        View('Login', 'showLogin')
    )


app = Flask(__name__)
Bootstrap(app)
nav.init_app(app)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item, User

# Auth Imports
from flask import session as login_session
import random, string

# Google OAuth imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

# DB init
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine

# Get G+ API CID and CSECRET from client_secrets.json
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Decorator for requiring login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        else:
            return f(*args, **kwargs)
    return wrap

# Function for creating DB sessions
def createDbSession():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

# User Creation 
def createUser(login_session):
    session = createDbSession()
    newUser = User(username = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

# Get information of user
def getUserInfo(user_id):
    session = createDbSession()
    user = session.query(User).filter_by(id = user_id).one()
    return user

# Checks if the email has a user, if so return user id
def getUserId(email):
    try:
        session = createDbSession()
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

# Check if user has permissions to edit/delete
def isOwner(user_id, target):
    print(user_id)
    print(target)
    if user_id == target:
        print("true")
        return True
    else:
        print("false")
        return False

# -----------------------------------LOGIN ROUTES----------------------------------------------

# Login Route
@app.route('/login')
def showLogin():
    # Creates a random string with 32 characters AKA State Variable which we store in the login session
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login_options.html', STATE=state)

# General Disconnect Route
@app.route('/disconnect')
def disconnect():
    if "provider" in login_session:
        if login_session['provider'] == 'google':
            print("google client")
            gdisconnect()
        del login_session['provider']
        del login_session['username']
        del login_session['email']
        flash("You have successfully been logged out.")
        return redirect(url_for('mainPage'))
    else:
        flash("You are not logged in")
        return redirect(url_for('mainPage'))

# Google Auth Route
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='') # Creates oauthflow object and adds the client secret file's key information into it
        oauth_flow.redirect_uri = 'postmessage' # Specify post message that this is the one time code that the server will send off
        credentials = oauth_flow.step2_exchange(code) # Initiates the key exchange, passing in the onetime code as the exchange, exchanges the code for a credentials object
                                                      # The response from google server should be a credential object
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code. '), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}'.format(access_token=access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'

    # Check if access token is the correct token for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."),401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected. '),200)
        response.headers['Content-Type'] = 'application/json'

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo" # Data scope
    params = {
        'access_token': credentials.access_token,
        'alt':'json'
    }
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # Set user info to session
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    if getUserId(login_session['email']) is None:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id

    flash("You are now logged in as {username}".format(username=login_session['username']))
    return "You've sucessfully logged in as: <strong>{username}</strong>".format(username=login_session['username'])

# Google Disconnect Route
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token={access_token}'.format(access_token=access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        print("i'm here")
        #Reset user's session
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected!'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response


# --------------------------------------LOGIN ROUTES END--------------------------------------


# -----------------------------------Route Handlers--------------------------------------------

# Main route/ Root route
@app.route('/')
@app.route('/catalog/')
def mainPage():
    session = createDbSession()
    category = session.query(Category).all()
    items = session.query(Item).limit(5)
    return render_template('main.html', categories=category, items=items)


# JSON Route (Items Index Route)
@app.route('/v1/catalog/items/')
def jsonCatalog():
    session = createDbSession()
    items = session.query(Item).all()
    return jsonify(CatalogItems=[item.serialize for item in items])

# Show Create Page
@app.route('/catalog/create/', methods=['GET','POST'])
@login_required
def createItem():
    session = createDbSession()
    user = session.query(User).filter_by(id=getUserId(login_session.get("email"))).first()
    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('item_create_page.html', categories=categories, user=user)
    elif request.method == 'POST':
        try:
            itemToCreate = Item(name=request.form.get("name"), 
            description=request.form.get("description"), 
            category_id = request.form.get("category"), 
            owner_id=getUserId(login_session["email"]))
            if itemToCreate.name is not None and itemToCreate.description is not None and itemToCreate.category_id is not None:
                session.add(itemToCreate)
                session.commit()
                item = session.query(Item).filter_by(name=itemToCreate.name).first()
                return redirect(url_for("showItem",category_id=itemToCreate.category_id, item_id=item.id))
            else:
                print("Form invalid, fields all need to be filled")
                return redirect("/")
        except Exception as e:
            print("Error {error}".format(error=e))
            return redirect('/')
    

# Show Category Items
@app.route('/catalog/<int:category_id>/')
def showCategoryItems(category_id):
    session = createDbSession()
    items = session.query(Item).filter_by(category_id=category_id).all()
    category = session.query(Category).filter_by(id=category_id).first()
    return render_template('category_items.html', items=items, category=category)


# Show User Items
@app.route('/catalog/items/<int:user_id>/')
@login_required
def showUserItems(user_id):
    session = createDbSession()
    items = session.query(Item).filter_by(owner_id=user_id).all()
    user = session.query(User).filter_by(id=user_id).one()
    return render_template("user_items.html", items=items, user=user)

# Show Item Page
@app.route('/catalog/<int:category_id>/<int:item_id>/', methods= ["GET","POST"])
def showItem(category_id, item_id):
    session = createDbSession()
    item = session.query(Item).filter_by(id=item_id).first()
    category = session.query(Category).filter_by(id=category_id).first()
    print("{email} : {id}".format(email=getUserId(login_session.get("email")), id = item.owner_id))
    if request.method == "GET" and isOwner(getUserId(login_session.get("email")), item.owner_id):
        return render_template('item_page.html', item=item, category=category)
    else:
        return render_template("public_item_page.html", item=item, category=category)


# Show Item Edit Page
@app.route('/catalog/<int:category_id>/<int:item_id>/edit/', methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    session = createDbSession()
    item = session.query(Item).filter_by(id=item_id).first()
    if request.method == 'GET' and isOwner(getUserId(login_session["email"]), item.owner_id):
        categories = session.query(Category).all()
        return render_template('item_edit_page.html', item=item, categories=categories)
    elif request.method == "POST" and isOwner(getUserId(login_session["email"]), item.owner_id):
        try:
            itemToUpdate = session.query(Item).filter_by(id=item_id).first()
            itemToUpdate.name = request.form.get("name")
            itemToUpdate.description = request.form.get("description")
            itemToUpdate.category_id = request.form.get("category")
            if itemToUpdate.name is not None and itemToUpdate.description is not None and itemToUpdate.category_id is not None:
                session.add(itemToUpdate)
                session.commit()
                return redirect(url_for("showItem",category_id=itemToUpdate.category_id, item_id=item_id))
            else:
                return redirect("/")
        except Exception as e:
            print("Error {error}".format(error=e))
            return url_for("showItem", category_id=category_id, item_id= item_id)
    else:
        return make_response(json.dumps("You are not the owner of this item!"),401)

# Delete Item Page
@app.route('/catalog/<int:category_id>/<int:item_id>/delete/', methods=['GET','POST'])
@login_required
def deleteItem(category_id, item_id):
    session = createDbSession()
    item = session.query(Item).filter_by(id=item_id).first()
    if request.method == 'GET' and isOwner(getUserId(login_session["email"]), item.owner_id):
        return render_template('item_delete_page.html', item=item)
    elif request.method == 'POST' and isOwner(getUserId(login_session["email"]), item.owner_id):
        try:
            item = session.query(Item).filter_by(id=item_id).first()
            session.delete(item)
            session.commit()
            return redirect(url_for('showCategoryItems', category_id=category_id))
        except Exception as e:
            print('Failed to delete {itemName}. Error: {error}'.format(itemName=item.name, error=e))
            return redirect(url_for('/'))
    else:
        return make_response(json.dumps("You are not the owner of this item!"),401)    
# ----------------------------------Route Handlers End--------------------------------------

if __name__ == '__main__':
    app.secret_key = 'super_secret_key_that_is_not_so_secret_now'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)