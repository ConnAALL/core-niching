import json
import os
import requests
import traceback
import csv
import threading
import time
from dotenv import load_dotenv

load_dotenv()

QUEUE_ADDR = os.getenv("QUEUE_ADDR")    

class NetworkInterface:
    def __init__(self):
        self.QUEUE_ADDR = "http://" + QUEUE_ADDR + ":8000/"
        self.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.error_log_path = os.path.join(self.repo_root, 'tracebacks')
        os.makedirs(os.path.dirname(self.error_log_path), exist_ok=True)

    def push_chrom(self, quadrant, chrom_name):
        data = {"quadrant": quadrant, "file_name": chrom_name}
        re = requests.post(self.QUEUE_ADDR + "post", json=data)

        if re.status_code == 200:
            print("Sucessfully pushed to QS")
        else:
            print("Error pushing to QS")


    def req_chrom(self, quadrant): 
        """Get chromosome from a specific quadrant."""
        try:
            re = requests.get(self.QUEUE_ADDR + "req_{}".format(quadrant))
            print(re.text)
            chrom_name = re.json()["chromosome"]

            if chrom_name == -1:
                print("No available chromosome, generating new chromosome")
                return "", ""

            print("Successfully received chromosome name")
            data_path = os.path.join(self.repo_root, 'data', '{}.json'.format(chrom_name))
            
            with open(data_path, 'r') as f:
                lines = f.readlines()
                # Read the lines in reverse order to find the closest valid JSON line
                for line in reversed(lines):
                    line = line.strip()
                    if not line:
                        continue  # skip empty lines
                    try:
                        chromosome_data = json.loads(line)
                        return chromosome_data[1], chrom_name
                    except json.JSONDecodeError:
                        continue

            # If no valid line found, log error
            raise ValueError("No valid JSON line found in file.")
        
        except Exception as e:
            print(f"Failed to request chromosome: {e}")
            self.log_error(traceback.format_exc(), chrom_name)
            return "", ""

    def ping_server(self):
        requests.get(self.QUEUE_ADDR + "is_alive")

    def update_chrom_map(self):
        requests.post(self.QUEUE_ADDR + "update_map",
                      json={"agent_name": self.bot_name, "chrom_file": self.chrom_name})

    def get_mapping(self, bot_name):
        r = requests.get(self.QUEUE_ADDR + "get_map_{}".format(bot_name))
        return r.json()[0]
    
    def log_error(self, error_message, chrom_name):
        """Log errors to a file."""
        with open(os.path.join(self.error_log_path, f'improper_json_format_{chrom_name}'), 'a') as log_file:
            log_file.write(f"{error_message}\n")