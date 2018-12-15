from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine


def createDbSession():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

# Main route/ Root route
@app.route('/')
def mainPage():
    session = createDbSession()
    category = session.query(Category).all()
    return render_template('main.html', categories=category)

# Show Items in Category
@app.route('/catalog/<int:category_id>')
def showCategory(category_id):
    session = createDbSession()
    category = session.query(Category).filter_by(id=category_id)
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('category_items.html', items=items)

# Show Item Page
@app.route('/catalog/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
    session = createDbSession()
    item = session.query(Item).filter_by(id=item_id).first()
    return render_template('item_page.html', item=item)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)