from flask import Blueprint, request, jsonify
from apifairy import body, response
from ..dao.sensor_dao import SensorDAO
from ..schemas import SensorRegistrationSchema, SensorSchema

sensor_blueprint = Blueprint('sensors', __name__, url_prefix="/api/v1/sensors")

sensors_schema = SensorSchema(many=True)


@sensor_blueprint.route('/', methods=['GET'])
@response(sensors_schema, 200)
def get_sensors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    sensors, total_items = SensorDAO.get_all(page, per_page)

    return sensors


@sensor_blueprint.route('/register', methods=['POST'])
# @body(SensorRegistrationSchema)
# @response(SensorSchema, 201)
def create_sensor():
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

    return jsonify(sensor.to_dict()), 201
