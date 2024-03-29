import ast
import collections
import json
import math
import os
import time
from json import dumps
from types import SimpleNamespace

from flask import send_from_directory, Response, make_response
import pandas as pd
from marshmallow import ValidationError
from sqlalchemy.engine import row
from sqlalchemy.orm import session
from werkzeug.utils import secure_filename

from flask import Blueprint, jsonify, request, render_template

from etlcsvmongodb import db_collection
from etlcsvmongodb.db_collection import get_single_data, insert_multi_data, get_multiple_data, \
    get_single_data_by_date_and_amt, remove_data
from etlcsvmongodb.db_collection_info import insert_data, get_single_data_by_file_name
from flask import current_app

from etlcsvmongodb.service import update_facility_name, insert_new_facility_record, insert_new_district_record, \
    update_district_name, update_sub_district_name, insert_new_sub_district_record, update_entity, insert_new_entity
from etlcsvmongodb.errors import error_response
from etlcsvmongodb.logger_config import logger
from etlcsvmongodb.models import DateTimeAmount, date_time_amount_schema, Facility, Region, District
from etlcsvmongodb.utils import JSONEncoder, allowed_file
from etlcsvmongodb.validator import add_item_param_validation
from flask import render_template, request, jsonify, make_response, current_app

main = Blueprint('main', __name__)

pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 3000)


@main.route('/')
def get_index_page():
    return render_template('index.html')


@main.route('/api/data/single/', defaults={'id': None})
@main.route('/api/data/single/<id>')
def get_single_data_by_id(id):
    if not id:
        return make_response(
            jsonify(
                msg="Param id is required",
                status="02",
            ),
            400,
        )

    jsn_data = None

    msg = "Successfully Fetched Record with id " + id
    status = '00'

    try:
        data = get_single_data(id)
        if not jsn_data:
            msg = "Document/Record with id: " + id + " does not exist"
            status = '03'


    except Exception as e:
        # logger.info(e)
        msg = "Something went wrong fetchting Document/Record with id: " + id
        status = '01'

    jsn_data = json.loads(JSONEncoder().encode(data))

    response = make_response(
        jsonify(
            msg=msg,
            status=status,
            data=jsn_data
        ),
        200,
    )
    return response


@main.route('/api/data/multi')
def get_all_data():
    msg = "Successfully Fetched Data"
    status = '00'
    try:
        data = get_multiple_data()
    except Exception as e:
        logger.info(e)
        msg = "Something Went Wrong Fetching Data"
        status = '01'

    response = make_response(
        jsonify(
            msg=msg,
            status=status,
            data=json.loads(JSONEncoder().encode(data))
        ),
        200,
    )
    response.headers["Content-Type"] = "application/json"
    return response


