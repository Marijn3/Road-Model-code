import logging
import requests

HOST = "http://127.0.0.1:5000"

logger = logging.getLogger(__name__)


class ILPSender:
    def __init__(self):
        self.scenarios = None
        self.requests = None
        self.response = {}

    def send_request(self, scenario: dict, request: dict):
        self.scenario = scenario
        self.requests = request

        if not self.test_connection():
            quit(1)

        model = self.get_dataset(self.scenario["dataset"])

        if not self.init_model(model):
            print("Error loading model.")
            quit(1)
        logger.info(f"Aanvraag {scenario['name']} wordt uitgevoerd.")

        self.execute_step(scenario["step"])
        return self.determine_group_names(self.response)

    def translate_jvm_to_mtm(self, name_jvm: str) -> str:
        rsu, wegnummer, rijrichting_or_hecto, km = name_jvm.split("_")
        if rijrichting_or_hecto in ["L", "R"]:
            return f"{wegnummer}{rijrichting_or_hecto}:{km}"
        else:
            return f"{wegnummer}_{rijrichting_or_hecto}:{km}"

    def determine_group_names(self, name_to_legend: dict) -> list:
        group_names = []
        for jvm_name, legend_list in name_to_legend.items():
            mtm_name = self.translate_jvm_to_mtm(jvm_name)
            for msi_nr, legend_name in enumerate(legend_list):
                legend_name = legend_name[0]  # Take out of its list
                if legend_name != "Blank":
                    group_names.append(f"{legend_name}[{mtm_name}:{msi_nr+1}]")
        return group_names

    def test_connection(self, timeout=1.0, verbose=False):
        """
        Simple test to see if the server is active.

        :param: timeout How many seconds to wait for the server to send data before giving up.
        :return: Whether the test succeeded.
        """
        if verbose:
            print("Searching for server at %s" % HOST)
        try:
            self.response = requests.get(HOST + "/", timeout=timeout)
            if self.response.text == "Hello World!":
                if verbose:
                    print("App server is active.")
                return True
        except requests.ConnectionError:
            print("A Connection error occurred.")
            return False
        except requests.Timeout:
            print("The request timed out.")
            return False
        except requests.RequestException:
            print("There was an ambiguous exception.")
            return False
        return False

    def execute_step(self, step, verbose=False):
        self.response = {}
        name = step["name"]
        if step["type"] == "add":
            if verbose:
                print("  Add %s" % name)
            request = self.requests[name]
            self.response = self._request(request)
            if self.response is None:
                quit(1)
        elif step["type"] == "remove":
            if verbose:
                print("  Remove %s" % name)
            self.response = self._request({"type": "remove", "name": name})
            if self.response is None:
                quit(1)
        else:
            raise ValueError("Unknown request type: %s" % step["type"])

    def get_dataset(self, name, verbose=False):
        datasets = self._request({"type": "datasets"})
        if datasets is None:
            print("Failed to obtain datasets")
            return -1

        if verbose:
            print(datasets)

        model = -1
        for (i, dataset) in datasets.items():
            marker = " "
            if dataset == name:
                if verbose:
                    model = int(i)
                else:
                    return int(i)
                marker = "*"
            if verbose:
                print("%s%2i: %s" % (marker, int(i), dataset))
        return model

    def _request(self, json):
        """
        Send a request.

        :param: json The JSON data that is sent with this request.
        :return: The JSON that is received, or None if the request failed
        """
        try:
            self.response = requests.post(HOST + "/request", json=json)
            if not self.response.ok:
                print(self.response.reason)
                return None
            return self.response.json()
        except requests.ConnectionError:
            print("A Connection error occurred.")
            return None
        except requests.Timeout:
            print("The request timed out.")
            return None
        except requests.JSONDecodeError:
            print("There was an error in the JSON data.")
            return None
        except requests.RequestException:
            print("There was an ambiguous exception.")
            return None

    def init_model(self, model_number, verbose=False):
        """
        Initialize the model.

        :param: model_number The ID number of the model.
        :return: Whether the procedure succeeded.
        """
        if verbose:
            print("Initializing model %i." % model_number)
        self.response = self._request({"type": "init", "datasetId": str(model_number)})
        if self.response is None:
            return False
        return True
