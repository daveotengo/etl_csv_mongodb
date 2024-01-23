import logging
import random
import uuid

from flask import Flask, render_template, request
import pandas as pd
from sqlalchemy import create_engine, update, text, select
from sqlalchemy.engine import row

from etlcsvmongodb.db_repo import PostgreSQLDB

from contextlib import contextmanager

from etlcsvmongodb.models import Facility, Region, District, Community

db = PostgreSQLDB(user='sormas_user', password='sormas123', host='localhost', port='5432', db='sormas_db')


@contextmanager
def session_scope():
    session = db.create_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error in database operation: {e}")
        raise  # Re-raise the exception after rolling back the session
    finally:
        session.close()


def insert_new_facility_record(row, validated_facility):
    try:
        with session_scope() as session:

            region = row["Region"]
            print(region)
            district = row["District"]
            print(district)
            community = row["Sub-District"]
            print(community)

            region_to_insert = session.query(Region).filter_by(name=region).first()
            print(region_to_insert)

            district_to_insert = session.query(District).filter_by(name=district).first()
            print(district_to_insert)

            community_to_insert = session.query(Community).filter_by(name=community).first()
            print(community_to_insert)
            unique_rand = generate_complex_unique_number()

            existing_facility = session.query(Facility).filter_by(name=validated_facility).first()
            print("==existing_facility==")
            print(existing_facility)

            if existing_facility:
                print("Facility already exists. Skipping insertion.")
                logging.info("Facility already exists. Skipping insertion.")
                return True, "Facility already exists. Skipping insertion"

            # Insert entire record considering the specific matching field in the table
            new_facility_data = {
                "id": unique_rand,
                "additionalinformation": row["SD Code"],
                "region_id": region_to_insert.id,
                "district_id": district_to_insert.id,
                "community_id": community_to_insert.id,
                # "DHIMS Facility": row["DHIMS Facility"],
                # "SORMAS Facility": validated_facility,
                # "Comments": row["Comments"],
                "name": validated_facility,
                # "Comments 2": row["Comments 2"],
                # Add other columns as needed
            }
            new_facility = Facility(**new_facility_data)
            session.add(new_facility)

            print("facility created")

        return True
    except Exception as e:
        print(f"Error inserting new facility record: {e}")
        return False

def generate_complex_unique_number():
    current_time = pd.datetime.datetime.utcnow()
    timestamp_part = int(current_time.timestamp()) * 1000000
    random_part = random.randint(0, 99999)  # 5-digit random number

    complex_unique_number = timestamp_part + random_part

    return complex_unique_number


# def generate_complex_unique_number():
#     current_time = pd.datetime.datetime.utcnow()
#     timestamp_part = int(current_time.timestamp()) * 1000000
#     random_part = random.randint(100000, 999999)  # 6-digit random number
#
#     complex_unique_number = timestamp_part + random_part
#
#     return complex_unique_number


def update_facility_name(sormas_facility, validated_facility):
    print("update_facility_name called")
    try:
        with session_scope() as session:
            print("in session scopes")
            print(sormas_facility)

            sormas_facility_name = sormas_facility

            # SQL query string
            sql_query = text("SELECT * FROM facility WHERE name = :name")

            # Execute the query and fetch results
            # facility_to_update = session.execute(sql_query, {"name": sormas_facility_name}).fetchone()

            facility_to_update = session.query(Facility).filter_by(name=sormas_facility_name).first()
            print(facility_to_update)

            print("==facility_to_update==")
            print(facility_to_update)

            if facility_to_update:
                # Update the name field
                facility_to_update.name = validated_facility
                session.commit()
                return True
            else:
                print(f"Facility with name '{sormas_facility}' not found.")
                return False

    except Exception as e:
        print(f"Error updating data in PostgreSQL: {e}")
        return False
# def update_facility_name(sormas_facility, validated_facility):
#     try:
#         with session_scope() as session:
#             # Use SQL expression language for the update
#             stmt = update(Facility).where(Facility.name == sormas_facility).values(name=validated_facility)
#             session.execute(stmt)
#
#         return True
#     except Exception as e:
#         print(f"Error updating data in PostgreSQL: {e}")
#         return False

# def update_facility_name(sormas_facility, validated_facility):
#     try:
#         with session_scope() as session:
#             # Retrieve the Facility record to update
#             facility_to_update = session.query(Facility).filter_by(name=sormas_facility).first()
#
#             if facility_to_update:
#                 # Update the name with the validated_facility value
#                 facility_to_update.name = validated_facility
#
#             return True
#     except Exception as e:
#         print(f"Error updating data in PostgreSQL: {e}")
#         return False


# def update_facility_name(sormas_facility, validated_facility):
#     try:
#         with session_scope() as session:
#             # Update the corresponding record in the database
#             session.query(Facility).filter_by(name=sormas_facility).update({"name": validated_facility})
#         return True
#     except Exception as e:
#         print(f"Error updating data in PostgreSQL: {e}")
#         return False