@main.route('/api/uploads', methods=['GET', 'POST'])
def multi_upload():
    if request.method == 'POST':

        try:
            uploaded_files = request.files.getlist("file[]")
        except:

            return make_response(
                jsonify(
                    msg="Param file[] is required",
                    status='03'
                ),
                400,
            )

        if (len(uploaded_files) > 0):

            logger.info(uploaded_files[0].filename)
            filenames = []
            msg = ''
            status = ''
            data = ''
            file_path = current_app.config['UPLOAD_FOLDER']
            for file in uploaded_files:

                file.stream.seek(0)
                filename = secure_filename(file.filename)
                # Check if the file is one of the allowed types/extensions
                if file and allowed_file(file.filename):
                    # Check if file has already been uploaded
                    if not get_single_data_by_file_name(filename):
                        logger.info("enter")
                        # Make the filename safe, remove unsupported chars
                        # Move the file form the temporal folder to the upload
                        # folder we setup
                        file.save(os.path.join(file_path, filename))
                        # Save the filename into a list, we'll use it later
                        filenames.append(filename)

                        df = pd.read_csv(file_path + filename)
                        data = df.to_dict('records')
                        try:
                            insert_multi_data(data)
                        except Exception as e:
                            logger.info(e)

                        # Getting filesize
                        size = os.stat(file_path + filename).st_size
                        # Getting date of entry
                        files_date = time.strftime('%m/%d/%Y', time.gmtime(
                            os.path.getmtime(file_path + file.filename)))
                        # Getting total_rows
                        total_rows = len(df.axes[0])  # ===> Axes of 0 is for a row
                        # Getting total_colums
                        total_cols = len(df.axes[1])  # ===> Axes of 0 is for a column

                        info_data = {
                            'file_name': filename,
                            'file_size': str(size) + "bytes",
                            'files_date': files_date,
                            'total_rows': total_rows,
                            'total_cols': total_cols,

                        }

                        insert_data(info_data)

                        msg = "Successfully Uploaded File(s)"
                        status = '00'
                    else:

                        msg = "Please check it seems this file has already been Uploaded"
                        status = '02'
                else:
                    msg = "Please check File(s) type"
                    status = '01'
        else:
            msg = "Please Select A File"
            status = '03'

        response = make_response(
            jsonify(
                msg=msg,
                status=status,
                filenames=filenames
            ),
            200,
        )

        response.headers["Content-Type"] = "application/json"
        return response

    return '''
             <!doctype html>
             <title>Upload new File</title>
             <h1>Upload new File</h1>
             <form action="" method=post  enctype=multipart/form-data>
               <p><input type=file multiple="multiple" name="file[]" >
                  <input type=submit value=Upload>
             </form>
             '''


