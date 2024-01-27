import logging
import random
import sys

from sqlalchemy import text

from etlcsvmongodb.db_repo import PostgreSQLDB

from contextlib import contextmanager

from etlcsvmongodb.enums import FacilityType
from etlcsvmongodb.logger_config import logger
from etlcsvmongodb.models import Facility, Region, District, Community
from etlcsvmongodb.settings import PSQL_USER, PSQL_PWD, PSQL_HOST, PSQL_PORT, PSQL_DB

db = PostgreSQLDB(user=PSQL_USER, password=PSQL_PWD, host=PSQL_HOST, port=PSQL_PORT, db=PSQL_DB)


@contextmanager
def session_scope():
    session = db.create_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.info(f"Error in database operation: {e}")
        raise  # Re-raise the exception after rolling back the session
    finally:
        session.close()


def insert_new_entity(excel_row, entity_str):
    sormas_entity = excel_row[f'SORMAS {entity_str}']
    validated_entity = excel_row[f'Validated {entity_str}']
    logger.info(f"=======insert_{entity_str}_record called======={validated_entity}")

    try:
        with session_scope() as session:

            region = excel_row["Region"]
            logger.info(region)
            district = excel_row["District"]
            logger.info(district)
            community = excel_row["Sub-District"]
            logger.info(community)

            if region is not None:
                region_to_insert = session.query(Region).filter_by(name=region).first()
                logger.info(region_to_insert)

            if region_to_insert is not None:
                district_to_insert = session.query(District).filter_by(name=district,
                                                                       region_id=region_to_insert.id).first()
                logger.info(district_to_insert)

            if district_to_insert is not None:
                community_to_insert = session.query(Community).filter_by(name=community,
                                                                         district_id=district_to_insert.id).first()
            logger.info(community_to_insert)
            unique_rand = generate_unique_random_numbers()
            if entity_str == 'Facility':

                if region_to_insert is not None and district_to_insert is not None and community_to_insert is not None:

                    existing_facility = session.query(Facility).filter_by(name=validated_entity,
                                                                          district_id=district_to_insert.id,
                                                                          region_id=region_to_insert.id,
                                                                          community_id=community_to_insert.id).first()
                    logger.info("==existing_facility==")
                    logger.info(existing_facility)

                    if existing_facility:
                        logger.info(f"Facility already exists. Skipping insertion for {validated_entity}")
                        return False, f"Facility already exists. Skipping insertion for {validated_entity}"

                    # Insert entire record considering the specific matching field in the table
                    new_facility_data = {
                        "id": unique_rand,
                        "additionalinformation": excel_row["SD Code"],
                        "region_id": region_to_insert.id,
                        "district_id": district_to_insert.id,
                        "community_id": community_to_insert.id,
                        # "DHIMS Facility": excel_row["DHIMS Facility"],
                        # "SORMAS Facility": validated_facility,
                        # "Comments": excel_row["Comments"],
                        "name": validated_entity,
                        "type": FacilityType.HOSPITAL.name
                        # "Comments 2": excel_row["Comments 2"],
                        # Add other columns as needed
                    }
                    new_facility = Facility(**new_facility_data)
                    session.add(new_facility)

                    logger.info("facility created")
                else:
                    # Handle the case when any of the values are None
                    print(f"Invalid or missing data(Region/District/Sub-district) for "
                          f"{validated_entity} in the exel input.")

            if entity_str == 'District':
                if region_to_insert is not None:

                    existing_district = session.query(District).filter_by(name=validated_entity,
                                                                          region_id=region_to_insert.id).first()
                    logger.info("==existing_district==")
                    logger.info(existing_district)

                    if existing_district:
                        logger.info(f"District already exists. Skipping insertion for {validated_entity}")
                        return False, f"District already exists. Skipping insertion for {validated_entity}"

                    # Insert entire record considering the specific matching field in the table
                    new_district_data = {
                        "id": unique_rand,
                        "additionalinformation": excel_row["SD Code"],
                        "region_id": region_to_insert.id,
                        # "DHIMS Facility": excel_row["DHIMS Facility"],
                        # "SORMAS Facility": validated_facility,
                        # "Comments": excel_row["Comments"],
                        "name": validated_entity,
                        # "Comments 2": excel_row["Comments 2"],
                    }
                    new_district = District(**new_district_data)
                    session.add(new_district)
                    logger.info("district created")
                else:
                    logger.info(f"Invalid or missing data (Region) for {validated_entity} in the excel input.")
                    return False, f"Invalid or missing data (Region) for {validated_entity} in the excel input."

            if entity_str == 'Sub-District':
                if district_to_insert is not None:

                    existing_sub_district = session.query(Community).filter_by(name=validated_entity,
                                                                               district_id=district_to_insert.id).first()
                    logger.info("==existing_sub_district==")
                    logger.info(existing_sub_district)

                    if existing_sub_district:
                        logger.info(f"Sub District already exists. Skipping insertion for {validated_entity}")
                        return False, f"Sub District  already exists. Skipping insertion for {validated_entity}"

                    # Insert entire record considering the specific matching field in the table
                    new_sub_district_data = {
                        "id": unique_rand,
                        "additionalinformation": excel_row["SD Code"],
                        "region_id": region_to_insert.id,
                        "district_id": district_to_insert.id,
                        # "DHIMS Facility": excel_row["DHIMS Facility"],
                        # "SORMAS Facility": validated_sub_district,
                        # "Comments": excel_row["Comments"],
                        "name": validated_entity,
                        # "Comments 2": excel_row["Comments 2"],
                        # Add other columns as needed
                    }
                    new_sub_district = Community(**new_sub_district_data)
                    session.add(new_sub_district)

                    logger.info("sub_district created")
                else:
                    logger.info(f"Invalid or missing data (District) for {validated_entity} in the excel input.")
                    return False, f"Invalid or missing data (District) for {validated_entity} in the excel input."

        return True
    except Exception as e:
        logger.info(f"Error inserting new facility record: {e}")
        return False


