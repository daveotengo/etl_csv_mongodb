
import os
import time
from json import dumps

from flask import send_from_directory, Response
import pandas as pd
from werkzeug.utils import secure_filename


from flask import Blueprint, jsonify, request, render_template

from etlcsvmongodb import app
from etlcsvmongodb.db_collection import get_single_data, insert_multi_data, get_multiple_data
from etlcsvmongodb.db_collection_info import insert_data, get_single_data_by_file_name
from flask import current_app

from etlcsvmongodb.utils import JSONEncoder, allowed_file

main = Blueprint('main',__name__)

pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 3000)


@main.route('/')
def get_index_page():
    return render_template('index.html')

@main.route('/api/data/single/<id>')
def get_sing_data(id):
    data = get_single_data(id)
    return Response(JSONEncoder().encode(data), status=200, mimetype='application/json')

@main.route('/api/data/multi')
def get_all_data():
    data = get_multiple_data()
    return Response(JSONEncoder().encode(data), status=200, mimetype='application/json')


@main.route('/api/uploads',methods=['POST'])
def multi_upload():


    if request.method == 'POST':

        uploaded_files = request.files.getlist("file[]")
        if (len(uploaded_files)>0):

            print(uploaded_files[0].filename)
            filenames = []
            msg=''
            status=''
            data=''
            file_path = current_app.config['UPLOAD_FOLDER']
            for file in uploaded_files:

                file.stream.seek(0)
                filename = secure_filename(file.filename)

                # Check if the file is one of the allowed types/extensions
                if not get_single_data_by_file_name(filename):
                    if file and allowed_file(file.filename):
                        print("enter")
                        # Make the filename safe, remove unsupported chars
                        # Move the file form the temporal folder to the upload
                        # folder we setup
                        file.save(os.path.join(file_path, filename))
                        # Save the filename into a list, we'll use it later
                        filenames.append(filename)

                        df = pd.read_csv(file_path+filename)
                        data = df.to_dict('records')
                        try :
                            insert_multi_data(data)
                        except Exception as e:
                            print(e)


                        size = os.stat(current_app.config['UPLOAD_FOLDER'] + filename).st_size

                        files_date = time.strftime('%m/%d/%Y', time.gmtime(
                            os.path.getmtime(current_app.config['UPLOAD_FOLDER'] + file.filename)))

                        total_rows = len(df.axes[0])  # ===> Axes of 0 is for a row

                        total_cols = len(df.axes[1])  # ===> Axes of 0 is for a column

                        info_data = {
                            'file_name': filename,
                            'file_size': str(size)+"bytes",
                            'files_date': files_date,
                            'total_rows':total_rows,
                            'total_cols':total_cols,

                        }
                        insert_data(info_data)

                        msg ="Successfully Added File(s)"
                        status='00'
                    else:
                        msg ="There was Something wrong Adding File(s)"
                        status='01'
                else:
                    msg = "Please check it seems this file has already been Uploaded"
                    status = '02'
        else:
            msg = "Please Select A File"
            status = '03'



    return jsonify(
        message=msg,
        status= status,
    )



@main.route('/api/upload', methods=['GET', 'POST'])
def single_upload():
    if request.method == 'POST':
        file_path = current_app.config['UPLOAD_FOLDER']

        csv = request.files['data']

        uploaded_file=csv
        uploaded_file.stream.seek(0)

        filename = secure_filename(csv.filename)

        uploaded_file.save(os.path.join(file_path, filename))

        df = pd.read_csv(file_path + filename)

        data = df.to_dict('records')

        insert_multi_data(data)

        #file_size = round((size/ 1048576), 4)
        size = os.stat(file_path + filename).st_size


        files_date = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path+csv.filename)))

        total_rows = len(df.axes[0])  # ===> Axes of 0 is for a row

        total_cols = len(df.axes[1])  # ===> Axes of 0 is for a column

        info_data = {
            'file_name': filename,
            'file_size': str(size) + "bytes",
            'files_date': files_date,
            'total_rows': total_rows,
            'total_cols': total_cols,

        }
        insert_data(info_data)


    data = jsonify(
        total_rows = total_rows,
        total_cols=total_cols,
        csv_name=secure_filename(csv.filename),
    )
    return data
