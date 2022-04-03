
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

