import json

DATASETS_FILE = "Data/datasets.json"
ACTIVE_CONFIG_FILE = "/Solution/active_data_set.json"


def read_json_file(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data


def write_json_file(path, data):
    with open(path, "w") as json_file:
        json.dump(data, json_file)

def write_log(path, *args):
    with open(path, "a") as file:
        for i in range(len(args)):
            print(args[i], file=file)
