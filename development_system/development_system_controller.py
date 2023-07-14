import os
import threading
import time
from multiprocessing.context import Process
import multiprocessing

import numpy as np
import requests

from development_system.classifier_handler import ClassifierHandler
from development_system.communication_handler import CommunicationHandler, ModuleRestParams
import json

from development_system.grid_search_handler import GridSearchHandler
from development_system.report_generator import ReportGenerator
import signal


class DevelopmentSystemController:

    def __init__(self):
        self.communication_handler = CommunicationHandler(self)

        development_configuration_file = open('development_configuration.json')
        self.development_configuration = json.load(development_configuration_file)
        development_configuration_file.close()

        self.communication_handler.add_schema(self.development_configuration["datasetSchema"], "dataset")

        self.mean_neurons_per_layer = round((self.development_configuration["minNeuronsPerLayer"] +
                                             self.development_configuration["maxNeuronsPerLayer"]) / 2)

        self.mean_number_of_layers = round((self.development_configuration["minNumberOfLayers"] +
                                            self.development_configuration["maxNumberOfLayers"]) / 2)

        development_internal_parameters_file = open('development_internal_parameters.json')
        self.development_internal_parameters = json.load(development_internal_parameters_file)
        development_internal_parameters_file.close()

        self.execution_params = ModuleRestParams(self.development_configuration["executionSystemIP"],
                                                 self.development_configuration["executionSystemPort"],
                                                 self.development_configuration["executionSystemPath"])

        if self.development_internal_parameters["status"] != "start":
            self.retrieve_dataset(self.development_internal_parameters["jsonDataset"])

        self.server_thread = None

    def __signal_handler(self, sign_num, frame):
        time.sleep(1)
        exit(0)

    def run(self):
        status = self.development_internal_parameters["status"]
        if status == "start":
            self.server_thread = threading.Thread(target=self.communication_handler.run, args=("127.0.0.1", 5001))
            self.server_thread.daemon = True
            self.server_thread.start()
            signal.signal(signal.SIGINT, self.__signal_handler)
            while True:
                time.sleep(300)

        elif status == "epoch_selection":
            self.start_epoch_selection_phase()

        elif status == "grid_search":
            print("Execution flow error")
            self.update_internal_file("epoch_selection", self.development_configuration["numberOfEpochs"], None)
            self.stop()

        elif status == "testing":
            network_filename = self.development_configuration["networkSelected"]
            if network_filename == "no_network":
                self.update_internal_file("grid_search", self.development_configuration["numberOfEpochs"], None)
                self.start_grid_search_phase()
            else:
                if os.path.isfile(network_filename):
                    self.start_test_phase(network_filename)
                else:
                    print("Wrong filename")
                    self.stop()

        elif status == "end":
            if self.development_configuration["testingResultCorrect"]:
                self.communication_handler.send_message_sav(self.development_configuration["networkSelected"],
                                                            self.execution_params,
                                                            self.development_internal_parameters["jsonDataset"]["clientId"])
            else:
                print("Error, require reconfiguration for client: ", self.development_internal_parameters["clientId"])

            self.update_internal_file("start", 0, {})
            self.stop()

    def handle_json(self, json_dataset, json_type):
        self.update_internal_file("epoch_selection", None, json_dataset)
        self.retrieve_dataset(json_dataset)
        self.start_epoch_selection_phase()

    def retrieve_dataset(self, json_dataset):
        training_dict = json_dataset["trainingDataset"]
        training_features_list = []
        for feature in training_dict["features"]:
            training_features_list.append(training_dict["features"][feature])

        self.training_features = np.transpose(np.array(training_features_list))
        self.training_labels = np.transpose(np.array(training_dict["labels"]))

        testing_dict = json_dataset["testDataset"]
        testing_features_list = []
        for feature in testing_dict["features"]:
            testing_features_list.append(testing_dict["features"][feature])

        self.testing_features = np.transpose(np.array(testing_features_list))
        self.testing_labels = np.transpose(np.array(testing_dict["labels"]))

        validation_dict = json_dataset["validationDataset"]
        validation_features_list = []
        for feature in validation_dict["features"]:
            validation_features_list.append(validation_dict["features"][feature])

        self.validation_features = np.transpose(np.array(validation_features_list))
        self.validation_labels = np.transpose(np.array(validation_dict["labels"]))

    def start_epoch_selection_phase(self):
        old_epoch_number = self.development_internal_parameters["oldNumberOfEpochs"]
        new_epoch_number = self.development_configuration["numberOfEpochs"]
        if old_epoch_number == new_epoch_number:
            self.update_internal_file("grid_search", None, None)
            self.start_grid_search_phase()
        else:
            self.update_internal_file(None, new_epoch_number, None)
            filename = "classifiers/classifier_" + str(self.mean_number_of_layers) + "_" + str(self.mean_neurons_per_layer) + ".sav"
            classifier = ClassifierHandler(new_epoch_number, self.mean_neurons_per_layer,
                                           self.mean_number_of_layers, filename)
            classifier.train_neural_network(self.training_features, self.training_labels,
                                            self.validation_features, self.validation_labels)
            report_generator = ReportGenerator()
            report_generator.generate_report(classifier, "training")
            self.stop()

    def start_grid_search_phase(self):
        print("Start grid search algorithm")
        grid_search_handler = GridSearchHandler(self.training_features, self.training_labels,
                                                self.validation_features, self.validation_labels,
                                                self.development_configuration["numberOfEpochs"])
        grid_search_handler.start_grid_search(self.development_configuration["minNumberOfLayers"],
                                              self.development_configuration["maxNumberOfLayers"],
                                              self.development_configuration["layersNumberStep"],
                                              self.development_configuration["minNeuronsPerLayer"],
                                              self.development_configuration["maxNeuronsPerLayer"],
                                              self.development_configuration["neuronsPerLayerStep"])
        self.update_internal_file("testing", None, None)
        self.stop()

    def start_test_phase(self, classifier_filename):
        print("Start test phase")
        classifier = ClassifierHandler(None, None, None, classifier_filename)
        classifier.load_neural_network_by_file()
        classifier.test_neural_network(self.testing_features, self.testing_labels)
        report_generator = ReportGenerator()
        report_generator.generate_report(classifier, "testing")
        self.update_internal_file("end", None, None)
        self.stop()

    def update_internal_file(self, status, old_number_of_epochs, json_dataset):
        if status is not None:
            self.development_internal_parameters["status"] = status

        if old_number_of_epochs is not None:
            self.development_internal_parameters["oldNumberOfEpochs"] = old_number_of_epochs

        if json_dataset is not None:
            self.development_internal_parameters["jsonDataset"] = json_dataset

        with open("development_internal_parameters.json", 'w') as outfile:
            json.dump(self.development_internal_parameters, outfile)

    def stop(self):
        if self.server_thread is not None:
            signal.raise_signal(signal.SIGINT)
        else:
            exit(0)

if __name__ == '__main__':
    development = DevelopmentSystemController()
    development.run()
