import subprocess
import sys
import threading

from flask import Flask, request, send_file
from dataclasses import dataclass
import requests
import json
from jsonschema import validate, ValidationError


@dataclass
class ModuleRestParams:
    host: str
    port: int
    path: str = '/'


class CommunicationHandler:

    # make it a singleton
    def __new__(cls, *a, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, controller):
        self.app = Flask(__name__)
        self.schemas = []
        self.app.add_url_rule('/json', view_func=self.receive_message_json, methods=['POST'])
        self.app.add_url_rule('/sav', view_func=self.receive_message_sav, methods=['POST'])

        if not hasattr(controller, 'handle_json'):
            raise Exception('Controller must have a handle_json method')
        self.controller = controller

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port, debug=True, use_reloader=False)

    def add_schema(self, schema, schema_type):
        self.schemas.append((schema, schema_type))

    def validate_json(self, json_file, schema):
        try:
            validate(instance=json_file, schema=schema)
        except ValidationError as v:
            # print("JSON not valid: following error occured. \n" + v.message)
            return 0
        return 1

    def receive_message_json(self):
        json_document = request.get_json()
        result = 0
        json_type = ""
        for (schema, schema_type) in self.schemas:
            validation = self.validate_json(json_document, schema)
            result = result + validation
            if validation == 1:
                json_type = schema_type
        if result > 0:
            self.controller.handle_json(json_document, json_type)
        return "ok"

    def receive_message_sav(self):
        client_id = request.form["client_id"]
        file_sav = request.files['file']
        # file_sav.save("newFitted.sav")
        self.controller.handle_sav(file_sav)
        return "ok"

    def send_message_json(self, json_document: dict, receiver: ModuleRestParams) -> str:
        r = requests.post(f'http://{receiver.host}:{receiver.port}{receiver.path}/json', json=json_document)
        r.raise_for_status()
        return r.text

    def send_message_sav(self, sav_filename: str, receiver: ModuleRestParams, client_id):
        r = requests.post(f'http://{receiver.host}:{receiver.port}{receiver.path}/sav',
                          files={'file': open(sav_filename, 'rb')}, data={'client_id': client_id})
        return r.text

    def stop(self):
        pass
