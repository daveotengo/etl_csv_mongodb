from os.path import join, dirname, realpath

from flask import Flask, app
from .routes import main



def create_app(confing_object='etlcsvmongodb.settings'):
    app = Flask(__name__);

    UPLOADS_PATH = join(dirname(realpath(__file__)), './uploads/')

    UPLOAD_FOLDER = UPLOADS_PATH

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.register_blueprint(main)

    return app

