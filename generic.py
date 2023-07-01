# This is a sample Python script.

# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import threading
from time import sleep

from flask import Flask, send_file, request
from flask_restful import Resource, Api
from pandas import read_csv
import requests
from jsonschema import validate, ValidationError
import json
import cv2
import sqlite3
import mysql.connector

app = Flask(__name__)
api = Api(app)

class Generic(Resource):

    def createdb(self):
        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='sse',
                                                 user='root',
                                                 password='')

            mySql_Create_Table_Query = """CREATE TABLE IF NOT EXISTS names ( 
                                     id int(11) NOT NULL AUTO_INCREMENT,
                                     name varchar(250) NOT NULL,
                                     age tinyint NOT NULL,
                                     PRIMARY KEY (id)) """

            cursor = connection.cursor()
            result = cursor.execute(mySql_Create_Table_Query)
            print("Table created successfully ")

        except mysql.connector.Error as error:
            print("Failed to create table in MySQL: {}".format(error))
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")


    def insertdb(self, name, age):
        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='sse',
                                                 user='root',
                                                 password='')

            insert_values = """INSERT INTO names (name, age) VALUES (%s, %s) """

            tuple = (name, age)

            cursor = connection.cursor(prepared=True)
            result = cursor.execute(insert_values, tuple)
            print("Values inserted successfully ")

        except mysql.connector.Error as error:
            print("Failed to insert values in MySQL: {}".format(error))
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")


    def post(self, type):
        if type=="sav":
            f = request.files['file']
            f.save("./data/model.sav")
            return "File uploaded successfully"

        elif type=="json":
            myjson = request.get_json()
            if self.validateJSON(myjson) == 0:
                print(myjson)
                y = json.loads(myjson)
                self.insertdb(y["name"], y["age"])
            else:
                return "Invalid JSON"

        elif type=="msg":
            f = request.data.decode("utf-8")
            print(f)
            if f == "start":
                threadSendPeer = threading.Thread(target=self.sendPostRequest, args=('192.168.1.24:5002', 'msg', 'hi'))
                threadSendPeer.start()
                return "generic1"
            else:
                return "Message received"

        elif type == "png":
            f = request.files['file']
            f.save("./data/immagine.png")
            return "Image uploaded successfully"

    def validateJSON(self, jsonFile):
        try:
            schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                },
                "required": ["name"],
            }
            validate(instance=jsonFile, schema=schema)
        except ValidationError as v:
            print("JSON not valid: following error occured. \n" + v.message)
            return -1
        return 0

    def sendPostRequest(self, address, type, object):
        if type == "json":
            #TODO: controllare che object sia un file json
            r = requests.post("http://" + address + "/" + type, json=object)
            print("Response:" + r.text)

        elif type == "sav":
            #TODO: controllare che object sia un filename e che sia corretto
            r = requests.post("http://" + address + "/" + type, files={'file': open(object, 'rb')})
            print("Response:" + r.text)

        elif type == "msg":
            #TODO: controllare che object sia un messaggio
            r = requests.post("http://" + address + "/" + type, data=object)
            print("Response: " + r.text)

        elif type == "png":
            #TODO: controllare che object sia un filename e che sia corretto
            r = requests.post("http://" + address + "/" + type, files={'file': open(object, 'rb')})
            print("Response:" + r.text)
        return


api.add_resource(Generic, '/<string:type>')

if __name__ == '__main__':
    gen = Generic()
    gen.createdb()
    app.run(debug=True, host='0.0.0.0', port=5001)





