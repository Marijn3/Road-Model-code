import os
import time
from datetime import datetime, timezone

import gurobipy as gp

from Library import *
from Library.Constraint_library import addLegendRequest
from Library.Function_library import postprocess


class Request:
    def __init__(self):
        self.name = ""
        self.add = False
        self.remove = False
        self.legend_requests = {}
        self.options = {}


def undict_request(request) -> Request:
    req_obj = Request()
    if request["type"] == "add":
        req_obj.add = True
        req_obj.legend_requests = request["legend_requests"]
        req_obj.options = request["options"]
    elif request["type"] == "remove":
        req_obj.remove = True
    else:
        raise ValueError("Unknown request type: %s" % request["type"])

    req_obj.name = request['name'].replace(' ', '_')
    return req_obj


def main(request):
    start_time = time.time()

    dirname = os.path.dirname(__file__)

    data_set = read_json_file(f"{dirname}/{ACTIVE_CONFIG_FILE}")

    ilp_file = f"{dirname}/{data_set['solve_ilp_file']}"
    json_file = f"{dirname}/{data_set['json_file']}"
    constraints_list_file = f"{dirname}/{data_set['constraints_list_file']}"

    model = gp.read(ilp_file)

    msi_data = read_json_file(json_file)
    constraints_list = read_json_file(constraints_list_file)

    start_add_rem_time = time.time()
    request = undict_request(request)
    if request.add and (request.name in constraints_list):
        write_log(f"{dirname}/Solution/time_log.txt",
                  f"{request.name} was already in the list of constraints",
                  "---------------------------------------------------------------------")
        return {"update": False}

    if request.add and (request.name not in constraints_list):
        constraints_list = addLegendRequest(model, request, msi_data, constraints_list)
        logging_string = f"{request.name} is added"

    if request.remove:
        for i in constraints_list[request.name]:
            if all(word in i for word in ['aid', 'trafficstream']):
                T = i.split('[')[1].split(']')[0]
                aid_var = model.getVarByName(f"aid_trafficstream[{T}]")
                model.addConstr(aid_var == 0, name=f"AID_TS_[{T}]_no_request")
            if all(word in i for word in ['v_vrij']):
                RSU = i.split('[')[1].split(',')[0]
                vvrij_var = model.getVarByName(f"vvrij_opa[{RSU}]")
                if model.getConstrByName(f"VVrij_ROW_[{RSU}]_no_request") is None:
                    model.addConstr(vvrij_var == 0, name=f"VVrij_ROW_[{RSU}]_no_request")
                    model.update()
            if '_o[' in i:
                MSI = i.split('[')[1].split(']')[0]
                o_var = model.getVarByName(f"o[{MSI}]")
                model.addConstr(o_var == 0, name=f"[{MSI}]_blank_overrule_not_requested")
            model.remove(model.getConstrByName(i))
        constraints_list.pop(request.name)
        logging_string = f"{request.name} is removed"

    model.update()

    end_add_rem_time = time.time()

    # Solve model
    model.optimize()
    status = model.status

    if status == gp.GRB.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
        return
    if status == gp.GRB.INFEASIBLE:
        model.computeIIS()
        model.write(f"{dirname}/Solution/IISmodel.ilp")
        return

    # Post processing
    post_time = time.time()

    active_constr = []
    inactive_constr = []
    constrs = model.getConstrs()
    for constr in constrs:
        if constr.Slack < 1e-4:
            active_constr.append({constr.ConstrName: constr.Slack})
        else:
            inactive_constr.append({constr.ConstrName: constr.Slack})

    write_json_file(f"{dirname}/Solution/active_constr.json", {"active": active_constr, "inactive": inactive_constr})

    model.write(f"{dirname}/{data_set['solve_ilp_file']}")

    model.write(f'{dirname}/Solution/output.json')

    write_json_file(constraints_list_file, constraints_list)

    print(json.dumps(create_rsu_based_result(model, msi_data)))

    svg, msi_data = postprocess(data_set, model, msi_data)

    end_time = time.time()

    write_log(f"{dirname}/Solution/time_log.txt",
              f"Elapsed time request handling: {(end_time - start_time) * 1000:.2f} ms",
              f"Elapsed time data selection: {(start_add_rem_time - start_time) * 1000:.2f} ms",
              f"Elapsed time request addition/removal: {(end_add_rem_time - start_add_rem_time) * 1000:.2f} ms",
              f"Elapsed time solver: {model.getAttr(gp.GRB.Attr.Runtime) * 1000:.2f} ms",
              f"Elapsed time post processing: {(end_time - post_time) * 1000:.2f} ms",
              logging_string,
              f"Number of variables: {model.getAttr(gp.GRB.Attr.NumVars)}",
              f"Number of constraints: {model.getAttr(gp.GRB.Attr.NumConstrs)}",
              "---------------------------------------------------------------------")

    write_json_file(constraints_list_file, constraints_list)
    update = {"update": True, "data": msi_data, "svg": svg, "constraints_list": constraints_list}
    write_json_file(f'{dirname}/Solution/update.json', update)
    return update