def insert_new_facility_record(excel_row, validated_facility):
    logger.info(f"=======insert_facility_record called======={validated_facility}")

    try:
        with session_scope() as session:
            sd_code = excel_row["SD Code"]
            logger.info(sd_code)

            if validated_facility is not None:
                region = excel_row["Region"]
                logger.info(region)
                district = excel_row["District"]
                logger.info(district)
                community = excel_row["Sub-District"]
                logger.info(community)

                if region is not None and district is not None and community is not None:

                    region_to_insert = session.query(Region).filter_by(name=region).first()
                    logger.info(region_to_insert)

                    if region_to_insert is not None:
                        district_to_insert = session.query(District).filter_by(name=district,
                                                                               region_id=region_to_insert.id).first()
                        logger.info(district_to_insert)

                        if district_to_insert is not None:
                            community_to_insert = session.query(Community).filter_by(
                                name=community, district_id=district_to_insert.id).first()
                            logger.info(community_to_insert)

                            logger.info(community_to_insert)
                            unique_rand = generate_unique_random_numbers()

                            existing_facility = session.query(Facility).filter_by(
                                name=validated_facility,
                                district_id=district_to_insert.id,
                                region_id=region_to_insert.id,
                                community_id=community_to_insert.id
                            ).first()

                            logger.info(f"==existing_facility==")
                            logger.info(existing_facility)

                            if existing_facility:
                                logger.info(f"Facility {validated_facility} already exists. Skipping insertion.")
                                return False, f"Facility {validated_facility} already exists. Skipping insertion"

                            # Insert entire record considering the specific matching field in the table
                            new_facility_data = {
                                "id": unique_rand,
                                "additionalinformation": sd_code,
                                "region_id": region_to_insert.id,
                                "district_id": district_to_insert.id,
                                "community_id": community_to_insert.id,
                                # "DHIMS Facility": excel_row["DHIMS Facility"],
                                # "SORMAS Facility": validated_facility,
                                # "Comments": excel_row["Comments"],
                                "name": validated_facility,
                                "type": FacilityType.HOSPITAL.name
                                # "Comments 2": excel_row["Comments 2"],
                                # Add other columns as needed
                            }
                            new_facility = Facility(**new_facility_data)
                            session.add(new_facility)

                            logger.info(f"Facility {new_facility} created Successfully")
                        else:
                            # Handle the case when district_to_insert is None
                            print(f"District not found for {validated_facility} in db.")
                    else:
                        # Handle the case when region_to_insert is None
                        print(f"Region not found for {validated_facility} in db.")
                else:
                    # Handle the case when any of the values are None
                    print(f"Invalid or missing data(Region/District/Sub-district) for "
                          f"{validated_facility} in the exel input.")
            else:
                print(f"Validated facility is Null for record with code {sd_code}. Exiting script.")

        return True
    except Exception as e:
        logger.info(f"Error inserting new facility record: {e}")
        return False