@main.route('/api/upload', methods=['GET', 'POST'])
def single_upload():
    if request.method == 'POST':
        try:
            file = request.files['data']
        except:
            return make_response(
                jsonify(
                    msg="Param data is required",
                    status='03'
                ),
                400,
            )

        file_path = current_app.config['UPLOAD_FOLDER']

        file.stream.seek(0)

        filename = secure_filename(file.filename)

        jsn_info_data = None
        jsnloadsArrayStr = None

        if file and allowed_file(file.filename):

            if not get_single_data_by_file_name(filename):

                file.save(os.path.join(file_path, filename))

                df = pd.read_csv(file_path + filename)

                data = df.to_dict('records')

                insert_multi_data(data)

                # file_size = round((size/ 1048576), 4)
                size = os.stat(file_path + filename).st_size

                files_date = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path + file.filename)))

                total_rows = len(df.axes[0])  # ===> Axes of 0 is for a row

                total_cols = len(df.axes[1])  # ===> Axes of 0 is for a column

                info_data = {
                    "file_name": filename,
                    "file_size": str(size) + 'bytes',
                    "files_date": files_date,
                    "total_rows": total_rows,
                    "total_cols": total_cols,
                }

                logger.info(str(info_data).replace("'", '"'))

                logger.info(str(info_data).replace("'", '"'))

                x = json.loads(str(info_data).replace("'", '"'), object_hook=lambda d: SimpleNamespace(**d))
                logger.info(x.file_name, x.file_size, x.files_date)
                logger.info(x)
                logger.info(json.loads(str(info_data).replace("'", '"')))

                logger.info(json.dumps(json.loads(str(info_data).replace("'", '"')), indent=2))

                jsn_info_data = json.loads(str(info_data).replace("'", '"'))

                logger.info(str(data).replace("'", '"'))

                logger.info("\n")

                jsnencodedArrayStr = JSONEncoder().encode(data)

                logger.info(jsnencodedArrayStr)

                jsnloadsArrayStr = json.loads(jsnencodedArrayStr)

                logger.info("\n")

                insert_data(info_data)

                msg = "Successfully Uploaded File(s)"
                status = '00'
            else:
                msg = "Please Check File has alread been uploaded"
                status = '01'
        else:
            msg = "Please Check File Type"
            status = '02'

        response = make_response(
            jsonify(
                msg=msg,
                status=status,
                info_data=jsn_info_data,
                data=jsnloadsArrayStr
            ),
            200,
        )
        response.headers["Content-Type"] = "application/json"

        return response

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=data>
         <input type=submit value=Upload>
    </form>
    '''


@main.route('/api/item/add', methods=['POST'])
def add_item():
    validation_result = add_item_param_validation.validate(request.json)
    data = None
    if validation_result.get('success', False) is False:
        return make_response(
            jsonify({
                "status": "02",
                "errors": validation_result.get("error")
            }
            ),
            400,
        )

    jsn_req = request.json

    # j = json.loads(str(jsn_req).replace("'", '"'))
    # u = DateTimeAmount(**j)
    # logger.info(u)
    #
    # date_time = u.Datetime
    # amount = u.amount
    #
    date_time = jsn_req['Datetime']
    amount = jsn_req['amount']
    logger.info(jsn_req)

    if not get_single_data_by_date_and_amt(date_time, amount):
        data = {
            "Datetime": date_time,
            "amount": amount
        }

        msg = "Successfully Added Record/Document"
        status = '00'
        try:
            db_collection.insert_data(data)
        except Exception as e:
            msg = "Something went wrong while inserting data, Error: " + e
            status = '01'

    else:
        msg = "Record Has alread been added"
        status = '03'

    response = make_response(
        jsonify(
            msg=msg,
            status=status,
            data=json.loads(JSONEncoder().encode(data))

        ),
        201,
    )
    response.headers["Content-Type"] = "application/json"
    return response


@main.route('/api/item/update', methods=['PUT'])
def update_item():
    try:
        date_time_amount = date_time_amount_schema.loads(request.data)
    except ValidationError as err:
        return error_response(400, err.messages)
    logger.info(date_time_amount)
    jsn_req = request.json
    logger.info(jsn_req)
    id = jsn_req['id']

    sing_data = get_single_data(id)
    if not sing_data:
        msg = "Sorry Please record you are trying to upate does not exist"
        status = '02'
    else:

        logger.info("printing initial single data")
        logger.info(sing_data)

        date_time = jsn_req['Datetime']

        amount = jsn_req['amount']

        if amount:
            sing_data['amount'] = amount
        if date_time:
            sing_data['Datetime'] = date_time

        logger.info("printing updated single data")
        logger.info(sing_data)

        logger.info(jsn_req)
        msg = "Successfully Updated Record/Document"
        status = '00'

        try:

            db_collection.update_existing(id, sing_data)
        except Exception as e:
            # pass
            msg = "Something went wrong while inserting data, Error: " + str(e)
            status = '01'
            # return make_response(
            #     jsonify(
            #         msg=msg,
            #         status=status,
            #     ),
            #     500,
            # )

    response = make_response(
        jsonify(
            msg=msg,
            status=status,
            data=json.loads(JSONEncoder().encode(sing_data))

        ),
        200,
    )
    response.headers["Content-Type"] = "application/json"
    return response


@main.route('/api/item/', methods=['DELETE'], defaults={'id': None})
@main.route('/api/item/<id>', methods=['DELETE'])
def delete_data_by_id(id):
    if not id:
        return make_response(
            jsonify(
                msg="Param id is required",
                status="03",
            ),
            400,
        )

    jsn_data = None

    msg = "Successfully Deleted Record with id " + id
    status = '00'

    sing_data = get_single_data(id)
    if not sing_data:
        msg = "Sorry please record you are trying to update does not exist"
        status = '02'
    else:

        try:
            data = remove_data(id)
            jsn_data = json.loads(JSONEncoder().encode(data))
        except Exception as e:
            # logger.info(e)
            msg = "Sorry Something went wrong when deleting Document/Record with id: " + id
            status = '01'

    response = make_response(
        jsonify(
            msg=msg,
            status=status,
            data=jsn_data
        ),
        200,
    )
    return response


ALLOWED_EXTENSIONS = {'csv', 'xlsx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/api/upload_and_update', methods=['GET', 'POST'])
def upload_and_update_data():
    if request.method == 'POST':
        try:
            logger.info("Endpoint : /api/upload_and_update Hit ")
            # File upload handling
            file = request.files['data']

            # Validate file type
            if not allowed_file(file.filename):
                logger.info("not allowed")

                return jsonify(
                    msg="Invalid file type. Please upload a CSV or Excel file.",
                    status='02',
                )

            logger.info("file allowed")
            file_path = current_app.config['UPLOAD_FOLDER']
            filename = secure_filename(file.filename)
            file.save(os.path.join(file_path, filename))
            logger.info("setting file name")
            logger.info(filename)
            logger.info(file_path)

            # Read file data
            # sheet_name = 'Facility GAPS'  # Replace 'YourSheetName' with the actual sheet name
            # df = pd.read_csv(file_path + filename) if filename.endswith('.csv') else pd.read_excel(file_path + filename,
            #                                                                                        sheet_name=sheet_name,
            #                                                                                        engine='openpyxl'
            # List of sheet names
            sheet_names = ['District GAPS', 'Sub-district GAPS', 'Facility GAPS']

            # Loop through each sheet name
            for sheet_name in sheet_names:
                # Read file data for each sheet
                df = pd.read_csv(file_path + filename) if filename.endswith('.csv') else pd.read_excel(
                    file_path + filename,
                    sheet_name=sheet_name,
                    engine='openpyxl')
                logger.info(df)
                logger.info(f"read file name and path for sheet: {sheet_name}")

                if sheet_name == 'District GAPS':
                    process_district_gaps(df)
                if sheet_name == 'Sub-district GAPS':
                    process_sub_district_gaps(df)
                if sheet_name == 'Facility GAPS':
                    process_facility_gaps(df)
                # process_all_gaps(df, sheet_name.split(" ")[0])

            return jsonify(
                msg="File data updated successfully",
                status='00',
            )

        except Exception as e:
            # Error handling
            return jsonify(
                msg=f"An error occurred: {str(e)}",
                status='03',
            )

    return render_template('upload_and_update.html')


def process_all_gaps(df, entity_str):
    logger.info(f"****called process_all_gaps {entity_str} ****")
    # Extract sormas_facility and validated_facility columns
    if f'SORMAS {entity_str}' not in df.columns or f'Validated {entity_str}' not in df.columns:
        return jsonify(
            msg=f"Required columns f'SORMAS {entity_str}' and 'Validated {entity_str}' not found in the file.",
            status='04',
        )

    # Update database with file data
    # Iterate over rows in the DataFrame
    entity_str_lower = entity_str.lower()

    for index, row in df.iterrows():
        sormas_entity_exl_row_val = row[f'SORMAS {entity_str}']
        validated_entity_exl_row_val = row[f'Validated {entity_str}']
        logger.info(f"printing {sormas_entity_exl_row_val}")
        logger.info(sormas_entity_exl_row_val)
        if str(sormas_entity_exl_row_val).lower() == "nan" or isinstance(sormas_entity_exl_row_val,
                                                                         float) and math.isnan(
            sormas_entity_exl_row_val):
            logger.info("entered")

            # Perform the insertion, adjust as needed based on your data model
            logger.info("Inserting")
            result = insert_new_entity(row, entity_str)
            logger.info(f"Processed {validated_entity_exl_row_val} result: {result}")

        else:

            logger.info("Updating")
            # Update database with file data
            # Perform the update, adjust as needed based on your data model
            postgresql_updated = update_entity(row, entity_str)

            logger.info(f"Processed {sormas_entity_exl_row_val} with "
                        f"{validated_entity_exl_row_val} result: {postgresql_updated}")


def process_facility_gaps(df):
    logger.info("****called process_facility_gaps****")
    # Extract sormas_facility and validated_facility columns
    if 'SORMAS Facility' not in df.columns or 'Validated Facility' not in df.columns:
        return jsonify(
            msg="Required columns 'SORMAS Facility' and 'Validated Facility' not found in the file.",
            status='04',
        )

    # Update database with file data
    # Iterate over rows in the DataFrame
    for index, row in df.iterrows():
        sormas_facility = row['SORMAS Facility']
        validated_facility = row['Validated Facility']
        logger.info("printing sormas_facility")
        logger.info(sormas_facility)
        if str(sormas_facility).lower() == "nan" or isinstance(sormas_facility, float) and math.isnan(
                sormas_facility):
            logger.info("entered")

            # Perform the insertion, adjust as needed based on your data model
            logger.info("Inserting")
            result = insert_new_facility_record(row, validated_facility)

            logger.info(f"Processed {validated_facility} result: {result}")
        else:
            logger.info("Updating")
            # Update database with file data
            # Perform the update, adjust as needed based on your data model
            postgresql_updated = update_facility_name(row)

            logger.info(f"Processed {sormas_facility} with {validated_facility} result: {postgresql_updated}")


def process_district_gaps(df):
    logger.info("***start called process_district_gaps****")

    # Extract sormas_facility and validated_facility columns
    if 'SORMAS District' not in df.columns or 'Validated District Name' not in df.columns:
        return jsonify(
            msg="Required columns 'SORMAS District' and 'Validated District Name' not found in the file.",
            status='04',
        )

    # Update database with file data
    # Iterate over rows in the DataFrame
    for index, row in df.iterrows():
        sormas_district = row['SORMAS District']
        validated_district = row['Validated District Name']
        logger.info("printing sormas_facility")
        logger.info(sormas_district)
        if str(sormas_district).lower() == "nan" or isinstance(sormas_district, float) and math.isnan(
                sormas_district):
            logger.info("entered")

            # Perform the insertion, adjust as needed based on your data model
            logger.info("Inserting")
            result = insert_new_district_record(row, validated_district)
            logger.info(f"Processed {validated_district} result: {result}")


        else:

            logger.info("Updating")
            # Update database with file data
            # Perform the update, adjust as needed based on your data model
            postgresql_updated = update_district_name(row)

            logger.info(f"Processed {sormas_district} result: {postgresql_updated}")


def process_sub_district_gaps(df):
    logger.info("****called process_sub_district_gaps entity_str****")

    # Extract sormas_sub-district and validated_sub-district columns
    if 'SORMAS Sub-District' not in df.columns or 'Validated Sub-district' not in df.columns:
        return jsonify(
            msg="Required columns 'SORMAS Sub-District' and 'Validated Sub-District' not found in the file.",
            status='04',
        )

    # Update database with file data
    # Iterate over rows in the DataFrame
    for index, row in df.iterrows():
        sormas_sub_district = row['SORMAS Sub-District']
        validated_sub_district = row['Validated Sub-district']
        logger.info("printing sormas_sub-district")
        logger.info(sormas_sub_district)
        if str(sormas_sub_district).lower() == "nan" or isinstance(sormas_sub_district, float) and math.isnan(
                sormas_sub_district):
            logger.info("entered")

            # Perform the insertion, adjust as needed based on your data model
            logger.info("Inserting")
            result = insert_new_sub_district_record(row, validated_sub_district)
            logger.info(f"Processed {validated_sub_district} result: {result}")

        else:

            logger.info("Updating")
            # Update database with file data
            # Perform the update, adjust as needed based on your data model
            postgresql_updated = update_sub_district_name(row)
            logger.info(f"Processed {sormas_sub_district} result: {postgresql_updated}")

# @main.route('/update_data', methods=['GET', 'POST'])
# def update_data_route():
#     if request.method == 'POST':
#         # Assuming you have a form with sormas_sub-district and validated_facility fields
#         sormas_facility = request.form.get('sormas_facility')
#         validated_facility = request.form.get('validated_facility')
#
#         # Update in PostgreSQL
#         postgresql_updated = update_facility_name(sormas_facility, validated_facility)
#
#         if postgresql_updated :
#             message = "Data updated successfully in both databases."
#         else:
#             message = "Error updating data in one or more databases."
#
#         return render_template('update_data.html', message=message)
#     return render_template('update_data.html', message=None)
