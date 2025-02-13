import json
import os
import requests
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

    def req_chrom(self, quadrant):
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
