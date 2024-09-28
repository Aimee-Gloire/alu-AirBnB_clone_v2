#!/usr/bin/python3
"""Define storage engine using MySQL database."""
from models.base_model import BaseModel, Base
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from os import getenv

all_classes = {'State': State, 'City': City,
               'User': User, 'Place': Place,
               'Review': Review, 'Amenity': Amenity}

class DBStorage:
    """This class manages MySQL storage using SQLAlchemy.

    Attributes:
        __engine: engine object
        __session: session object
    """
    __engine = None
    __session = None

    def __init__(self):
        """Create SQLAlchemy engine."""
        try:
            self.__engine = create_engine('mysql+mysqldb://{}:{}@{}:3306/{}'.format(
                getenv('HBNB_MYSQL_USER'),
                getenv('HBNB_MYSQL_PWD'),
                getenv('HBNB_MYSQL_HOST'),
                getenv('HBNB_MYSQL_DB')),
                pool_pre_ping=True
            )
            print("Engine created successfully.")
            self.test_database_connection()
        except Exception as e:
            print("Error creating engine:", e)

        # Drop tables if the environment variable HBNB_ENV is equal to 'test'
        if getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def test_database_connection(self):
        """Test the database connection."""
        try:
            with self.__engine.connect() as connection:
                print("Database connection successful!")
        except SQLAlchemyError as e:
            print("Database connection failed:", e)

    def check_tables_exist(self):
        """Check if the necessary tables exist in the database."""
        try:
            with self.__engine.connect() as connection:
                result = connection.execute("SHOW TABLES;")
                tables = result.fetchall()
                print("Tables in the database:", tables)
        except SQLAlchemyError as e:
            print("Error checking tables:", e)

    def all(self, cls=None):
        """Query and return all objects by class/generally.
        Return: dictionary (<class-name>.<object-id>: <obj>)
        """
        obj_dict = {}

        if cls:
            for row in self.__session.query(cls).all():
                # populate dict with objects from storage
                obj_dict.update({'{}.{}'.format(type(cls).__name__, row.id): row})
        else:
            for key, val in all_classes.items():
                for row in self.__session.query(val):
                    obj_dict.update({'{}.{}'.format(type(row).__name__, row.id): row})
        return obj_dict

    def new(self, obj):
        """Add object to current database session."""
        self.__session.add(obj)

    def save(self):
        """Commit current database session."""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete obj from database session."""
        if obj:
            # determine class from obj
            cls_name = all_classes[type(obj).__name__]

            # query class table and delete
            self.__session.query(cls_name).filter(cls_name.id == obj.id).delete()

    def reload(self):
        """Create database session."""
        # create db tables
        Base.metadata.create_all(self.__engine)
        # create db session from current engine
        session = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(session)

    def close(self):
        """Close scoped session."""
        self.__session.remove()
