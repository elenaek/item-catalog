from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine


def createDBSession():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

def createCategory(name):
    session = createDBSession()
    newCategory = Category(name=name)
    if session.query(Category).filter_by(name=name).first() is not None:
        return "This category already exists!"
    else:
        try:
            session.add(newCategory)
            session.commit()
            print("Created {categoryName}".format(categoryName=name))
        except Exception as e:
            print("Unable to add {categoryName}".format(categoryName=name))
            print(e)

# Add a bunch of categories into DB

def addItem(name, category_id, description):
    session = createDBSession()
    if session.query(Item).filter_by(name=name).first() is not None:
        return "This item already exists!"
    else:
        newItem = Item(name=name, category_id=category_id, description=description)
        session.add(newItem)
        session.commit()
        category = session.query(Category).filter_by(id=category_id).first()
        print("Created {itemName} under the {categoryName} category!".format(itemName=name, categoryName=category.name))

createCategory("Winter Tires")
createCategory("All Season Tires")
createCategory("Summer Tires")
createCategory("Extreme Summer Tires")
addItem("re-71r",3,"Some reaaal good tires, man!")