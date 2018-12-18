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

# Show Create Page
@app.route('/catalog/create', methods=['GET','POST'])
def createItem():
    session = createDbSession()
    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('item_create_page.html', categories=categories)
    

# Show Category Items
@app.route('/catalog/<int:category_id>')
def showCategoryItems(category_id):
    session = createDbSession()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('category_items.html', items=items)


# Show Item Page
@app.route('/catalog/<int:category_id>/<int:item_id>', methods= ["GET","POST"])
def showItem(category_id, item_id):
    session = createDbSession()
    if request.method == "GET":
        item = session.query(Item).filter_by(id=item_id).first()
        return render_template('item_page.html', item=item)


# Show Item Edit Page
@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    session = createDbSession()
    if request.method == 'GET':
        item = session.query(Item).filter_by(id=item_id).first()
        categories = session.query(Category).all()
        return render_template('item_edit_page.html', item=item, categories=categories)
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

# Delete Item Page
@app.route('/catalog/<int:category_id>/<int:item_id>/delete', methods=['GET','POST'])
def deleteItem(category_id, item_id):
    session = createDbSession()
    
    if request.method == 'GET':
        item = session.query(Item).filter_by(id=item_id).first()
        return render_template('item_delete_page.html', item=item)

    elif request.method == 'POST':
        try:
            item = session.query(Item).filter_by(id=item_id).first()
            session.delete(item)
            session.commit()
        except Exception as e:
            print('Failed to delete {itemName}. Error: {error}'.format(itemName=item.name, error=e))
            return redirect(url_for('/'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)