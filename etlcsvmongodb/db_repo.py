

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from etlcsvmongodb.settings import MONGO_HOST, MONGO_PORT, MONGO_MAX_POOL_SIZE

try:
    import pymongo
    from pymongo import MongoClient
    import pandas as pd
    import json
except Exception as e:
    print("Some Modules are Missing ")


class MongoDB(object):

    def __init__(self, dBName=None, collectionName=None):

        self.dBName = dBName
        self.collectionName = collectionName

        self.client = MongoClient(MONGO_HOST, MONGO_PORT, maxPoolSize=MONGO_MAX_POOL_SIZE)

        self.DB = self.client[self.dBName]
        self.collection = self.DB[self.collectionName]


Base = declarative_base()

# class PostgreSQLDB(object):
#     def __init__(self, user=None, password=None, host=None, port=None, db=None ):
#         self.engine = create_engine(
#             f"postgresql://{user}:{password}@{host}:{port}/{db}"
#         )
#         Base.metadata.create_all(self.engine)
#         self.Session = sessionmaker(bind=self.engine)


class PostgreSQLDB(object):
    def __init__(self, user=None, password=None, host=None, port=None, db=None):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db = db

        self._create_engine()
        #self._create_tables()

    def _create_engine(self):
        self.engine = create_engine(
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}",
            pool_size=5,
            max_overflow=10,
        )

    def _create_tables(self):
        Base.metadata.create_all(self.engine)

    def create_session(self):
        print("creating session for psql")
        Session = sessionmaker(bind=self.engine)
        return Session()


