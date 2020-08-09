import os
import shelve
import markdown

# Import the framework
from flask import Flask, g
from flask_restful import Resource, Api, reqparse

# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("devices.db")
    return db


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    """
    Print documentation
    """
    # Open the README file
    with open(os.path.dirname(app.root_path) + "/readme.md") as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)


class DeviceList(Resource):

    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        devices = []

        for key in keys:
            devices.append(shelf[key])

        # For success return 200, OK
        return {'message': 'Success!!!', 'data': devices}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('identifier', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('device_type', type=str, required=True)
        parser.add_argument('controller_gateway', type=str, required=True)

        # Parse the arguments into and object
        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        # For success return 201, Created
        return {'message': 'Device registered!!!', 'data': args}, 201


class Device(Resource):

    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return 404 error.
        if not(identifier in shelf):
            return {'message': 'Device not found!!!', 'data': {}}, 404

        # For success return 200, OK
        return {'message': 'Device found!!!', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return 404 error.
        if not(identifier in shelf):
            return {'message': 'Device not found!!!', 'data': {}}, 404

        # Delete data corresponding to identifier passed
        del shelf[identifier]

        # For success return 204, no content
        return "", 204


api.add_resource(DeviceList, '/devices')
api.add_resource(Device, '/device/<string:identifier>')
