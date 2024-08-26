from flask import jsonify, request
from flask_smorest import Blueprint, abort
import requests

# Define a Blueprint for the API
NS_TEST = Blueprint("sample", "sample", url_prefix="/api", description="A sample API")


@NS_TEST.route("/hello", endpoint='api-hello')
def hello():

    print('\nHello Start')
    response = requests.get('http://127.0.0.1:5001/api/propagate?test=99')
    print(response.headers)
    print(response.json())
    print('Hello END\n')
    return jsonify(response.json())

@NS_TEST.route("/propagate",  endpoint='api-propagate')
def propagate():
    print('\n\nPropagate >> ', request.headers, '\n\n')
    return jsonify(message="Hello, World!")


@NS_TEST.route("/error",  endpoint='api-error')
def error():
    abort(400, message="This is a bad request")
