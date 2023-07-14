# This is a sample Python script.

# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import threading

import requests


def send():
    # Use a breakpoint in the code line below to debug your script.
    r = requests.post('http://127.0.0.1:5001/json',
                      json={"clientId": "lidl1",
                            "trainingDataset": {
                                "features": {
                                    "f1": [0.5, 0.7, 0.09],
                                    "f2": [0.15, 0.71, 0.19],
                                    "f3": [0.59, 0.87, 0.9321]
                                },
                                "labels": [1, 0, 1]
                            },
                            "validationDataset": {
                                "features": {
                                    "f1": [0.09],
                                    "f2": [0.19],
                                    "f3": [0.9321]
                                },
                                "labels": [1]
                            },
                            "testDataset": {
                                "features": {
                                    "f1": [0.7, 0.09],
                                    "f2": [0.71, 0.19],
                                    "f3": [0.87, 0.9321]
                                },
                                "labels": [0, 1]
                            }
                            })


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    send()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