def insert_new_district_record(excel_row, validated_district):
    logger.info(f"=======insert_district_record called======={validated_district}")

    try:
        with session_scope() as session:
            region = excel_row["Region"]
            sd_code = excel_row["SD Code"]
            logger.info(region)
            if validated_district is not None:
                # Check for null values
                if region is not None:

                    # Check if region exists
                    region_to_insert = session.query(Region).filter_by(name=region).first()
                    if not region_to_insert:
                        logger.info(f"Region {region} not found. Skipping district insertion for {validated_district}.")
                        return False, f"Region {region} not found. Skipping district insertion for {validated_district}"

                    logger.info(f"Region {region_to_insert} found.")

                    unique_rand = generate_unique_random_numbers()

                    # Check if the district already exists
                    existing_district = session.query(District).filter_by(name=validated_district,
                                                                          region_id=region_to_insert.id).first()
                    logger.info(f"==existing_district==")
                    logger.info(existing_district)

                    if existing_district:
                        logger.info(f"District {validated_district} already exists. Skipping insertion.")
                        return False, f"District {validated_district} already exists. Skipping insertion"

                    # Insert entire record considering the specific matching field in the table
                    new_district_data = {
                        "id": unique_rand,
                        "additionalinformation": sd_code,
                        "region_id": region_to_insert.id,
                        "name": validated_district,
                    }
                    new_district = District(**new_district_data)
                    session.add(new_district)

                    logger.info(f"District {validated_district} created successfully.")
                    return True, f"District {validated_district} created successfully."
                else:
                    # Handle the case when any of the values are None
                    logger.info(f"Invalid or missing data (Region) for {validated_district} in the excel input.")
                    return False, f"Invalid or missing data (Region) for {validated_district} in the excel input."
            else:
                logger.info(f"Validated District Cannot be null for item with code {sd_code} please check excel file")

    except Exception as e:
        logger.info(f"Error inserting new district record: {e}")
        return False, f"Error inserting new district record: {e}"


