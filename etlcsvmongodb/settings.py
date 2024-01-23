import os
from os.path import dirname, join, realpath

#DATABASE
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_MAX_POOL_SIZE=50

PSQL_HOST = 'localhost'
PSQL_PORT = '5432'
PSQL_USER = 'sormas_user'
PSQL_PSW = 'sormas123'
PSQL_DB_NAME = 'sormas_db'

#FILE UPLOAD
UPLOADS_PATH = join(dirname(realpath(__file__)), './uploads/')
MAX_CONTENT_LENGTH=16 * 1000 * 1000

#os.environ.get('MONGO_HOST')