# report fields:
# hyperparameters: number of neurons, n of layers
# training accuracy (passati come parametri)
# validation accuracy (passati come parametri)
# numero di epoche

# generare file json e salvare

# plot:
# asse x numero di epoche, asse y loss function
import datetime
import json

import matplotlib
import matplotlib.pyplot as plt


class ReportGenerator:

    def generate_report(self, classifier, report_type):
        filename_classifier = classifier.get_filename()
        neurons_per_layer = classifier.get_neurons_per_layer()
        number_of_layers = classifier.get_number_of_layers()
        training_accuracy = classifier.get_training_accuracy()
        validation_accuracy = classifier.get_validation_accuracy()

        print(filename_classifier)

        training_report = {
            "classifierFilename": filename_classifier,
            "numberOfNeuronsPerLayer": neurons_per_layer,
            "numberOfLayers": number_of_layers,
            "trainingAccuracy": training_accuracy,
            "validationAccuracy": validation_accuracy
        }

        if report_type == "testing":
            testing_accuracy = classifier.get_testing_accuracy()
            training_report["testingAccuracy"] = testing_accuracy
        elif report_type == "training":
            self.generate_training_plot(classifier)

        date = datetime.datetime.now()
        filename = "reports/"+report_type+"/"+report_type + "_report " + str(date.year) + "-" + str(date.month) + "-" + str(date.day) + " " + \
                    str(date.hour) + "-" + str(date.minute) + "-" + str(date.second) + ".json"


        with open(filename, 'w') as outfile:
            json.dump(training_report, outfile)

    def generate_training_report_top_five(self, classifier_list):
        report_top_five = {"topFiveClassifiers":[]}
        for classifier in classifier_list:
            training_report = {
                "classifierFilename": classifier.get_filename(),
                "numberOfNeuronsPerLayer": classifier.get_neurons_per_layer(),
                "numberOfLayers": classifier.get_number_of_layers(),
                "trainingAccuracy": classifier.get_training_accuracy(),
                "validationAccuracy": classifier.get_validation_accuracy()
            }
            report_top_five["topFiveClassifiers"].append(training_report)

        date = datetime.datetime.now()
        filename = "reports/top_five/top_five_classifiers_report " + str(date.year) + "-" + str(date.month) + "-" + str(date.day) + " " + \
                   str(date.hour) + "-" + str(date.minute) + "-" + str(date.second) + ".json"

        with open(filename, 'w') as outfile:
            json.dump(report_top_five, outfile)

    def generate_training_plot(self, classifier):
        matplotlib.use("Agg")
        plt.figure(figsize=(5, 2.7), layout='constrained')
        plt.plot(classifier.get_loss_curve(), label='training')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.title('Model loss')
        plt.legend()
        #plt.show()

        date = datetime.datetime.now()
        filename = "plots/training_plot " + str(date.year) + "-" + str(date.month) + "-" + str(date.day) + " " + \
                   str(date.hour) + "-" + str(date.minute) + "-" + str(date.second) + ".png"

        plt.savefig(filename)