def insert_new_sub_district_record(excel_row, validated_sub_district):
    logger.info(f"=======insert_sub_district_record called======={validated_sub_district}")

    try:
        with session_scope() as session:
            sd_code = excel_row["SD Code"]

            if validated_sub_district is not None:

                region = excel_row["Region"]
                logger.info(region)
                district = excel_row["District"]
                logger.info(district)
                # Check for null values
                if region is not None and district:

                    # Check if region exists
                    region_to_insert = session.query(Region).filter_by(name=region).first()
                    if not region_to_insert:
                        logger.info(
                            f"Region {region} not found. Skipping sub-district insertion for {validated_sub_district}.")
                        return False, f"Region {region} not found. Skipping sub-district insertion for {validated_sub_district}"

                    logger.info(f"Region {region_to_insert} found.")

                    # Check if district exists
                    district_to_insert = session.query(District).filter_by(name=district,
                                                                           region_id=region_to_insert.id).first()
                    if not district_to_insert:
                        logger.info(
                            f"District {district} not found. Skipping sub-district insertion for {validated_sub_district}.")
                        return False, f"District {district} not found. Skipping sub-district insertion for {validated_sub_district}"

                    logger.info(f"District {district_to_insert} found.")

                    unique_rand = generate_unique_random_numbers()

                    # Check if the sub-district already exists
                    existing_sub_district = session.query(Community).filter_by(name=validated_sub_district,
                                                                               district_id=district_to_insert.id).first()
                    logger.info("==existing_sub_district==")
                    logger.info(existing_sub_district)

                    if existing_sub_district:
                        logger.info(f"Sub District already exists. Skipping insertion for {district_to_insert} .")
                        return False, f"Sub District already exists. Skipping insertion for {district_to_insert}"

                    # Insert entire record considering the specific matching field in the table
                    new_sub_district_data = {
                        "id": unique_rand,
                        "additionalinformation": excel_row["SD Code"],
                        "region_id": region_to_insert.id,
                        "district_id": district_to_insert.id,
                        "name": validated_sub_district,
                    }

                    new_sub_district = Community(**new_sub_district_data)
                    session.add(new_sub_district)

                    logger.info(f"Sub-district {new_sub_district} created successfully.")
                    return True, f"Sub-district {new_sub_district} created successfully."
                else:
                    # Handle the case when any of the values are None
                    logger.info(f"Invalid or missing data (Region/District/Sub-district) for {validated_sub_district} "
                                f"in the excel input.")
                    return False, (
                        f"Invalid or missing data (Region/District/Sub-district) for {validated_sub_district}"
                        f" in the excel input.")
            else:
                logger.info(f"Validated Sub-district cannot be null for record with code {sd_code} "
                            f"please check the excel file")

    except Exception as e:
        logger.info(f"Error inserting new sub_district record: {e}")
        return False, f"Error inserting new sub_district record: {e}"


def generate_unique_random_numbers():
    unique_num = random.randint(10000, 999999)
    logger.info(unique_num)
    return unique_num


# # Example usage:
# unique_numbers = generate_unique_random_numbers(5)  # Generate 5 unique numbers
# logger.info(unique_numbers)

# Generating more unique numbers while avoiding previously generated ones:
# more_unique_numbers = generate_unique_random_numbers(5, existing_numbers=unique_numbers)
# logger.info(more_unique_numbers)


# def generate_complex_unique_number():
#     current_time = pd.datetime.datetime.utcnow()
#     timestamp_part = int(current_time.timestamp() * 1000000)  # Convert seconds to microseconds
#     random_part = random.randint(0, 99999)  # 5-digit random number
#
#     # Combine timestamp_part and random_part to form a six-character integer
#     six_char_unique_number = int(f"{timestamp_part:012d}{random_part:05d}")
#
#     return six_char_unique_number
# def generate_complex_unique_number():
#     current_time = pd.datetime.datetime.utcnow()
#     timestamp_part = int(current_time.timestamp()) * 1000000
#     random_part = random.randint(0, 99999)  # 5-digit random number
#
#     complex_unique_number = timestamp_part + random_part
#
#     return complex_unique_number


# def generate_complex_unique_number():
#     current_time = pd.datetime.datetime.utcnow()
#     timestamp_part = int(current_time.timestamp()) * 1000000
#     random_part = random.randint(100000, 999999)  # 6-digit random number
#
#     complex_unique_number = timestamp_part + random_part
#
#     return complex_unique_number

