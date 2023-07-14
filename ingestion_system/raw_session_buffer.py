import sqlite3
import json
from datetime import datetime


class RawSessionBuffer:

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        connection = sqlite3.connect('rawSessions.db')
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Transactions('
                       'timestamp INTEGER NOT NULL, '
                       'sourceIP TEXT NOT NULL, '
                       'probe TEXT, '
                       'vulnerabilityScan TEXT, '
                       'hostDiscovery TEXT, '
                       'securityAnalyst TEXT, '
                       'PRIMARY KEY(timestamp, sourceIP)'
                       ')')
        connection.close()

    def insert_packet(self, packet, packet_type):

        timestamp = packet["timestamp"]
        source_IP = packet["sourceIP"]

        # datetime_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        # timestamp = datetime_object.timestamp()

        connection = sqlite3.connect('rawSessions.db')
        cursor = connection.cursor()

        values = None
        query = None

        if packet_type == "probe":
            skip = ["timestamp", "sourceIP"]
            probe = json.dumps({key: val for key, val in packet.items() if key not in skip})
            values = (timestamp, source_IP, probe, timestamp, source_IP, timestamp, source_IP, timestamp, source_IP)
            query = 'REPLACE INTO Transactions (timestamp, sourceIP, probe, vulnerabilityScan, ' \
                    'hostDiscovery, securityAnalyst) ' \
                    'VALUES (?, ?, ?,' \
                    '(SELECT vulnerabilityScan FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '(SELECT hostDiscovery FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '(SELECT securityAnalyst FROM Transactions WHERE timestamp = ? AND sourceIP = ?))'

        elif packet_type == "vulnerability_scan":
            select_old_vulnerability_scan = 'SELECT * FROM Transactions ' \
                                            'WHERE timestamp = ? AND sourceIP = ?'
            values_select = (timestamp, source_IP)
            cursor.execute(select_old_vulnerability_scan, values_select)
            row = cursor.fetchone()

            port_to_add = packet["port"]
            CVE_to_add = packet["CVE"]

            if row is not None and row[3] is not None:
                vulnerability_scan = json.loads(str(row[3]))
            else:
                vulnerability_scan = packet
                new_field = {"CVEtoPort": []}
                vulnerability_scan.update(new_field)
                del vulnerability_scan["port"]
                del vulnerability_scan["CVE"]

            new_json = {"CVE" : CVE_to_add, "port": port_to_add}
            vulnerability_scan["CVEtoPort"].append(new_json)

            skip = ["timestamp", "sourceIP"]
            vulnerability_scan = json.dumps({key: val for key, val in vulnerability_scan.items() if key not in skip})
            values = (timestamp, source_IP, timestamp, source_IP, vulnerability_scan, timestamp, source_IP,
                      timestamp, source_IP)
            query = 'REPLACE INTO Transactions (timestamp, sourceIP, probe, vulnerabilityScan, ' \
                    'hostDiscovery, securityAnalyst) ' \
                    'VALUES (?, ?,' \
                    '(SELECT probe FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '?,' \
                    '(SELECT hostDiscovery FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '(SELECT securityAnalyst FROM Transactions WHERE timestamp = ? AND sourceIP = ?))'

        elif packet_type == "host_discovery":
            skip = ["timestamp", "sourceIP"]
            host_discovery = json.dumps({key: val for key, val in packet.items() if key not in skip})
            values = (timestamp, source_IP, timestamp, source_IP, timestamp, source_IP, host_discovery, timestamp,
                      source_IP)
            query = 'REPLACE INTO Transactions (timestamp, sourceIP, probe, vulnerabilityScan, ' \
                    'hostDiscovery, securityAnalyst) ' \
                    'VALUES (?, ?,' \
                    '(SELECT probe FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '(SELECT vulnerabilityScan FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '?,' \
                    '(SELECT securityAnalyst FROM Transactions WHERE timestamp = ? AND sourceIP = ?))'

        elif packet_type == "security_analyst":
            skip = ["timestamp", "sourceIP"]
            security_analyst = json.dumps({key: val for key, val in packet.items() if key not in skip})
            # values = (timestamp, source_IP, security_analyst)
            # query = 'REPLACE INTO Transactions (timestamp, sourceIP, securityAnalyst) VALUES (?, ?, ?)'
            values = (timestamp, source_IP, timestamp, source_IP, timestamp, source_IP, timestamp,
                      source_IP, security_analyst)
            query = 'REPLACE INTO Transactions (timestamp, sourceIP, probe, vulnerabilityScan, ' \
                    'hostDiscovery, securityAnalyst) ' \
                    'VALUES (?, ?,' \
                    '(SELECT probe FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '(SELECT vulnerabilityScan FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '(SELECT hostDiscovery FROM Transactions WHERE timestamp = ? AND sourceIP = ?),' \
                    '?)'

        if query is not None and values is not None:
            cursor.execute(query, values)
            connection.commit()

        connection.close()

    def retrieve_session(self, session_id):
        connection = sqlite3.connect('rawSessions.db')
        cursor = connection.cursor()
        query = "SELECT * FROM Transactions"
        cursor.execute(query)
        rows = cursor.fetchall()

        session_dict = {"session_id": session_id, "transactions": []}

        for row in rows:
            string_fields = []
            for i in range(2, 6):
                if row[i] is not None:
                    string_fields.append(json.loads(str(row[i])))
                else:
                    string_fields.append(None)
            transaction_dict = {"timestamp": row[0],
                                "sourceIP": row[1],
                                "probe": string_fields[0],
                                "vulnerabilityScan": string_fields[1],
                                "hostDiscovery": string_fields[2],
                                "securityAnalyst": string_fields[3]}
            session_dict["transactions"].append(transaction_dict)

        cursor.execute("DELETE FROM Transactions")
        connection.commit()
        connection.close()

        return session_dict