def request_light(request):
    dirname = os.path.dirname(__file__)
    data_set = read_json_file(f"{dirname}/{ACTIVE_CONFIG_FILE}")
    ilp_file = f"{dirname}/{data_set['solve_ilp_file']}"
    json_file = f"{dirname}/{data_set['json_file']}"
    constraints_list_file = f"{dirname}/{data_set['constraints_list_file']}"

    model = gp.read(ilp_file)

    msi_data = read_json_file(json_file)
    constraints_list = read_json_file(constraints_list_file)

    request = undict_request(request)
    if request.add:
        if request.name in constraints_list:
            raise RuntimeError(f"{request.name} was already in the list of constraints.")
        constraints_list = addLegendRequest(model, request, msi_data, constraints_list)

    if request.remove:
        for i in constraints_list[request.name]:
            if all(word in i for word in ['aid', 'trafficstream']):
                T = i.split('[')[1].split(']')[0]
                aid_var = model.getVarByName(f"aid_trafficstream[{T}]")
                model.addConstr(aid_var == 0, name=f"AID_TS_[{T}]_no_request")
            if all(word in i for word in ['v_vrij']):
                RSU = i.split('[')[1].split(',')[0]
                vvrij_var = model.getVarByName(f"vvrij_opa[{RSU}]")
                if model.getConstrByName(f"VVrij_ROW_[{RSU}]_no_request") is None:
                    model.addConstr(vvrij_var == 0, name=f"VVrij_ROW_[{RSU}]_no_request")
                    model.update()
            model.remove(model.getConstrByName(i))
        constraints_list.pop(request.name)
    write_json_file(constraints_list_file, constraints_list)
    model.update()

    # Solve model
    model.optimize()
    status = model.status

    if status == gp.GRB.UNBOUNDED:
        raise RuntimeError('The model cannot be solved because it is unbounded')
    if status == gp.GRB.INFEASIBLE:
        raise RuntimeError('The model cannot be solved because it is unfeasible')

    model.write(f"{dirname}/{data_set['solve_ilp_file']}")
    out_legends = create_rsu_based_result(model, msi_data)
    return out_legends


def create_rsu_based_result(model, msi_data):
    out_legends = {}
    for (key, value) in msi_data.items():
        msi = int(key[-2]) - 1
        rsu = key[1:-3]
        if rsu not in out_legends:
            n = int(value["N_row"])
            out_legends[rsu] = [''] * n
        out_legends[rsu][msi] = value['State']
    # Fill the results with legend_ids that are active.
    for v in model.getVars():
        varname = v.getAttr('VarName')
        varval = v.getAttr('X')

        # Variable should always be equal to 1 or 0
        if 0.01 < varval < 0.99:
            raise ValueError("Variable has unclear numerical value")

        # Indicator variables should not be taken into account
        if (v.getAttr('X') > 0.5) and (varname[1] == "_" or varname[1] == "["):
            split_varname = varname.split('[')
            legend = split_varname[0][0]
            rsu = split_varname[1][:-3]
            msi = int(split_varname[1][-2]) - 1

            # make sure that RHL variables are used on every MSI of the respective RHL
            if out_legends[rsu][msi][0] == "Blank":
                out_legends[rsu][msi] = [legend]
            else:
                out_legends[rsu][msi].append(legend)
    return out_legends


def get_changes(request):
    dirname = os.path.dirname(__file__)
    if request["time"][-1] != 'Z':
        raise ValueError("Incorrect timezone for timestamp")
    last_update = datetime.strptime(request["time"][:-1],"%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
    last_change = datetime.fromtimestamp(os.path.getmtime(f'{dirname}/Solution/update.json'), datetime.now().astimezone().tzinfo)
    if last_change <= last_update:
        return {"update": False}
    return read_json_file(f'{dirname}/Solution/update.json')
