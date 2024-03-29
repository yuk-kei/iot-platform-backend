import time, uuid

from .models import Device, db
from flask import Blueprint, request, jsonify

"""
Routes Module

This module defines the api (endpoints) used in the api. Each route is associated with a specific
HTTP request method (e.g., GET, POST, PUT, DELETE) and performs a specific action when accessed. The route
functions typically interact with the api's business logic and data access layers to perform the
required actions and return the appropriate HTTP response.

Current Routes:
    - /test: Test endpoint to check if the device-related endpoints are accessible and functioning.
    - /api/devices/register: Endpoint to register a device or check if a device is already registered.
    - /api/devices/delete: Endpoint to delete a device based on device_id.
    - /api/devices/update: Endpoint to update a device's details based on the device_id.
    - /api/devices/get_type: Endpoint to retrieve a list of devices based on their type.
    - /api/devices/filter_by: Endpoint to filter devices based on a specific field name and value.

Expected Additions:
    More api are anticipated to be added to this module as the api expands. These may include
    api for user authentication, transaction logging, etc.

"""
devices_blueprint = Blueprint('devices', __name__, url_prefix="/api/devices")


@devices_blueprint.route('/test')
def hello():
    """
    Test Endpoint
    This route is used to check if the device-related endpoints are accessible and functioning.

    :return: A simple greeting string confirming the accessibility of the endpoint.
    """
    return '<h1>Home</h1>'


@devices_blueprint.route("/register", methods=['POST', 'GET'])
def check_register():
    """
    Register a device or check if a device is already registered.

    For a POST request, it will either register a new device or check if the provided device_id is already in the database.
    For a GET request, it will return all the registered devices.

    :return: A JSON response indicating the status or a list of registered devices.
    """
    if request.method == 'POST':
        device_id = request.json.get('device_id')
        name = request.json.get('name')
        type = request.json.get('type')
        category = request.json.get('category')
        location = request.json.get('location')
        status = request.json.get('status')
        ip_address = request.json.get('ip_address')
        port = request.json.get('port')
        frequency = request.json.get('frequency', 0)

        # Check if a device with the same name already exists
        device = Device.query.filter_by(name=name).first()

        if device:
            return jsonify({'message': 'Device with this name is already registered.'}), 409  # Conflict status code

        if not device_id:
            device_id = next_short_id()
            new_device = Device(id=device_id, name=name, type=type, category=category, location=location, status=status,
                                ip_address=ip_address, port=port, frequency=frequency)
            db.session.add(new_device)
            db.session.commit()
            return jsonify({'device_id': device_id}), 201
        else:
            device = Device.query.get(device_id)
            if device:
                return jsonify({'message': 'Device already registered.'}), 409
            if not device:
                new_device = Device(id=device_id, name=name, type=type, category=category, location=location,
                                    status=status, ip_address=ip_address, port=port)
                db.session.add(new_device)
                db.session.commit()
                return jsonify({'Successfully registered device': device_id}), 201

    elif request.method == 'GET':
        # Logic for handling GET requests
        devices = Device.query.all()
        device_list = [{'device_id': device.id, 'name': device.name, 'type': device.type, 'location': device.location,
                        'category': device.category, 'status': device.status, 'ip_address': device.ip_address,
                        'port': device.port, 'frequency': device.frequency} for device in devices]
        return jsonify(device_list), 200


@devices_blueprint.route("/delete", methods=['POST', 'GET'])
def delete_device():
    """
    Delete a device based on device_id.

    The route will look for the device with the provided device_id and delete it if found.

    :return: A JSON response indicating the status of the deletion operation.
    """
    ...
    device_id = request.json.get('device_id')
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'device_id': device.id, 'message': 'Device deleted!'}), 200
    else:
        return jsonify({'message': 'Device ID not found in database.'}), 404


@devices_blueprint.route("/update", methods=['POST', 'GET', 'PUT'])
def update_device():
    """
    Update a device's details based on the device_id.

    For the device with the provided device_id, its attributes will be updated with the provided details.

    :return: A JSON response indicating the status of the update operation.
    """
    device_id = request.json.get('device_id')

    if not device_id:
        return jsonify({'message': 'Device ID not provided.'}), 400
    print(device_id)
    device = Device.query.get(device_id)

    if not device:
        return jsonify({'message': 'Device ID not found in database.'}), 404

    updated = False

    if request.json.get('name') and device.name != request.json.get('name'):
        device.name = request.json.get('name')
        updated = True

    if request.json.get('type') and device.type != request.json.get('type'):
        device.type = request.json.get('type')
        updated = True

    if request.json.get('location') and device.location != request.json.get('location'):
        device.location = request.json.get('location')
        updated = True

    if request.json.get('category') and device.category != request.json.get('category'):
        device.category = request.json.get('category')
        updated = True

    if request.json.get('status') and device.status != request.json.get('status'):
        device.status = request.json.get('status')
        updated = True

    if request.json.get('ip_address') and device.ip_address != request.json.get('ip_address'):
        device.ip_address = request.json.get('ip_address')
        updated = True

    if request.json.get('port') and device.port != request.json.get('port'):
        device.port = request.json.get('port')
        updated = True

    if request.json.get('frequency') and device.frequency != request.json.get('frequency'):
        device.frequency = request.json.get('frequency')
        updated = True

    if updated:
        db.session.commit()
        return jsonify({'message': 'Device updated.', 'device_id': device.id}), 200
    else:
        return jsonify({'message': 'No updates were made to the device.'}), 400


@devices_blueprint.route("/get_type")
def get_type():
    """
    Retrieve a list of devices based on their type.

    The route will filter and return devices that match the provided type.

    :return: A JSON response containing a list of devices of the given type.
    """
    type = request.json.get('type')
    devices = Device.query.filter_by(type=type).all()
    device_list = [{'device_id': device.id, 'name': device.name, 'type': device.type,
                    'location': device.location, 'category': device.category, 'status': device.status,
                    'ip_address': device.ip_address, 'port': device.port, 'frequency': device.frequency} for device in devices]
    return jsonify(device_list), 200


@devices_blueprint.route("/filter_by", methods=['POST', 'GET'])
def filter_by_field():
    """
    Filter devices based on a specific field name and value.

    This route will dynamically filter devices based on the field_name and field_value provided in the request.

    :return: A JSON response containing a list of devices that match the criteria or an error message.
    """
    # Get the field name and value from the request
    field_name = request.json.get('field_name')
    field_value = request.json.get('field_value')
    # Check if the field is present in the Device model
    if hasattr(Device, field_name):
        # Construct the filter dynamically based on the field name and value
        filter_kwargs = {field_name: field_value}
        devices = Device.query.filter_by(**filter_kwargs).all()
        device_list = [{'device_id': device.id, 'name': device.name, 'type': device.type,
                        'location': device.location, 'category': device.category, 'status': device.status,
                        'ip_address': device.ip_address, 'port': device.port, 'frequency': device.frequency} for device in devices]
        return jsonify(device_list), 200
    else:
        return jsonify({'message': 'Field name not found '}), 404


def next_short_id():
    """
    Generate a short unique device ID.

    This utility function combines the current time and a portion of a UUID to produce a unique string.

    :return: A unique string to be used as a device_id.
    """
    current_time_str = str(int(time.time()))
    uid = uuid.uuid4().bytes_le[:4].hex()
    return current_time_str + uid
