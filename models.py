from sqlalchemy import Column,Integer,String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password = Column(String(64))

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    @property
    def serialize(self):
	    """Return object data in easily serializeable format"""
	    return {
	    'username' : self.username
	        }


class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	@property
	def serialize(self):
	    return {
	    'name' : self.name
	        }

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(String, ForeignKey('user.id'))
    category_id = Column(String, ForeignKey('category.id'))
    user = relationship(User)
    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        'title' : self.title,
        'description' : self.description
            }


engine = create_engine('sqlite:///itemCatalog.db')
 

Base.metadata.create_all(engine)