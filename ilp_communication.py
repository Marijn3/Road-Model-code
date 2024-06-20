import requests

from Server.Library import read_json_file

HOST = "http://127.0.0.1:5000"
LEGENDS = {"x": "><", "r": "->", "l": "<-", "o": "__",
           "e": "50", "g": "70", "h": "80", "i": "90", "j": "100", "k": "110",
           "y": "\\/", "z": "//", "Blank": "  "}


class ILPSender:
    def __init__(self):
        self.plan = None
        self.data = None

    def send_request(self, plan_filepath: str):
        if not self.test_connection():
            quit(1)
        self.plan = read_json_file(plan_filepath)

        for scenario in self.plan["scenarios"]:
            model = self.get_dataset(scenario["dataset"])

            if not self.init_model(model):
                print("Error loading model.")
                quit(1)
            print("Executing scenario %s:" % scenario["name"])
            self.response = None
            for step in scenario["steps"]:
                self.execute_step(step)

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
        name = step["name"]
        if step["type"] == "add":
            if verbose:
                print("  Add %s" % name)
            request = self.plan["requests"][name]
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
        self.data = self.response["data"]
        self.print_legends()
        return True

    def print_legends(self):
        """
        Print received data in a more user-friendly format.

        :param: data The received data.
        """
        for rsu_name, rsu in self.data.items():
            value = [self.get_legend(msi) for msi in rsu]
            for legend in value:
                if legend != "    ":
                    print(f"{rsu_name} shows [{'|'.join(value)}]")
                    break

    def get_legend(self, state):
        """
        Convert received 'State' into a text-based legend image.

        :param: state The State value of the MSI.
        """
        legend = LEGENDS[state[0]]
        if 'a' in state:
            return "*%s*" % legend
        if 'b' in state:
            return "(%s)" % legend
        return " %s " % legend
