from marshmallow import validate, fields, validates, validates_schema, \
    ValidationError, post_dump, pre_load
from api import ma, db
from api.models.sensor import Sensor
from api.models.lab import Lab
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field


class RegistrationAttributeSchema(ma.Schema):
    class Meta:
        model = Sensor
        ordered = True
        description = 'This schema represents an attribute.'

    attribute = fields.Str(required=True)
    is_key_attribute = fields.Int(required=True)


class RegistrationUrlSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Sensor
        ordered = True
        description = 'This schema represents a url.'

    url = fields.Str(required=True)
    url_type = fields.Str(required=True)


class SensorRegistrationSchemaOutput(ma.Schema):
    sensor_id = fields.Int(allow_none=True)
    sensor_uuid = fields.Str(allow_none=True)
    name = fields.Str()
    frequency = fields.Float(allow_none=True)
    category = fields.Str(allow_none=True)
    sensor_type = fields.Str(allow_none=True)
    sensor_vendor = fields.Str(allow_none=True)
    vendor_pid = fields.Str(allow_none=True)
    chip = fields.Str(allow_none=True)
    rpi_name = fields.Str(allow_none=True)
    rpi_id = fields.Int(allow_none=True)
    is_key_sensor = fields.Int(allow_none=True)
    machine_list = fields.List(fields.Str(allow_none=True))
    Attributes = fields.List(fields.Nested(RegistrationAttributeSchema))
    Urls = fields.List(fields.Nested(RegistrationUrlSchema))


class SensorRegistrationSchemaInput(ma.Schema):
    sensor_uuid = fields.Str(allow_none=True)
    name = fields.Str()
    frequency = fields.Float(allow_none=True)
    category = fields.Str(allow_none=True)
    sensor_type = fields.Str(allow_none=True)
    sensor_vendor = fields.Str(allow_none=True)
    vendor_pid = fields.Str(allow_none=True)
    chip = fields.Str(allow_none=True)
    rpi_name = fields.Str(allow_none=True)
    rpi_id = fields.Int(allow_none=True)
    is_key_sensor = fields.Int(allow_none=True)
    machine_list = fields.List(fields.Str(allow_none=True))
    Attributes = fields.List(fields.Nested(RegistrationAttributeSchema))
    Urls = fields.List(fields.Nested(RegistrationUrlSchema))


class SensorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Sensor
        ordered = True
        description = 'This schema represents a sensor'

    sensor_id = fields.Int()
    sensor_uuid = fields.Str()
    name = fields.Str()
    category = fields.Str()
    frequency = fields.Float()
    sensor_type = fields.Str()
    sensor_vendor = fields.Str()
    vendor_pid = fields.Str()
    chip = fields.Str()
    rpi_id = fields.Int()
    is_key_sensor = fields.Int()

    @validates('name')
    def validate_name(self, name):
        if len(name) < 3:
            raise ValidationError('Name must be greater than 3 characters.')
        if len(name) > 50:
            raise ValidationError('Name must be less than 50 characters.')

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')


class DetailsAttributesSchema(ma.Schema):
    id = fields.Int(allow_none=True)
    attribute_id = fields.Int(allow_none=True)
    level = fields.Int(allow_none=True)
    name = fields.Str()


class DetailsURLSchema(ma.Schema):
    main = fields.Str()
    preview = fields.Str()


class SensorDetailsSchema(ma.Schema):
    category = fields.Str(allow_none=True)
    frequency = fields.Float(allow_none=True)
    id = fields.Int(allow_none=True)
    machine_id = fields.Int(allow_none=True)
    machine_name = fields.Str(allow_none=True)
    name = fields.Str()
    attributes = fields.List(fields.Nested(DetailsAttributesSchema))
    urls = fields.Dict(keys=fields.Str(), values=fields.Str(), allow_none=True)

    # urls = fields.Nested(DetailsURLSchema)
    @pre_load
    def handle_empty_urls(self, data, **kwargs):
        if 'urls' in data and data['urls'] is None:
            data['urls'] = []  # Convert None to an empty list for consistent handling
        return data


# class SensorListResponseSchema(Schema):
#     sensors = fields.List(fields.Nested(SensorSchema))
#     total = fields.Int()


if __name__ == "__main__":
    # Example instance of SensorSchema
    sensor_schema = SensorSchema()

    # Test data matching the structure of SensorSchema
    test_sensor_data = {
        'sensor_id': 123,
        'sensor_uuid': '123e4567-e89b-12d3-a456-426655440000',
        'name': 'TemperatureSensor',
        'category': 'Environmental',
        'frequency': 5.5,
        'sensor_type': 'Thermometer',
        'sensor_vendor': 'SensorTech Inc.',
        'vendor_pid': 'ST-001',
        'chip': 'ChipModelX',
        'rpi_id': 789
    }

    update_test = {
        'name': 'TemperatureSensor',
        'category': 'Environmental',
        'frequency': 5.5,
        'sensor_type': 'Thermometer',
        'sensor_vendor': 'SensorTech Inc.',
        'vendor_pid': 'ST-001',
        'chip': 'ChipModelX',
        'rpi_id': 789
    }

    # Serializing the test data
    serialized_data = sensor_schema.dump(test_sensor_data)

    # Printing the serialized data
    print(serialized_data)