def update_entity(excel_row, entity_str):
    sormas_entity = excel_row[f'SORMAS {entity_str}']
    validated_entity = excel_row[f'Validated {entity_str}']
    logger.info(f"=======update_facility_name called======={sormas_entity} with {validated_entity}")
    try:
        with session_scope() as session:
            logger.info("in session scopes")
            logger.info(sormas_entity)

            # SQL query string
            sql_query = text("SELECT * FROM facility WHERE name = :name")

            # Execute the query and fetch results
            # facility_to_update = session.execute(sql_query, {"name": sormas_facility_name}).fetchone()
            # Check if the facility exists
            region = excel_row["Region"]
            logger.info(region)
            district = excel_row["District"]
            logger.info(district)
            community = excel_row["Sub-District"]
            logger.info(community)

            if region is not None:
                selected_region = session.query(Region).filter_by(name=region).first()
                logger.info(selected_region)

            if selected_region is not None:
                selected_district = session.query(District).filter_by(name=district,
                                                                      region_id=selected_region.id).first()
                logger.info(selected_district)

            if selected_district is not None:
                selected_community = session.query(Community).filter_by(name=community,
                                                                        district_id=selected_district.id).first()
            logger.info(selected_community)

            if entity_str == 'Facility':
                if selected_region is not None and selected_district is not None and selected_community is not None:

                    facilities_exist = session.query(Facility).filter_by(name=validated_entity,
                                                                         district_id=selected_district.id,
                                                                         region_id=selected_region.id,
                                                                         community_id=selected_community.id).all()
                    logger.info("facilities_exist")

                    logger.info(facilities_exist)

                    facilities_to_update = session.query(Facility).filter_by(name=sormas_entity,
                                                                             district_id=selected_district.id,
                                                                             region_id=selected_region.id,
                                                                             community_id=selected_community.id).all()

                    if not facilities_exist:
                        # If it doesn't exist, check if there's a facility to update

                        if not facilities_to_update:
                            logger.info("No records to update")
                        else:
                            if validated_entity is not None:
                                # Update facility names
                                for facility_to_update in facilities_to_update:
                                    logger.info(f"Updating {facility_to_update} with {validated_entity}")

                                    facility_to_update.name = validated_entity
                                    logger.info(f"{facility_to_update} Updated with {validated_entity} ")

                                # Commit the changes
                                session.commit()
                            else:
                                logger.info(f"Record {sormas_entity} can not be updated")

                    else:
                        # Delete existing facilities
                        if sormas_entity != validated_entity:
                            for facility_to_update in facilities_to_update:
                                logger.info(f"Deleting {facility_to_update} ")
                                session.delete(facility_to_update)
                                logger.info(f"{facility_to_update} deleted Successfully")
                        else:
                            logger.info(f"Record {sormas_entity} can not be deleted")

                    return True
                else:
                    # Handle the case when any of the values are None
                    print(f"Invalid or missing data(Region/District/Sub-district) for "
                          f"{validated_entity} in the exel input.")

            if entity_str == 'District':
                if selected_district is not None:

                    districts_exit = session.query(District).filter_by(name=validated_entity, region_id=region.id).all()
                    logger.info("districts_exit")

                    logger.info(districts_exit)

                    districts_to_update = session.query(District).filter_by(name=sormas_entity,
                                                                            region_id=region.id).all()

                    if not districts_exit:
                        # If it doesn't exist, check if there's a facility to update

                        if not districts_to_update:
                            logger.info("No records to update")
                        else:
                            if validated_entity is not None:
                                # Update facility names
                                for district_to_update in districts_to_update:
                                    logger.info(f"Updating {district_to_update}  with {validated_entity}")

                                    district_to_update.name = validated_entity
                                    logger.info(f"{districts_to_update} updated successfully with {validated_entity} ")

                                # Commit the changes
                                session.commit()
                            else:
                                logger.info(f"Record {sormas_entity} can not be updated")
                    else:
                        # Delete existing facilities
                        if sormas_entity != validated_entity:
                            for district_to_update in districts_to_update:
                                logger.info(f"Deleting {district_to_update} ")

                                session.delete(district_to_update)
                                session.commit()
                                logger.info(f"{district_to_update} deleted Successfully")
                        else:
                            logger.info(f"Record {sormas_entity} can not be deleted")

                    return True
                else:
                    # Handle the case when any of the values are None
                    print(f"Invalid or missing data(Region) for "
                          f"{validated_entity} in the exel input.")

            if entity_str == 'Sub District':
                if selected_district is not None:

                    sub_districts_exit = session.query(Community).filter_by(name=validated_entity,
                                                                            district_id=district.id).all()
                    logger.info("sub_districts_exit")

                    logger.info(sub_districts_exit)
                    sub_districts_to_update = session.query(Community).filter_by(name=sormas_entity,
                                                                                 district_id=district.id).all()

                    if not sub_districts_exit:
                        # If it doesn't exist, check if there's a sub_district to update

                        if not sub_districts_to_update:
                            logger.info("No records to update")
                        else:
                            if validated_entity is not None:
                                # Update facility names
                                for sub_district_to_update in sub_districts_to_update:
                                    logger.info(f"Updating {sub_district_to_update} with {validated_entity} ")

                                    sub_district_to_update.name = validated_entity
                                    logger.info(
                                        f"{sub_district_to_update} Updated Successfully with {validated_entity}")

                                # Commit the changes
                                session.commit()
                            else:
                                logger.info(f"Record {sormas_entity} can not be updated")

                    else:
                        if sormas_entity != validated_entity:

                            # Delete existing facilities
                            for sub_district_to_update in sub_districts_to_update:
                                logger.info(f"Deleting {sub_district_to_update} ")

                                session.delete(sub_district_to_update)
                                session.commit()

                                logger.info(f"{sub_district_to_update} deleted Successfully")
                        else:
                            logger.info(f"Record {sormas_entity} can not be deleted")

                    return True
                else:
                    # Handle the case when any of the values are None
                    print(f"Invalid or missing data(District) for "
                          f"{validated_entity} in the exel input.")

    except Exception as e:
        logger.info(f"Error updating data in PostgreSQL: {e}")
        return False


