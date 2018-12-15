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

# Show and Create Item Page
@app.route('/catalog/<int:category_id>/<int:item_id>', methods= ["GET","POST"])
def interactItem(category_id, item_id):
    session = createDbSession()
    if request.method == "GET":
        item = session.query(Item).filter_by(id=item_id).first()
        return render_template('item_page.html', item=item)
    elif request.method == "POST":
        try:
            itemToUpdate = session.query(Item).filter_by(id=item_id).first()
            itemToUpdate.name = request.form.get("name")
            itemToUpdate.description = request.form.get("description")
            itemToUpdate.category_id = request.form.get("category")
            if itemToUpdate.name is not None and itemToUpdate.description is not None and itemToUpdate.category_id is not None:
                session.add(itemToUpdate)
                session.commit()
                return redirect(url_for("interactItem",category_id=itemToUpdate.category_id, item_id=item_id))
            else:
                return redirect("/")
        except Exception as e:
            print("Error {error}".format(error=e))
            return url_for("interactItem", category_id=category_id, item_id= item_id)

# Show Item Edit Page
@app.route('/catalog/<int:category_id>/<int:item_id>/edit')
def editItem(category_id, item_id):
    session = createDbSession()
    item = session.query(Item).filter_by(id=item_id).first()
    categories = session.query(Category).all()
    return render_template('item_edit_page.html', item=item, categories=categories)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)