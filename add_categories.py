from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def createCategory(name):
    newCategory = Category(name=name)
    try:
        session.add(newCategory)
        session.commit()
        print("Created {categoryName}".format(categoryName=name))
    except Exception as e:
        print("Unable to add {categoryName}".format(categoryName=name))
        print(e)

# Add a bunch of categories into DB

createCategory("Winter Tires")
createCategory("All Season Tires")
createCategory("Summer Tires")
createCategory("Extreme Summer Tires")