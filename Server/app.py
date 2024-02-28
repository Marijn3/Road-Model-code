import json
import os

from flask import Flask, request
from flask_cors import CORS

from Initial_model_creation import create_model
from Request_handling import main as apply_legend_request, get_changes
from Request_handling import request_light

app = Flask(__name__)
CORS(app)

options_file = f"{os.path.dirname(__file__)}/Data/datasets.json"
data_set = 0


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/request", methods=['GET', 'POST'])
def do_request():
    print(request.data)
    data = request.get_json()
    if data["type"] == "datasets":
        with open(options_file) as json_file:
            datasets = json.load(json_file)
        dataset_list = {}
        for (key, value) in datasets.items():
            dataset_list[key] = value["name"]

        return json.dumps(dataset_list)
    if data["type"] == "init":
        result = create_model(data["datasetId"])
        return result
    result = request_light(data)
    return result


@app.route("/data-sets")
def listDataSets():
    with open(options_file) as json_file:
        jsondata = json.load(json_file)

    dataset_list = [{"id": key, "name": value["name"]}
                    for (key, value) in jsondata.items()]

    return json.dumps(dataset_list)


@app.route("/initModel", methods=['GET', 'POST'])
def initModel():
    if request.method == 'POST':
        data_sets = request.get_json()
        result = create_model(data_sets["datasetId"])
        return result


@app.route("/runModel", methods=['POST'])
def runModel():
    if request.method == 'POST':
        legend_request = json.loads(request.files['files[]'].stream.read())
        result = apply_legend_request(legend_request)
        return result


@app.route("/runNewRequest", methods=['POST'])
def runNewRequest():
    print(request.data)
    if request.method == 'POST':
        legend_request = request.get_json()
        result = apply_legend_request(legend_request)
        return result


@app.route("/removeRequest", methods=['POST'])
def removeRequest():
    if request.method == 'POST':
        legend_request = request.get_json()
        result = apply_legend_request(legend_request)
        return result


@app.route("/getChanges", methods=['POST'])
def getChanges():
    if request.method == 'POST':
        legend_request = request.get_json()
        result = get_changes(legend_request)
        return result


if __name__ == "__main__":
    app.run(host="127.0.0.1", threaded=False, processes=1)
