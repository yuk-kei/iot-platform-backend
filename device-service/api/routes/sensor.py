from flask import Blueprint, request, jsonify
from apifairy import body, response
from ..dao.sensor_dao import SensorDAO
from ..schemas.sensor_schema import SensorRegistrationSchema, SensorSchema, SensorDetailsSchema, SensorUpdateSchema

sensor_blueprint = Blueprint('sensors', __name__, url_prefix="/api/v1/sensors")

sensors_schema = SensorSchema(many=True)
detail_schema = SensorDetailsSchema(many=True)
update_schema = SensorUpdateSchema()


@sensor_blueprint.route('/', methods=['GET'])
@response(sensors_schema, 200)
def get_sensors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 200, type=int)
    sensors, total_items = SensorDAO.get_all(page, per_page)

    return sensors


@sensor_blueprint.route('/details', methods=['GET'])
@response(detail_schema, 200)
def get_sensors_details():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 200, type=int)
    sensors, total_items = SensorDAO.get_all_details(page, per_page)
    print(type(sensors))
    return sensors


@sensor_blueprint.route('/register', methods=['POST'])
@body(SensorRegistrationSchema)
@response(SensorSchema, 201)
def create_sensor(param=None):
    sensor_info = request.get_json()
    rpi_name = sensor_info.pop('rpi_name', None)
    machine_lists = sensor_info.pop('machine_list', [])
    attributes = sensor_info.pop('Attributes', [])
    urls = sensor_info.pop('Urls', [])

    sensor = SensorDAO.create(sensor_info=sensor_info,
                              rpi_name=rpi_name,
                              machine_names=machine_lists,
                              attributes=attributes,
                              urls=urls)
    return sensor, 201


@sensor_blueprint.route('/key-attribute', methods=['GET'])
def get_key_attribute():
    sensor_identifier = request.args.get('sensor_identifier', None)
    attr_key_level = request.args.get('attr_key_level', None)
    try:
        # Attempt to convert to an integer
        sensor_identifier = int(sensor_identifier)
    except ValueError:
        sensor_identifier = sensor_identifier
    key_attribute = SensorDAO.get_key_attribute(sensor_identifier=sensor_identifier,
                                                attr_key_level=attr_key_level)
    return jsonify(key_attribute)

@sensor_blueprint.route('/<sensor_identifier>/result', methods=['PUT'])
@body(update_schema)
@response(SensorSchema, 201)
def update_sensor_result(*args, sensor_identifier):
    sensor_info = request.get_json()
    try:
        # Attempt to convert to an integer
        sensor_identifier = int(sensor_identifier)
    except ValueError:
        sensor_identifier = sensor_identifier
    sensor_result = SensorDAO.update(sensor_identifier, sensor_info)
    return sensor_result