def update_facility_name(excel_row):
    sormas_facility = excel_row['SORMAS Facility']
    validated_facility = excel_row['Validated Facility']
    logger.info(f"=======update_facility_name called======={sormas_facility} with {validated_facility}")

    try:
        with session_scope() as session:
            logger.info("in session scopes")
            logger.info(sormas_facility)

            region = excel_row["Region"]
            logger.info(region)
            district = excel_row["District"]
            logger.info(district)
            community = excel_row["Sub-District"]
            logger.info(community)

            # Check for null values
            if region is not None and district is not None and community is not None and validated_facility is not None:
                selected_region = session.query(Region).filter_by(name=region).first()
                logger.info(selected_region)

                selected_district = session.query(District).filter_by(name=district).first()
                logger.info(selected_district)

                selected_community = session.query(Community).filter_by(name=community).first()
                logger.info(selected_community)

                if selected_region is not None and selected_district is not None and selected_community is not None:

                    # Check if facilities exist
                    facilities_exist = session.query(Facility).filter_by(name=validated_facility,
                                                                         district_id=selected_district.id,
                                                                         region_id=selected_region.id,
                                                                         community_id=selected_community.id).all()
                    logger.info("facilities_exist")
                    logger.info(facilities_exist)

                    # If facilities_exist is empty, check if there's a facility to update
                    facilities_to_update = session.query(Facility).filter_by(name=sormas_facility,
                                                                             district_id=selected_district.id,
                                                                             region_id=selected_region.id,
                                                                             community_id=selected_community.id).all()

                    if not facilities_exist:
                        logger.info("facilities_exist")
                        logger.info(facilities_exist)

                        if not facilities_to_update:
                            logger.info("No records to update")
                        else:
                            logger.info("validated_facility")
                            logger.info(validated_facility)

                            # Update facility names
                            for facility_to_update in facilities_to_update:
                                logger.info(f"Updating {facility_to_update} ")
                                facility_to_update.name = validated_facility
                                logger.info(f"{facility_to_update} is updated with {validated_facility} successfully")

                            # Commit the changes
                            session.commit()
                    else:

                        if sormas_facility != validated_facility:
                            # Delete existing facilities
                            for facility_to_update in facilities_to_update:
                                logger.info(f"Deleting {facility_to_update} ")
                                session.delete(facility_to_update)
                                logger.info(f"{facility_to_update} is deleted successfully")

                            session.commit()
                        else:
                            logger.info(f"Record {sormas_facility} can not be deleted")
                    return True
                logger.info(f"There is no matching values: Region/District/Sub-district for {sormas_facility} in the db")

            else:
                logger.info("Invalid or missing data in the excel input.")
                return False

    except Exception as e:
        logger.info(f"Error updating data in PostgreSQL: {e}")
        return False


