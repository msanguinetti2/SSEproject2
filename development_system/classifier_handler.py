from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from numpy import ravel
import joblib


class ClassifierHandler:

    def __init__(self, number_of_epochs, neurons_per_layer, number_of_layers, filename):
        self.filename = filename
        self.number_of_epochs = number_of_epochs
        self.neurons_per_layer = neurons_per_layer
        self.number_of_layers = number_of_layers
        self.training_accuracy = 0
        self.validation_accuracy = 0
        self.testing_accuracy = 0
        self.mlp = None
        self.hyperparameters = ()
        if number_of_layers is not None:
            for iterator in range(0, self.number_of_layers):
                self.hyperparameters = self.hyperparameters + (self.neurons_per_layer,)

    def train_neural_network(self, training_data, training_labels, validation_data, validation_labels):
        self.mlp = MLPClassifier(hidden_layer_sizes=self.hyperparameters, max_iter=self.number_of_epochs)

        print("Training_data\n: ", training_data)
        print("Training_labels\n: ", ravel(training_labels))
        print(type(training_data))
        print(type(ravel(training_labels)))
        self.mlp.fit(training_data, ravel(training_labels))
        self.training_accuracy = self.mlp.score(training_data, ravel(training_labels))

        validation_results = self.mlp.predict(validation_data)
        self.validation_accuracy = accuracy_score(ravel(validation_labels), validation_results)

    def test_neural_network(self, testing_data, testing_labels):
        testing_results = self.mlp.predict(testing_data)
        self.testing_accuracy = accuracy_score(ravel(testing_labels), testing_results)

    def load_neural_network_by_file(self):
        self.mlp = joblib.load(self.filename)
        self.number_of_epochs = self.mlp.n_iter_
        self.number_of_layers = self.mlp.n_layers_

        # Retrieve number of neurons per layer from filename
        # No attributes inside MLPClassifier class referring to that value
        self.neurons_per_layer = int(self.filename.split("_")[2].split(".")[0])

    def get_loss_curve(self):
        return self.mlp.loss_curve_

    def store_classifier_in_file(self):
        joblib.dump(self.mlp, self.filename)

    def get_filename(self):
        return self.filename

    def get_number_of_epochs(self):
        return self.number_of_epochs

    def get_neurons_per_layer(self):
        return self.neurons_per_layer

    def get_number_of_layers(self):
        return self.number_of_layers

    def get_training_accuracy(self):
        return self.training_accuracy

    def get_validation_accuracy(self):
        return self.validation_accuracy

    def get_testing_accuracy(self):
        return self.testing_accuracy
