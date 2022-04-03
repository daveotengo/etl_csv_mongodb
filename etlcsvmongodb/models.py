from marshmallow import Schema, post_load, fields, validate


class DateTimeAmount(object):
    def __init__(self, Datetime, amount,id):
        self.Datetime = Datetime
        self.amount = amount
        self.id=id

class DateTimeAmountSchema(Schema):
    #id = fields.Integer(validate=validate.Range(min=1), missing=0)
    id = fields.Str(required=True, validate=validate.Length(min=2))
    Datetime = fields.Str(required=True, validate=validate.Length(min=2))
    amount = fields.Str(required=True, validate=validate.Length(min=4), load_only=True)

    #neededd
    @post_load
    def make_date_time_amount(self, data, **kwargs):
        return DateTimeAmount(**data)

import json
def object_decoder(obj):
    if '__type__' in obj and obj['__type__'] == 'DateTimeAmount':
        return DateTimeAmount(obj['Datetime'], obj['amount'])
    return obj


date_time_amount_schema = DateTimeAmountSchema()

