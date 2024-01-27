import os

from flask import Flask
from .routes import main
from etlcsvmongodb.settings import UPLOADS_PATH, MAX_CONTENT_LENGTH
def create_app(confing_object='etlcsvmongodb.settings'):

    app = Flask(__name__)

    # if os.environ.get('FLASK_ENV') == 'production':
    #     app.config.from_object('prod')
    # else:
    #     app.config.from_object('dev')

    UPLOAD_FOLDER = UPLOADS_PATH

    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.register_blueprint(main)

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    return app




