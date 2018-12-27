from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item, User
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

def addItem(name, category_name, description, username):
    session = createDBSession()
    if session.query(Item).filter_by(name=name).first() is not None:
        return "This item already exists!"
    else:
        user = session.query(User).filter_by(username=username).first()
        category = session.query(Category).filter_by(name=category_name).first()
        newItem = Item(name=name, category_id=category.id, description=description, owner_id=user.id)
        session.add(newItem)
        session.commit()
        category = session.query(Category).filter_by(id=category.id).first()
        print("Created {itemName} under the {categoryName} category!".format(itemName=name, categoryName=category.name))

def addUser(username, email):
    session = createDBSession()
    if session.query(User).filter_by(username=username).first() is not None:
        return "This item already exists!"
    else:
        newUser = User(username=username, email=email)
        session.add(newUser)
        session.commit()
        print("Created {userName} with the email {email}".format(userName=username,email=email))

addUser("Some Person","someperson@somecompany.com")
createCategory("Winter Tires")
createCategory("All Season Tires")
createCategory("Summer Tires")
createCategory("Extreme Summer Tires")
addItem("Bridgestone POTENZA RE-71R", "Extreme Summer Tires", """
The Potenza RE-71R is an Extreme Performance Summer tire developed for serious sports car, sports coupe and performance sedan driving enthusiasts looking 
for Bridgestone's fastest DOT-legal street radial. Starting with a clean-sheet approach and a virtual slick tread, all of the design features were 
fine-tuned to maximize performance, traction, handling and control. Performance-tuned for dry and damp conditions, the Potenza RE-71R, like all 
Extreme Performance Summer tires, are not intended to be serviced, stored or driven in near- and below-freezing temperatures, through snow or on ice.
""",
"Some Person")
addItem("Dunlop DIREZZA ZII STAR SPEC", "Extreme Summer Tires", """
The Direzza ZII Star Spec is Dunlop's Extreme Performance Summer tire developed for serious sports car, 
sports coupe and performance sedan enthusiasts looking for race tire-like traction on the street or for use in autocross, drifting and track events.
""",
"Some Person"
)
addItem("Bridgestone BLIZZAK WS80", "Winter Tires", """
If winter has you worried, you can rest easy with the Bridgestone Blizzak WS80 winter tire. Designed for cold weather conditions, 
it delivers excellent braking and accelerating on both ice and snow, and reliable dry weather handling. Get great winter traction and 
responsive handling in dry conditions with the Blizzak WS80 from Bridgestone.
""",
"Some Person"
)