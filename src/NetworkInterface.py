import json
import os
import requests
import csv
import threading
import time
from dotenv import load_dotenv

load_dotenv()

QUEUE_ADDR = os.getenv("QUEUE_ADDR")    

class NetworkInterface:
    def __init__(self):
        self.QUEUE_ADDR = "http://" + QUEUE_ADDR + ":8000/"

    def push_chrom(self, quadrant, chrom_name):
        data = {"quadrant": quadrant, "file_name": chrom_name}
        re = requests.post(self.QUEUE_ADDR + "post", json=data)

        if re.status_code == 200:
            print("Sucessfully pushed to QS")
        else:
            print("Error pushing to QS")

    def req_chrom(self, quadrant): # Get chromosome from a specific quadrant
        re = requests.get(self.QUEUE_ADDR + "req_{}".format(quadrant))
        print(re.text)
        chrom_name = re.json()["chromosome"]

        if chrom_name == -1:
            print("No available chromosome, generating new chromosome")
            return "", ""

        print("Succesfully recieved chromosome name")
        data_path = os.path.join(self.repo_root, 'data', '{}.json'.format(chrom_name))
        with open(data_path, 'r') as f:
            chromosome_data = json.loads(f.readlines()[-1])

        return chromosome_data[1], chrom_name

    def ping_server(self):
        requests.get(self.QUEUE_ADDR + "is_alive")

    def update_chrom_map(self):
        requests.post(self.QUEUE_ADDR + "update_map",
                      json={"agent_name": self.bot_name, "chrom_file": self.chrom_name})

    def get_mapping(self, bot_name):
        r = requests.get(self.QUEUE_ADDR + "get_map_{}".format(bot_name))
        return r.json()[0]
    
    def fetch_chrom_map(self):
        """Fetch the entire chrom map from the server."""
        r = requests.get(self.QUEUE_ADDR + "get_chrom_map")
        if r.status_code == 200:
            return r.json()
        else:
            print("Error fetching chrom map")
            return None

    def log_chrom_map_to_csv(self, csv_file_path):
        """Log the entire chrom map to a CSV file."""
        chrom_map = self.fetch_chrom_map()
        if chrom_map is not None:
            with open(csv_file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow(["Quadrant", "Chromosome Name", "Chromosome Data"])
                # Write data
                for entry in chrom_map:
                    writer.writerow([entry["quadrant"], entry["chrom_name"], json.dumps(entry["chrom_data"])])
            print(f"Chrom map logged to {csv_file_path}")
        else:
            print("Failed to log chrom map to CSV")

    def start_logging_chrom_map(self, csv_file_path, interval=60):
        """Start logging the chrom map to a CSV file at regular intervals."""
        if self.chrom_map_thread is None:
            self.logging = True
            self.chrom_map_thread = threading.Thread(target=self._log_chrom_map_periodically, args=(csv_file_path, interval))
            self.chrom_map_thread.start()
            print("Started logging chrom map to CSV")
        else:
            print("Chrom map logging is already running")

    def stop_logging_chrom_map(self):
        """Stop logging the chrom map to a CSV file."""
        if self.chrom_map_thread is not None:
            self.logging = False
            self.chrom_map_thread.join()
            self.chrom_map_thread = None
            print("Stopped logging chrom map to CSV")

    def _log_chrom_map_periodically(self, csv_file_path, interval):
        """Log the chrom map to a CSV file at regular intervals."""
        while self.logging:
            self.log_chrom_map_to_csv(csv_file_path)
            time.sleep(interval)