

import pymongo
from bson import ObjectId


# CONNECT TO DATABASE
from pandas import unique

from etlcsvmongodb.db_repo import MongoDB


db = MongoDB(dBName='my_database', collectionName='my_collection_info')

collection =db.collection
print("Database connected")




def insert_data(data):
    """
    Insert new data or document in collection
    :param data:
    :return:
    """
    document = collection.insert_one(data)
    return document.inserted_id

def insert_multi_data(data):
    """
    :param data: data os csv File
    :return:
    """


    collection.insert_many(data, ordered=False)
    return data


def update_or_create(document_id, data):
    """
    This will create new document in collection
    IF same document ID exist then update the data
    :param document_id:
    :param data:
    :return:
    """
    # TO AVOID DUPLICATES - THIS WILL CREATE NEW DOCUMENT IF SAME ID NOT EXIST
    document = collection.update_one({'_id': ObjectId(document_id)}, {"$set": data}, upsert=True)
    return document.acknowledged


def get_single_data(document_id):
    """
    get document data by document ID
    :param document_id:
    :return:
    """
    data = collection.find_one({'_id': ObjectId(document_id)})
    return data

def get_single_data_by_file_name(file_name):
    """
    get document data by document ID
    :param document_id:
    :return:
    """
    data = collection.find_one({'file_name': file_name})
    return data


def get_multiple_data():
    """
    get document data by document ID
    :return:
    """
    data = collection.find()
    return list(data)


def update_existing(document_id, data):
    """
    Update existing document data by document ID
    :param document_id:
    :param data:
    :return:
    """
    document = collection.update_one({'_id': ObjectId(document_id)}, {"$set": data})
    return document.acknowledged


def remove_data(document_id):
    document = collection.delete_one({'_id': ObjectId(document_id)})
    return document.acknowledged


# CLOSE DATABASE
#connection.close()
