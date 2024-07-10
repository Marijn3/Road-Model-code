import os
import time

from Library import *
from Library.Constraint_library import *
from Library.Function_library import *


def create_model(model_number):
    start_time = time.time()

    dirname = os.path.dirname(__file__)

    if not os.path.exists(f"{dirname}/Solution"):
        os.makedirs(f"{dirname}/Solution")

    datasets = read_json_file(f"{dirname}/{DATASETS_FILE}")
    filenames = datasets[model_number]

    write_json_file(f"{dirname}/{ACTIVE_CONFIG_FILE}", filenames)

    # path to road layout data
    data_file = f"{dirname}/{filenames['data_file']}"
    ilp_file = f"{dirname}/{filenames['ilp_file']}"
    solve_ilp_file = f"{dirname}/{filenames['solve_ilp_file']}"
    json_file = f"{dirname}/{filenames['json_file']}"
    constraints_list_file = f"{dirname}/{filenames['constraints_list_file']}"

    road_layout = read_json_file(data_file)

    # if the road layout data has to be altered it must be done here.
    start_model_time = time.time()
    # create variables from road layout
    model = initModel(road_layout)

    msi_data = {}
    row_data = {}
    for RSU in road_layout:
        row_data = initRSUData(RSU, row_data, road_layout)
        for MSI in road_layout[RSU]["MSI"]:
            single_msi_data = initMSIData(RSU, MSI, model, road_layout)
            msi_data = createJSON(msi_data, single_msi_data)
    ts_data = initTSData(msi_data)

    addConstraints(msi_data, row_data, ts_data, model)

    end_model_time = time.time()

    model.optimize()
    status = model.status
    if status == gp.GRB.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
        return
    if status == gp.GRB.INFEASIBLE:
        model.computeIIS()
        model.write(f"{dirname}/Solution/IISmodel.ilp")
        return

    end_optim_time = time.time()

    write_json_file(json_file, msi_data)
    write_json_file(constraints_list_file, {})

    # model.write(ilp_file)
    model.write(solve_ilp_file)
    # model.write(debug_ilp_file)
    model.write(f'{dirname}/Solution/output.json')

    end_time = time.time()
    write_log(f"{dirname}/Solution/time_log.txt",
              f"Elapsed time initial model creation: {(end_time - start_time) * 1000:.2f} ms",
              f"Elapsed time creating model: {(end_model_time - start_model_time) * 1000:.2f} ms",
              f"Elapsed time solving model: {(end_optim_time - end_model_time) * 1000:.2f} ms",
              f"Elapsed time writing to files: {(end_time - end_optim_time) * 1000:.2f} ms",
              f"Number of variables: {model.getAttr(gp.GRB.Attr.NumVars)}",
              f"Number of constraints: {model.getAttr(gp.GRB.Attr.NumConstrs)}",
              "---------------------------------------------------------------------")

    if model.status == 2:
        svg, msi_data = postprocess(filenames, model, msi_data)
        update = {"update": True, "data": msi_data, "svg": svg, "constraints_list": {}}
        write_json_file(f'{dirname}/Solution/update.json', update)
        return update