def update_district_name(excel_row):
    sormas_district = excel_row['SORMAS District']
    validated_district = excel_row['Validated District Name']

    logger.info(f"=======update_district_name called======={sormas_district} with {validated_district}")

    try:
        with session_scope() as session:
            logger.info("in session scopes")
            logger.info(sormas_district)
            region = excel_row["Region"]
            logger.info(region)

            # Check for null values
            if region is not None and validated_district is not None:
                selected_region = session.query(Region).filter_by(name=region).first()
                logger.info(selected_region)

                # Check if districts exist
                districts_exist = session.query(District).filter_by(name=validated_district,
                                                                    region_id=selected_region.id).all()
                logger.info("exiting record districts_exist")
                logger.info(districts_exist)

                # If districts_exist is empty, check if there's a district to update
                districts_to_update = session.query(District).filter_by(name=sormas_district,
                                                                        region_id=selected_region.id).all()

                if not districts_exist:
                    logger.info("==districts_to_update==")
                    logger.info(districts_to_update)

                    if not districts_to_update:
                        logger.info("No records to update")
                    else:
                        if validated_district is not None:
                            # Update district names
                            for district_to_update in districts_to_update:
                                logger.info(f"Updating {district_to_update} with {validated_district} ")
                                district_to_update.name = validated_district
                                logger.info(f"{districts_to_update} Updated with {validated_district} Successfully")

                            # Commit the changes
                            session.commit()
                        else:
                            logger.info(f"Record {sormas_district} can not be updated")
                else:
                    if sormas_district != validated_district:
                        # Delete existing districts
                        for district_to_update in districts_to_update:
                            logger.info(f"Deleting {district_to_update} ")
                            session.delete(district_to_update)
                            session.commit()
                            logger.info(f" {district_to_update} Deleted Successfully")

                        logger.info("District already exists, deleting existing records and updating")
                    else:
                        logger.info(f"Record {sormas_district} can not be deleted")

                return True
            else:
                logger.info("Invalid or missing data in the excel input.")
                return False

    except Exception as e:
        logger.info(f"Error updating data in PostgreSQL: {e}")
        return False


def update_sub_district_name(excel_row):
    sormas_sub_district = excel_row['SORMAS Sub-District']
    validated_sub_district = excel_row['Validated Sub-district']
    logger.info(f"=======update_sub_district_name called======={validated_sub_district}")
    try:
        with session_scope() as session:

            logger.info("in session scopes")
            logger.info(sormas_sub_district)

            district = excel_row["District"]
            logger.info(district)

            # Check for null values
            if district is not None and validated_sub_district is not None:
                selected_district = session.query(District).filter_by(name=district).first()
                logger.info(selected_district)

                # Check if sub-districts exist
                sub_districts_exist = session.query(Community).filter_by(name=validated_sub_district,
                                                                         district_id=selected_district.id).all()
                logger.info("exiting sub_districts_exist")
                logger.info(sub_districts_exist)

                # If sub_districts_exist is empty, check if there's a sub_district to update
                sub_districts_to_update = session.query(Community).filter_by(name=sormas_sub_district,
                                                                             district_id=selected_district.id).all()

                if not sub_districts_exist:
                    if not sub_districts_to_update:
                        logger.info("No records to update")
                    else:
                        if validated_sub_district is not None:
                            # Update sub-district names
                            for sub_district_to_update in sub_districts_to_update:
                                logger.info(f"Updating {sub_district_to_update} with {validated_sub_district}")

                                sub_district_to_update.name = validated_sub_district
                                logger.info(
                                    f"{sub_district_to_update} Updated with {validated_sub_district} Successfully")

                            # Commit the changes
                            session.commit()
                        else:
                            logger.info(f"Record {sormas_sub_district} can not be updated")
                else:
                    if sormas_sub_district != validated_sub_district:
                        # Delete existing sub-districts
                        for sub_district_to_update in sub_districts_to_update:
                            logger.info(f"Deleting {sub_district_to_update} ")
                            session.delete(sub_district_to_update)
                            session.commit()

                            logger.info(f"{sub_district_to_update} Deleted Successfully")
                    else:
                        logger.info(f"Record {sormas_sub_district} can not be deleted")

                return True
            else:
                logger.info("Invalid or missing data in the excel input.")
                return False
    except Exception as e:
        logger.info(f"Error updating data in PostgreSQL: {e}")
        return False
