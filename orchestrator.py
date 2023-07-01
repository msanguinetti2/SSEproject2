import threading

import requests

# This is a sample Python script.

# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from flask import Flask, send_file, request
from flask_restful import Resource, Api
from pandas import read_csv
import requests
from jsonschema import validate, ValidationError
import json

app = Flask(__name__)
api = Api(app)

class Orchestrator(Resource):

    def post(self, type):
        if type=="msg":
            f = request.data.decode("utf-8")
            print(f)
            return "Message received"

    def startGeneric(self):
        requests.post("http://192.168.1.24:5001/msg", data="start")
        return "fine"

api.add_resource(Orchestrator, '/<string:type>')

if __name__ == '__main__':
    orch = Orchestrator()
    x = threading.Thread(target=orch.startGeneric, args=())
    x.start()
    app.run(debug=False, host='0.0.0.0', port=5006)











