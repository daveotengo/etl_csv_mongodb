import uuid

from marshmallow import Schema, post_load, fields, validate
from sqlalchemy import Column, Integer, String, Enum, Float, Boolean, ForeignKey, Table, func, Sequence, BigInteger, \
    DateTime, true, false
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, column_property

from etlcsvmongodb.db_repo import Base
from etlcsvmongodb.enums import AreaType, FacilityType, Disease


class DateTimeAmount(object):
    def __init__(self, Datetime, amount, id):
        self.Datetime = Datetime
        self.amount = amount
        self.id = id


class DateTimeAmountSchema(Schema):
    # id = fields.Integer(validate=validate.Range(min=1), missing=0)
    id = fields.Str(required=True, validate=validate.Length(min=2))
    Datetime = fields.Str(required=True, validate=validate.Length(min=2))
    amount = fields.Str(required=True, validate=validate.Length(min=4), load_only=True)

    # neededd
    @post_load
    def make_date_time_amount(self, data, **kwargs):
        return DateTimeAmount(**data)


import json


def object_decoder(obj):
    if '__type__' in obj and obj['__type__'] == 'DateTimeAmount':
        return DateTimeAmount(obj['Datetime'], obj['amount'])
    return obj


date_time_amount_schema = DateTimeAmountSchema()


class Facility(Base):
    __tablename__ = 'facility'

    id = Column(BigInteger, primary_key=True, nullable=False, unique=True)

    name = Column(String)
    region_id = Column(String, ForeignKey('region.id'))
    district_id = Column(String, ForeignKey('district.id'))
    community_id = Column(String, ForeignKey('community.id'))
    #city = Column(String, server='Later' )
    # postalcode = Column(String)
    #
    # street = Column(String)
    # housenumber = Column(String)
    additionalinformation = Column(String)
    #areatype = Column(Enum(AreaType))
    # contactpersonfirstname = Column(String)
    # contactpersonlastname = Column(String)
    # contactpersonphone = Column(String)
    # contactpersonemail = Column(String)
    # latitude = Column(Float)
    # longitude = Column(Float)
    type = Column(Enum(FacilityType))
    publicownership = Column(Boolean, default=False)
    #externalid = Column(String)
    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)

    region = relationship("Region", back_populates="facilities")
    district = relationship("District", back_populates="facilities")
    community = relationship("Community", back_populates="facilities")
    changedate = Column(DateTime, default=func.now(), nullable=False)
    creationdate= Column(DateTime, default=func.now(), nullable=False)

    #
    diseases = relationship("DiseaseConfiguration", secondary='facility_diseaseconfiguration',
                            back_populates="facilities")

    def __repr__(self):
        return f"<Facility(id={self.id}, name={self.name})>"


class FacilityDiseaseConfiguration(Base):
    __tablename__ = 'facility_diseaseconfiguration'

    facility_id = Column(String, ForeignKey('facility.id'), primary_key=True)
    diseaseconfiguration_id = Column(String, ForeignKey('diseaseconfiguration.id'), primary_key=True)


CHARACTER_LIMIT_DEFAULT = 512


class Community(Base):
    __tablename__ = 'community'

    id = Column(String, primary_key=True)
    name = Column(String)
    district_id = Column(String, ForeignKey('district.id'))
    growthrate = Column(Float)
    externalid = Column(String)

    district = relationship("District", back_populates="communities")
    facilities = relationship("Facility", back_populates="community")  # Add this line

    def __repr__(self):
        return f"<Community(id={self.id}, name={self.name}, district={self.district}, ...)>"


class District(Base):
    __tablename__ = 'district'

    id = Column(String, primary_key=True)
    name = Column(String)
    region_id = Column(String, ForeignKey('region.id'))
    epidcode = Column(String)
    growthrate = Column(Float)
    externalid = Column(String)
    districtlatitude = Column(Float)
    districtlongitude = Column(Float)

    region = relationship("Region", back_populates="districts")
    communities = relationship("Community", back_populates="district", lazy='dynamic')
    # featureconfigurations = relationship("FeatureConfiguration", back_populates="district")
    facilities = relationship("Facility", back_populates="district")  # Add this line

    def __repr__(self):
        return f"<District(id={self.id}, name={self.name}, region={self.region}, ...)>"


class Region(Base):
    __tablename__ = 'region'

    id = Column(String, primary_key=True)
    name = Column(String)
    epidcode = Column(String)
    growthrate = Column(Float)
    externalid = Column(String)
    #area_id = Column(String, ForeignKey('area.id'))
    country_id = Column(String, ForeignKey('country.id'))

    districts = relationship("District", back_populates="region", lazy='dynamic')
    country = relationship("Country", back_populates="regions")
    facilities = relationship("Facility", back_populates="region")  # Add this line
    #area = relationship("Area", back_populates="regions")

    def __repr__(self):
        return f"<Region(id={self.id}, name={self.name}, country={self.country}, ...)>"


class DiseaseConfiguration(Base):
    __tablename__ = 'diseaseconfiguration'

    id = Column(Integer, primary_key=True)
    uuid = Column(String)  # Assuming there is a corresponding UUID field
    disease = Column(Enum(Disease), unique=True)
    active = Column(Boolean)
    primarydisease = Column(Boolean)
    casebased = Column(Boolean)
    followupenabled = Column(Boolean)
    followupduration = Column(Integer)
    casefollowupduration = Column(Integer)
    eventparticipantfollowupduration = Column(Integer)
    extendedclassification = Column(Boolean)
    extendedclassificationmulti = Column(Boolean)
    agegroups = Column(String)  # Assuming a serialized string representation

    # Assuming you have a Facility class defined
    facilities = relationship("Facility", secondary='facility_diseaseconfiguration')


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    external_id = Column(String())




class Country(Base):
    __tablename__ = 'country'

    id = Column(String, primary_key=True)
    defaultname = Column(String)
    externalid = Column(String)
    isocode = Column(String)
    unocode = Column(String)
    regions = relationship("Region", back_populates="country")  # Add this line

    #subcontinent_id = Column(String, ForeignKey('subcontinent.id'))

    #subcontinent = relationship("Subcontinent", back_populates="countries")

    def __repr__(self):
        return f"<Country(id={self.id}, default_name={self.defaultname}, iso_code={self.isocode}, ...)>"

    # @external_id.setter
    # def set_external_id(self, external_id):
    #     self.external_id = external_id

# class FeatureConfiguration(Base):
#     __tablename__ = "featureconfiguration"
#
#     feature_type = Column(EnumType(FeatureType), nullable=False)
#     entity_type = Column(EnumType(CoreEntityType))
#     region_id = Column(Integer, ForeignKey("region.id"))
#     region = relationship("Region")
#     district_id = Column(Integer, ForeignKey("district.id"))
#     district = relationship("District")
#     disease = Column(EnumType(Disease))
#     end_date = Column(DateTime)
#     enabled = Column(Boolean, nullable=False)
#     properties = Column(JSON)  # Assuming JSON type for properties
#
#     @classmethod
#     def build(cls, feature_type: FeatureType, enabled: bool) -> "FeatureConfiguration":
#         configuration = cls()
#         configuration.feature_type = feature_type
#         configuration.enabled = enabled
#         return configuration


# Define the association table for the many-to-many relationship
# facility_disease_configuration = Table('facility_diseaseconfiguration', Base.metadata,
#                                        Column('facility_id', String, ForeignKey('facility.id')),
#                                        Column('diseaseconfiguration_id', Integer, ForeignKey('diseaseconfiguration.id'))
#                                        )
