class SessionValidator:

    def validate_raw_session(self, raw_session, status):
        validator = 0
        port_numbers = 0
        port_scanned = 0
        complete_transaction_number = 0
        for transaction in raw_session["transactions"]:
            if transaction["probe"] is None:
                validator = 1

            if transaction["hostDiscovery"] is None:
                validator = 1
            else:
                port_numbers = len(transaction["hostDiscovery"]["openPorts"])

            if status != "execution" and transaction["securityAnalyst"] is None:
                validator = 1

            if transaction["vulnerabilityScan"] is None:
                validator = 1
            else:
                port_scanned = len(transaction["vulnerabilityScan"]["CVEtoPort"])
                if port_scanned != port_numbers:
                    validator = 1

            if validator == 1:
                raw_session["transactions"].remove(transaction)
            else:
                complete_transaction_number = complete_transaction_number + 1

        return (complete_transaction_number, raw_session)
