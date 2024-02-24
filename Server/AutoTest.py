import requests

from Library import read_json_file

HOST = "http://127.0.0.1:5000"
LEGENDS = {"x": "><", "r": "->", "l": "<-", "o": "__",
           "e": "50", "g": "70", "h": "80", "i": "90", "j": "100", "k": "110",
           "y": "\\/", "z": "//", "Blank": "  "}


def test_connection(timeout=1.0, verbose=False):
    """
    Simple test to see if the server is active.

    :param: timeout How many seconds to wait for the server to send data before giving up.
    :return: Whether the test succeeded.
    """
    if verbose:
        print("Searching for server at %s" % HOST)
    try:
        response = requests.get(HOST + "/", timeout=timeout)
        if response.text == "Hello World!":
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


def _request(json):
    """
    Send a request.

    :param: json The JSON data that is sent with this request.
    :return: The JSON that is received, or None if the request failed
    """
    try:
        response = requests.post(HOST + "/request", json=json)
        if not response.ok:
            print(response.reason)
            return None
        return response.json()
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


def init_model(model_number, verbose=False):
    """
    Initialize the model.

    :param: model_number The ID number of the model.
    :return: Whether the procedure succeeded.
    """
    if verbose:
        print("Initializing model %i." % model_number)
    response = _request({"type": "init", "datasetId": str(model_number)})
    if response is None:
        return False
    data = response["data"]
    return True


def print_legends(data):
    """
    Print received data in a more user-friendly format.

    :param: data The received data.
    """
    RSUs = {}
    for rsu_name, rsu in data.items():
        value = [get_legend(msi) for msi in rsu]
        for legend in value:
            if legend != "    ":
                print(f"{rsu_name} shows [{'|'.join(value)}]")
                break


def get_legend(state):
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


def get_dataset(name, verbose=False):
    datasets = _request({"type": "datasets"})
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


def execute_step(step, verbose=False):
    name = step["name"]
    if step["type"] == "add":
        if verbose:
            print("  Add %s" % name)
        request = plan["requests"][name]
        response = _request(request)
        if response is None:
            quit(1)
    elif step["type"] == "remove":
        if verbose:
            print("  Remove %s" % name)
        response = _request({"type": "remove", "name": name})
        if response is None:
            quit(1)
    else:
        raise ValueError("Unknown request type: %s" % step["type"])
    return response


def compare_results(expected_result, real_result, verbose=True):
    equal = True
    for (row, value) in expected_result.items():
        if row not in real_result:
            if verbose:
                print("  Missing row %s in result" % row)
            equal = False
        if real_result[row] != value:
            if verbose:
                print("  Wrong result for row %s!" % row)
                legends = [get_legend(msi) for msi in value]
                print(f"  Expected: [{'|'.join(legends)}]")
                legends = [get_legend(msi) for msi in real_result[row]]
                print(f"  Received: [{'|'.join(legends)}]")
            equal = False
    if len(expected_result) != len(real_result):
        if verbose:
            print("  Superfluous row(s) in result!")
        equal = False
    if equal and verbose:
        print("  Results are equal.")
    return equal


if __name__ == "__main__":
    if not test_connection():
        quit(1)
    plan = read_json_file("automatic_validation.json")

    for scenario in plan["scenarios"]:
        model = get_dataset(scenario["dataset"])
        if not init_model(model):
            print("Error loading model.")
            quit(1)
        print("Executing scenario %s:" % scenario["name"])
        response = None
        for step in scenario["steps"]:
            response = execute_step(step)
        compare_results(scenario["result"], response)

