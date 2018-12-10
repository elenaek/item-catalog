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

@app.route('/')
def mainPage():
    session = createDbSession()
    category = session.query(Category).all()

    # items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('main.html', categories=category)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)