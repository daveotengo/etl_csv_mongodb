from enum import Enum
from enum import Enum

from enum import Enum

from sqlalchemy.sql.coercions import cls


class FacilityTypeGroup(Enum):
    LEISURE_FACILITY = "LEISURE_FACILITY"
    WORKING_PLACE = "WORKING_PLACE"
    CATERING_OUTLET = "CATERING_OUTLET"
    ACCOMMODATION = "ACCOMMODATION"
    CARE_FACILITY = "CARE_FACILITY"
    RESIDENCE = "RESIDENCE"
    MEDICAL_FACILITY = "MEDICAL_FACILITY"
    EDUCATIONAL_FACILITY = "EDUCATIONAL_FACILITY"
    COMMERCE = "COMMERCE"


class FacilityType(Enum):
    ASSOCIATION = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    BUSINESS = (FacilityTypeGroup.WORKING_PLACE, False, False)
    BAR = (FacilityTypeGroup.CATERING_OUTLET, False, False)
    CAMPSITE = (FacilityTypeGroup.ACCOMMODATION, True, False)
    CANTINE = (FacilityTypeGroup.CATERING_OUTLET, False, False)
    CHILDRENS_DAY_CARE = (FacilityTypeGroup.CARE_FACILITY, False, False)
    CHILDRENS_HOME = (FacilityTypeGroup.RESIDENCE, True, False)
    CORRECTIONAL_FACILITY = (FacilityTypeGroup.RESIDENCE, True, False)
    CRUISE_SHIP = (FacilityTypeGroup.ACCOMMODATION, True, False)
    ELDERLY_DAY_CARE = (FacilityTypeGroup.CARE_FACILITY, False, False)
    EVENT_VENUE = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    FOOD_STALL = (FacilityTypeGroup.CATERING_OUTLET, False, False)
    HOLIDAY_CAMP = (FacilityTypeGroup.CARE_FACILITY, False, False)
    HOMELESS_SHELTER = (FacilityTypeGroup.RESIDENCE, True, False)
    HOSPITAL = (FacilityTypeGroup.MEDICAL_FACILITY, True, True)
    HOSTEL = (FacilityTypeGroup.ACCOMMODATION, True, False)
    HOTEL = (FacilityTypeGroup.ACCOMMODATION, True, False)
    KINDERGARTEN = (FacilityTypeGroup.EDUCATIONAL_FACILITY, False, False)
    LABORATORY = (FacilityTypeGroup.MEDICAL_FACILITY, False, False)
    MASS_ACCOMMODATION = (FacilityTypeGroup.ACCOMMODATION, True, False)
    MILITARY_BARRACKS = (FacilityTypeGroup.RESIDENCE, True, False)
    MOBILE_NURSING_SERVICE = (FacilityTypeGroup.CARE_FACILITY, False, False)
    NIGHT_CLUB = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    OTHER_ACCOMMODATION = (FacilityTypeGroup.ACCOMMODATION, True, False)
    OTHER_CARE_FACILITY = (FacilityTypeGroup.CARE_FACILITY, False, False)
    OTHER_CATERING_OUTLET = (FacilityTypeGroup.CATERING_OUTLET, False, False)
    OTHER_EDUCATIONAL_FACILITY = (FacilityTypeGroup.EDUCATIONAL_FACILITY, False, False)
    OTHER_LEISURE_FACILITY = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    OTHER_MEDICAL_FACILITY = (FacilityTypeGroup.MEDICAL_FACILITY, True, True)
    OTHER_RESIDENCE = (FacilityTypeGroup.RESIDENCE, True, False)
    OTHER_WORKING_PLACE = (FacilityTypeGroup.WORKING_PLACE, False, False)
    OTHER_COMMERCE = (FacilityTypeGroup.COMMERCE, False, False)
    OUTPATIENT_TREATMENT_FACILITY = (FacilityTypeGroup.MEDICAL_FACILITY, False, True)
    PLACE_OF_WORSHIP = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    PUBLIC_PLACE = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    REFUGEE_ACCOMMODATION = (FacilityTypeGroup.RESIDENCE, True, False)
    REHAB_FACILITY = (FacilityTypeGroup.MEDICAL_FACILITY, True, False)
    RESTAURANT = (FacilityTypeGroup.CATERING_OUTLET, False, False)
    RETIREMENT_HOME = (FacilityTypeGroup.RESIDENCE, True, False)
    RETAIL = (FacilityTypeGroup.COMMERCE, False, False)
    WHOLESALE = (FacilityTypeGroup.COMMERCE, False, False)
    SCHOOL = (FacilityTypeGroup.EDUCATIONAL_FACILITY, False, False)
    SWIMMING_POOL = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    THEATER = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    UNIVERSITY = (FacilityTypeGroup.EDUCATIONAL_FACILITY, False, False)
    ZOO = (FacilityTypeGroup.LEISURE_FACILITY, False, False)
    AMBULATORY_SURGERY_FACILITY = (FacilityTypeGroup.MEDICAL_FACILITY, False, False)
    DIALYSIS_FACILITY = (FacilityTypeGroup.MEDICAL_FACILITY, False, False)
    DAY_HOSPITAL = (FacilityTypeGroup.MEDICAL_FACILITY, False, False)
    MATERNITY_FACILITY = (FacilityTypeGroup.MEDICAL_FACILITY, True, True)
    MEDICAL_PRACTICE = (FacilityTypeGroup.MEDICAL_FACILITY, False, False)
    DENTAL_PRACTICE = (FacilityTypeGroup.MEDICAL_FACILITY, False, False)
    OTHER_MEDICAL_PRACTICE = (FacilityTypeGroup.MEDICAL_FACILITY, False, False)
    DIAGNOSTIC_PREVENTATIVE_THERAPEUTIC_FACILITY = (FacilityTypeGroup.MEDICAL_FACILITY, True, False)
    EMERGENCY_MEDICAL_SERVICES = (FacilityTypeGroup.MEDICAL_FACILITY, False, False)
    ELDERLY_CARE_FACILITY = (FacilityTypeGroup.CARE_FACILITY, True, False)
    DISABLED_PERSON_HABITATION = (FacilityTypeGroup.CARE_FACILITY, True, False)
    CARE_RECIPIENT_HABITATION = (FacilityTypeGroup.CARE_FACILITY, True, False)
    VISITING_AMBULATORY_AID = (FacilityTypeGroup.CARE_FACILITY, False, False)
    AFTER_SCHOOL = (FacilityTypeGroup.EDUCATIONAL_FACILITY, False, False)

    types_by_group = {}
    accomodation_types_by_group = {}
    place_of_birth_types = None

    # def __init__(self, group, accommodation, place_of_birth):
    #     self.facility_type_group = group
    #     self.accommodation = accommodation
    #     self.place_of_birth = place_of_birth

    def get_facility_type_group(self):
        return self.facility_type_group

    def is_accommodation(self):
        return self.accommodation

    def is_place_of_birth(self):
        return self.place_of_birth

    @classmethod
    def get_types(cls, group):
        if group is None:
            return None
        if group not in cls.types_by_group:
            facility_types = [facility_type for facility_type in cls if facility_type.facility_type_group == group]
            cls.types_by_group[group] = facility_types
        return cls.types_by_group[group]

    @classmethod
    def get_place_of_birth_types(cls):
        if cls.place_of_birth_types is None:
            cls.place_of_birth_types = [facility_type for facility_type in cls if facility_type.is_place_of_birth()]
        return cls.place_of_birth_types

    @classmethod
    def get_accommodation_types(cls, group):
        if group is None:
            return None
        if group not in cls.accomodation_types_by_group:
            facility_types = [facility_type for facility_type in cls if
                              facility_type.facility_type_group == group and facility_type.is_accommodation()]
            cls.accomodation_types_by_group[group] = facility_types
        return cls.accomodation_types_by_group[group]

    # FOR_FACILITY_23_IFSG_GERMANY = [
    #     cls.HOSPITAL,
    #     cls.AMBULATORY_SURGERY_FACILITY,
    #     cls.REHAB_FACILITY,
    #     cls.DIALYSIS_FACILITY,
    #     cls.DAY_HOSPITAL,
    #     cls.MATERNITY_FACILITY,
    #     cls.OTHER_MEDICAL_FACILITY,
    #     cls.MEDICAL_PRACTICE,
    #     cls.DENTAL_PRACTICE,
    #     cls.OTHER_MEDICAL_PRACTICE,
    #     cls.DIAGNOSTIC_PREVENTATIVE_THERAPEUTIC_FACILITY,
    #     cls.MOBILE_NURSING_SERVICE,
    #     cls.EMERGENCY_MEDICAL_SERVICES
    # ]
    #
    # FOR_COMMUNITY_FACILITY_GERMANY = [
    #     cls.KINDERGARTEN,
    #     cls.CHILDRENS_DAY_CARE,
    #     cls.SCHOOL,
    #     cls.CHILDRENS_HOME,
    #     cls.HOLIDAY_CAMP,
    #     cls.AFTER_SCHOOL,
    #     cls.OTHER_EDUCATIONAL_FACILITY
    # ]
    #
    # FOR_FACILITY_36_IFSG_GERMANY = [
    #     cls.OTHER_CARE_FACILITY,
    #     cls.ELDERLY_CARE_FACILITY,
    #     cls.DISABLED_PERSON_HABITATION,
    #     cls.CARE_RECIPIENT_HABITATION,
    #     cls.HOMELESS_SHELTER,
    #     cls.REFUGEE_ACCOMMODATION,
    #     cls.MASS_ACCOMMODATION,
    #     cls.CORRECTIONAL_FACILITY,
    #     cls.MOBILE_NURSING_SERVICE,
    #     cls.VISITING_AMBULATORY_AID
    # ]

    def __str__(self):
        return str(self.name)


