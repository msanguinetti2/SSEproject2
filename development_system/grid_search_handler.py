import math
import os
import joblib
from sklearn.model_selection import ParameterGrid

from development_system.classifier_handler import ClassifierHandler
from development_system.report_generator import ReportGenerator
import os


class GridSearchHandler:

    def __init__(self, training_data, training_labels, validation_data, validation_labels, number_of_epochs):
        self.training_data = training_data
        self.training_labels = training_labels
        self.validation_data = validation_data
        self.validation_labels = validation_labels
        self.number_of_epochs = number_of_epochs
        self.top_classifier_list = []

    def start_grid_search(self, min_number_of_layers, max_number_of_layers, layers_number_step,
                          min_neurons_per_layer, max_neurons_per_layer, neurons_per_layer_step):

        number_of_layers_list = []
        for value in range(min_number_of_layers, max_number_of_layers + 1, layers_number_step):
            number_of_layers_list.append(value)

        neurons_per_layer_list = []
        for value in range(min_neurons_per_layer, max_neurons_per_layer + 1, neurons_per_layer_step):
            neurons_per_layer_list.append(value)

        grid_search_hyperparameters = list(ParameterGrid({"number_of_layers": number_of_layers_list,
                                                          "neurons_per_layer": neurons_per_layer_list}))

        for hyperparameters in grid_search_hyperparameters:
            number_of_layers = hyperparameters["number_of_layers"]
            neurons_per_layer = hyperparameters["neurons_per_layer"]

            print("Grid search iteration: ", number_of_layers, neurons_per_layer)

            filename = "classifiers/classifier_" + str(number_of_layers) + "_" + str(neurons_per_layer) + ".sav"
            classifier = ClassifierHandler(self.number_of_epochs, neurons_per_layer, number_of_layers, filename)
            classifier.train_neural_network(self.training_data, self.training_labels, self.validation_data,
                                            self.validation_labels)

            # ADD CLASSIFIER TO LIST
            self.insert_top_five(classifier)

        # grid search ended
        report_generator = ReportGenerator()
        report_generator.generate_training_report_top_five(self.top_classifier_list)

    def insert_top_five(self, classifier):
        if len(self.top_classifier_list) == 5:
            index_lowest = self.check_top_five(classifier)

            # Insert in top five
            if index_lowest >= 0:
                file_to_remove = self.top_classifier_list[index_lowest].get_filename()
                if os.path.isfile(file_to_remove):
                    os.remove(file_to_remove)
                self.top_classifier_list[index_lowest] = classifier
                classifier.store_classifier_in_file()
        else:
            self.top_classifier_list.append(classifier)

    def check_top_five(self, classifier):
        index = 0
        min_validation = self.top_classifier_list[0].get_validation_accuracy()
        for top_classifier in self.top_classifier_list:
            curr_validation = top_classifier.get_validation_accuracy()
            if curr_validation < min_validation:
                min_validation = curr_validation
                index = self.top_classifier_list.index(top_classifier)

        if min_validation < classifier.get_validation_accuracy():
            return index
        else:
            return -1

