import threading
from ingestion_system.communication_handler import CommunicationHandler
from ingestion_system.communication_handler import ModuleRestParams
from ingestion_system.raw_session_buffer import RawSessionBuffer
from ingestion_system.session_validator import SessionValidator
import sched
import time
import json


class IngestionSystemController:

    # def run(self):
    def __init__(self):
        self.communication_handler = CommunicationHandler(self)

        self.raw_session_buffer = RawSessionBuffer()

        ingestion_configuration_file = open('ingestion_configuration.json')
        ingestion_configuration = json.load(ingestion_configuration_file)
        ingestion_configuration_file.close()

        self.session_duration = ingestion_configuration["sessionTimeDuration"]
        self.minimum_transaction_number = ingestion_configuration["minimumTransactionNumber"]
        self.status = ingestion_configuration["status"]

        self.communication_handler.add_schema(ingestion_configuration["schemaProbe"], "probe")
        self.communication_handler.add_schema(ingestion_configuration["schemaHostDiscovery"], "host_discovery")
        self.communication_handler.add_schema(ingestion_configuration["schemaVulnerabilityScan"], "vulnerability_scan")
        self.communication_handler.add_schema(ingestion_configuration["schemaSecurityAnalyst"], "security_analyst")

        self.monitoring_params = ModuleRestParams(ingestion_configuration["monitoringSystemIP"],
                                                  ingestion_configuration["monitoringSystemPort"],
                                                  ingestion_configuration["monitoringSystemPath"])

        self.preparation_params = ModuleRestParams(ingestion_configuration["preparationSystemIP"],
                                                   ingestion_configuration["preparationSystemPort"],
                                                   ingestion_configuration["preparationSystemPath"])

    def run(self):
        threading.Thread(target=self.communication_handler.run, args=("127.0.0.1", 5001)).start()
        my_scheduler = sched.scheduler(time.time, time.sleep)
        my_scheduler.enter(self.session_duration, 1, self.terminate_session, (my_scheduler, 0))
        my_scheduler.run()

    def terminate_session(self, scheduler, session_id):
        scheduler.enter(self.session_duration, 1, self.terminate_session, (scheduler, session_id + 1))

        # Retrieve session
        session = self.raw_session_buffer.retrieve_session(session_id)

        # Session validator
        print(session)
        session_validator = SessionValidator()
        (correct_transactions_num, raw_session) = session_validator.validate_raw_session(session, self.status)
        print(raw_session)

        if correct_transactions_num >= self.minimum_transaction_number:
            self.communication_handler.send_message_json(session, self.preparation_params)
        else:
            print("Not enough transactions, session discarded: ", correct_transactions_num)

        if self.status == "monitoring":
            label_json = {"session_id": session_id, "label": self.label_session(session)}
            self.communication_handler.send_message_json(label_json, self.monitoring_params_params)

    def handle_json(self, packet, packet_type):
        self.raw_session_buffer.insert_packet(packet, packet_type)

    def label_session(self, session):
        total_anomalous = 0
        for transaction in session["transactions"]:
            if transaction["securityAnalyst"]["securityAnalysis"] == "Anomalous":
                total_anomalous = total_anomalous + 1
        total_transactions = len(session["transactions"])
        if total_anomalous > total_transactions * 0.3:
            return "Anomalous"
        else:
            return "Normal"

    def stop(self):
        pass


if __name__ == '__main__':
    ingestion = IngestionSystemController()
    ingestion.run()