class AreaType(Enum):
    URBAN = "URBAN"
    RURAL = "RURAL"
    UNKNOWN = "UNKNOWN"

    def __str__(self):
        return self.name  # Use the enum member's name as the string representation
# Assuming you have a function to get enum captions

class Disease(Enum):
    AFP = (True, True, True, False, 0, True, False, False)
    CHOLERA = (True, True, True, True, 5, True, False, False)
    CONGENITAL_RUBELLA = (True, True, True, True, 21, True, False, False)
    CSM = (True, True, True, False, 10, True, False, False)
    DENGUE = (True, True, True, False, 14, True, False, False)
    EVD = (True, True, True, True, 21, True, False, False)
    GUINEA_WORM = (True, True, True, False, 0, True, False, False)
    LASSA = (True, True, True, True, 21, True, False, False)
    MEASLES = (True, True, True, False, 21, True, True, False)
    MONKEYPOX = (True, True, True, True, 21, True, False, False)
    NEW_INFLUENZA = (True, True, True, True, 17, True, False, False)
    PLAGUE = (True, True, True, True, 7, True, False, False)
    POLIO = (True, True, True, False, 0, True, False, False)
    UNSPECIFIED_VHF = (True, True, True, True, 21, True, False, False)
    WEST_NILE_FEVER = (True, False, True, False, 0, True, False, False)
    YELLOW_FEVER = (True, True, True, False, 6, True, False, False)
    RABIES = (True, True, True, True, 6, True, False, False)
    ANTHRAX = (True, True, True, False, 0, True, False, False)
    CORONAVIRUS = (True, True, True, True, 14, True, True, True)
    PNEUMONIA = (True, False, True, False, 0, True, False, False)
    MALARIA = (True, False, False, False, 0, True, False, False)
    TYPHOID_FEVER = (True, False, False, False, 0, True, False, False)
    ACUTE_VIRAL_HEPATITIS = (True, False, False, False, 0, True, False, False)
    NON_NEONATAL_TETANUS = (True, False, False, False, 0, True, False, False)
    HIV = (True, False, False, False, 0, True, False, False)
    SCHISTOSOMIASIS = (True, False, False, False, 0, True, False, False)
    SOIL_TRANSMITTED_HELMINTHS = (True, False, False, False, 0, True, False, False)
    TRYPANOSOMIASIS = (True, False, False, False, 0, True, False, False)
    DIARRHEA_DEHYDRATION = (True, False, False, False, 0, True, False, False)
    DIARRHEA_BLOOD = (True, False, False, False, 0, True, False, False)
    SNAKE_BITE = (True, False, False, False, 0, True, False, False)
    RUBELLA = (True, False, False, False, 0, True, False, False)
    TUBERCULOSIS = (True, False, False, False, 0, True, False, False)
    LEPROSY = (True, False, False, False, 0, True, False, False)
    LYMPHATIC_FILARIASIS = (True, False, False, False, 0, True, False, False)
    BURULI_ULCER = (True, False, False, False, 0, True, False, False)
    PERTUSSIS = (True, False, False, False, 0, True, False, False)
    NEONATAL_TETANUS = (True, False, False, False, 0, True, False, False)
    ONCHOCERCIASIS = (True, False, False, False, 0, True, False, False)
    DIPHTERIA = (True, False, False, False, 0, True, False, False)
    TRACHOMA = (True, False, False, False, 0, True, False, False)
    YAWS_ENDEMIC_SYPHILIS = (True, False, False, False, 0, True, False, False)
    MATERNAL_DEATHS = (True, False, False, False, 0, True, False, False)
    PERINATAL_DEATHS = (True, False, False, False, 0, True, False, False)
    INFLUENZA_A = (True, False, True, False, 0, True, False, False)
    INFLUENZA_B = (True, False, True, False, 0, True, False, False)
    H_METAPNEUMOVIRUS = (True, False, True, False, 0, True, False, False)
    RESPIRATORY_SYNCYTIAL_VIRUS = (True, False, True, False, 0, True, False, False)
    PARAINFLUENZA_1_4 = (True, False, True, False, 0, True, False, False)
    ADENOVIRUS = (True, False, True, False, 0, True, False, False)
    RHINOVIRUS = (True, False, True, False, 0, True, False, False)
    ENTEROVIRUS = (True, False, True, False, 0, True, False, False)
    M_PNEUMONIAE = (True, False, True, False, 0, True, False, False)
    C_PNEUMONIAE = (True, False, True, False, 0, True, False, False)
    ARI = (True, False, False, False, 0, True, False, False)
    CHIKUNGUNYA = (True, False, False, False, 0, True, False, False)
    POST_IMMUNIZATION_ADVERSE_EVENTS_MILD = (True, False, False, False, 0, True, False, False)
    POST_IMMUNIZATION_ADVERSE_EVENTS_SEVERE = (True, False, False, False, 0, True, False, False)
    FHA = (True, False, False, False, 0, True, False, False)
    OTHER = (True, True, True, True, 21, False, False, False)
    UNDEFINED = (True, True, True, True, 0, False, False, False)

    def __init__(
        self,
        default_active,
        default_primary,
        default_case_based,
        default_follow_up_enabled,
        default_follow_up_duration,
        variant_allowed,
        default_extended_classification,
        default_extended_classification_multi
    ):
        self.default_active = default_active
        self.default_primary = default_primary
        self.default_case_based = default_case_based
        self.default_follow_up_enabled = default_follow_up_enabled
        self.default_follow_up_duration = default_follow_up_duration
        self.variant_allowed = variant_allowed
        self.default_extended_classification = default_extended_classification
        self.default_extended_classification_multi = default_extended_classification_multi

    def __str__(self):
        return self.name

    def to_short_string(self):
        return self.name

    def get_name(self):
        return self.name

    def uses_simple_view_for_outbreaks(self):
        return self == Disease.CSM  # Add other cases as needed

    def is_default_active(self):
        return self.default_active

    def is_default_primary(self):
        return self.default_primary

    def is_default_case_based(self):
        return self.default_case_based

    def is_default_follow_up_enabled(self):
        return self.default_follow_up_enabled

    def get_default_follow_up_duration(self):
        return self.default_follow_up_duration

    def is_disease_group(self):
        return self == Disease.UNSPECIFIED_VHF

    def is_variant_allowed(self):
        return self.variant_allowed

    def is_default_extended_classification(self):
        return self.default_extended_classification

    def is_default_extended_classification_multi(self):
        return self.default_extended_classification_multi

    def key_compare_to(self, o):
        if o is None:
            raise ValueError("Can't compare to None.")
        if not isinstance(o, Disease):
            raise NotImplementedError(f"Can't compare to class {type(o).__name__} that differs from Disease.")
        return str(self).compare_to(str(o))


DISEASE_LIST = list(Disease)
