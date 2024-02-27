from typing import Set
import gurobipy as gp
from Library.svg_library import *
from Library.svg_library import createSVG_A16_A58, createSVG_A50, createSVG_test_RHL, createSVG_Klaverblad_A15_A27, \
    createSVG_Eight_Lane, createSVG_Eight_Lane_2, createSVG_A15_Tunnel, createSVG_Circle, createSVG_Presentatie, \
    createSVG_Demo, createSVG_Demo2


def initModel(road_topology):
    model = gp.Model("Legend pattern calculation")

    temp_list = gp.tuplelist(
        [(RSU, Lane)
         for RSU in road_topology for Lane in road_topology[RSU]["MSI"]]
    )

    #               [x    , r   , l   , o , e , g , h , i, j, k, y, z, a, b]
    restrictivity = [210  , 207 , 206 , 19, 16, 13, 10, 7, 4, 3, 2, 1, 2, 1]
    
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[0] , name="x")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[1] , name="r")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[2] , name="l")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[3] , name="o")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[4] , name="e")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[5] , name="g")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[6] , name="h")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[7] , name="i")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[8] , name="j")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[9] , name="k")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[10], name="y")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[11], name="z")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[12], name="a")
    model.addVars(temp_list, vtype=gp.GRB.BINARY, obj=restrictivity[13], name="b")

    # Rush hour lane variables
    rsu_list = set()
    RHL_section_left = set()
    RHL_section_right = set()
    RHL_MSI_left = []
    RHL_MSI_right = []
    Carriageway_list = []
    Trafficstream_list = []

    for RSU in road_topology: 
        rsu_list.add(RSU)
        W = -1
        T = -1
        for Lane in road_topology[RSU]["MSI"]:
            if W != road_topology[RSU]["MSI"][Lane]['Carriageway']:
                W = road_topology[RSU]["MSI"][Lane]['Carriageway']
                Carriageway_list.append((RSU,W))
            if T != road_topology[RSU]["MSI"][Lane]['TrafficStream']:
                T = road_topology[RSU]["MSI"][Lane]['TrafficStream']
                Trafficstream_list.append((RSU,T))
            RHL = road_topology[RSU]["MSI"][Lane]["Rush_hour_lane"]
            if RHL:
                if int(Lane) == 1:
                    RHL_section_left.add(RHL)
                    RHL_MSI_left.append((RSU,Lane))
                else: 
                    RHL_section_right.add(RHL)
                    RHL_MSI_right.append((RSU,Lane))

    RHL_MSI_left = gp.tuplelist(RHL_MSI_left)
    RHL_MSI_right = gp.tuplelist(RHL_MSI_right)
    Carriageway_list = gp.tuplelist(Carriageway_list)

    if RHL_section_left:
        model.addVars(RHL_section_left, vtype=gp.GRB.BINARY, name="rhl_open")
        model.addVars(RHL_section_left, vtype=gp.GRB.BINARY, name="rhl_closing")
        model.addVars(RHL_section_left, vtype=gp.GRB.BINARY, name="rhl_closed")

        model.addVars(RHL_MSI_left, vtype=gp.GRB.BINARY, obj=restrictivity[0], name="x_rhl")
        model.addVars(RHL_MSI_left, vtype=gp.GRB.BINARY, obj=restrictivity[1], name="r_rhl")
        model.addVars(RHL_MSI_left, vtype=gp.GRB.BINARY, name="exit_lane")

    if RHL_section_right:
        model.addVars(RHL_section_right, vtype=gp.GRB.BINARY, name="rhl_open")
        model.addVars(RHL_section_right, vtype=gp.GRB.BINARY, name="rhl_closing")
        model.addVars(RHL_section_right, vtype=gp.GRB.BINARY, name="rhl_closed")

        model.addVars(RHL_MSI_right, vtype=gp.GRB.BINARY, obj=restrictivity[0], name="x_rhl")
        model.addVars(RHL_MSI_right, vtype=gp.GRB.BINARY, obj=restrictivity[2], name="l_rhl")
        model.addVars(RHL_MSI_right, vtype=gp.GRB.BINARY, name="exit_lane")
    
    if Carriageway_list:
        model.addVars(Carriageway_list, vtype=gp.GRB.BINARY, name="carriageway_all_cross")
        model.addVars(Carriageway_list, vtype=gp.GRB.BINARY, name="carriageway_cross_arrow")
        model.addVars(Carriageway_list, vtype=gp.GRB.BINARY, name="carriageway_closed_or")
        model.addVars(Carriageway_list, vtype=gp.GRB.BINARY, name="carriageway_closed")
    
    # V-Vrij 50 variables
    model.addVars(rsu_list, vtype=gp.GRB.BINARY, name="vvrij_opa")
    model.addVars(rsu_list, vtype=gp.GRB.BINARY, name="cross_in_row")
    model.addVars(rsu_list, vtype=gp.GRB.BINARY, name="row_all_cross")
    model.addVars(rsu_list, vtype=gp.GRB.BINARY, name="vvrij")
    model.addVars(rsu_list, vtype=gp.GRB.BINARY, name="vvrij_or")

    # AID variables
    model.addVars(Trafficstream_list, vtype=gp.GRB.BINARY, name="aid_trafficstream")
    model.addVars(Trafficstream_list, vtype=gp.GRB.BINARY, name="aid_trafficstream_req")
    model.addVars(Trafficstream_list, vtype=gp.GRB.BINARY, name="aid_speed")
    model.addVars(Trafficstream_list, vtype=gp.GRB.BINARY, name="aid_downstream")
    model.addVars(rsu_list, vtype=gp.GRB.BINARY, name="aid_row")
    
    # set model sense to minimize
    model.ModelSense = gp.GRB.MINIMIZE

    # set deterministic method
    model.setParam("Method", gp.GRB.METHOD_DETERMINISTIC_CONCURRENT)

    model.update()
    return model


def initRSUData(RSU, rsu_data, road_layout):
    d_list = set()
    u_list = set()
    for MSI in road_layout[RSU]["MSI"]:
        d = road_layout[RSU]["MSI"][MSI]["Downstream"]["Primary"]
        if d:
            d_list.add(d)
        u = road_layout[RSU]["MSI"][MSI]["Upstream"]["Primary"]
        if u:
            u_list.add(u)

    rsu_data[f"{RSU}"] = {
        "rsu_d": list(d_list),
        "rsu_u": list(u_list),
    }
    return rsu_data


def initTSData(msi_data):
    ts_data = {}

    for msi in msi_data:
        rsu = msi_data[msi]['RSU']
        ts_id = msi_data[msi]['T_num']
        if f"[{rsu},{ts_id}]" not in ts_data.keys():
            c_msi = msi_data[msi]
            d_set = set()
            ds_set = set()
            dt_set = set()
            u_set = set()
            us_set = set()
            ut_set = set()
            for ts_msi in c_msi['T']:
                c_ts_msi = msi_data[ts_msi]
                if c_ts_msi['d']:
                    d_set.add(f"[{msi_data[c_ts_msi['d']]['RSU']},{msi_data[c_ts_msi['d']]['T_num']}]")
                if c_ts_msi['ds']:
                    if isinstance(c_ts_msi['ds'],list):
                        for i in c_ts_msi['ds']:
                            ds_set.add(f"[{msi_data[i]['RSU']},{msi_data[i]['T_num']}]")
                    else:
                        ds_set.add(f"[{msi_data[c_ts_msi['ds']]['RSU']},{msi_data[c_ts_msi['ds']]['T_num']}]")
                if c_ts_msi['dt']:
                    dt_set.add(f"[{msi_data[c_ts_msi['dt']]['RSU']},{msi_data[c_ts_msi['dt']]['T_num']}]")
                if c_ts_msi['u']:
                    u_set.add(f"[{msi_data[c_ts_msi['u']]['RSU']},{msi_data[c_ts_msi['u']]['T_num']}]")
                if c_ts_msi['us']:
                    us_set.add(f"[{msi_data[c_ts_msi['us']]['RSU']},{msi_data[c_ts_msi['us']]['T_num']}]")
                if c_ts_msi['ut']:
                    ut_set.add(f"[{msi_data[c_ts_msi['ut']]['RSU']},{msi_data[c_ts_msi['ut']]['T_num']}]")

            ts_data[f"[{rsu},{ts_id}]"] = {
                "ts_d" : list(d_set),
                "ts_ds" : list(ds_set),
                "ts_dt" : list(dt_set),
                "ts_u" : list(u_set),
                "ts_us" : list(us_set),
                "ts_ut" : list(ut_set)
            }

    return ts_data


def initMSIData(RSU, MSI, model, road_layout):
    # TODO: This initialisation could potentially be done directly using my MSI class, avoiding the .json file?
    d = road_layout[RSU]["MSI"][MSI]["Downstream"]["Primary"]
    ds = road_layout[RSU]["MSI"][MSI]["Downstream"]["Secondary"]
    dt = road_layout[RSU]["MSI"][MSI]["Downstream"]["Taper"]
    db = road_layout[RSU]["MSI"][MSI]["Downstream"]["Broadening"]
    dn = road_layout[RSU]["MSI"][MSI]["Downstream"]["Narrowing"]

    u = road_layout[RSU]["MSI"][MSI]["Upstream"]["Primary"]
    us = road_layout[RSU]["MSI"][MSI]["Upstream"]["Secondary"]
    ut = road_layout[RSU]["MSI"][MSI]["Upstream"]["Taper"]
    ub = road_layout[RSU]["MSI"][MSI]["Upstream"]["Broadening"]
    un = road_layout[RSU]["MSI"][MSI]["Upstream"]["Narrowing"]

    T = []
    T_left = None
    T_right = None
    W = []
    W_left = None
    W_right = None
    l = None
    r = None
    row = []
    RHL_neighbor = None
    for lane in road_layout[RSU]["MSI"]:
        row.append(f"[{RSU},{lane}]")

        T_v = road_layout[RSU]["MSI"][lane]["TrafficStream"]
        T_c = road_layout[RSU]["MSI"][MSI]["TrafficStream"]
        if T_v == T_c:
            T.append(f"[{RSU},{lane}]")
        if (int(lane) == int(MSI) - 1) and (int(T_v) != int(T_c)):
            T_left = f"[{RSU},{lane}]"
        if (int(lane) == int(MSI) + 1) and (int(T_v) != int(T_c)):
            T_right = f"[{RSU},{lane}]"

        W_v = road_layout[RSU]["MSI"][lane]["Carriageway"]
        W_c = road_layout[RSU]["MSI"][MSI]["Carriageway"]
        if (
            road_layout[RSU]["MSI"][lane]["Carriageway"]
            == road_layout[RSU]["MSI"][MSI]["Carriageway"]
        ):
            W.append(f"[{RSU},{lane}]")
        if (int(lane) == int(MSI) - 1) and (int(W_v) != int(W_c)):
            W_left = f"[{RSU},{lane}]"
        if (int(lane) == int(MSI) + 1) and (int(W_v) != int(W_c)):
            W_right = f"[{RSU},{lane}]"

        if int(lane) == int(MSI) + 1:
            r = f"[{RSU},{lane}]"

        if int(lane) == int(MSI) - 1:
            l = f"[{RSU},{lane}]"
        
        last_MSI = len(road_layout[RSU]["MSI"])

        if last_MSI > 2:
            if ((road_layout[RSU]["MSI"]["1"]["Rush_hour_lane"] and lane != "1")
                or (road_layout[RSU]["MSI"][str(last_MSI)]["Rush_hour_lane"] and lane != str(last_MSI))
                or (road_layout[RSU]["MSI"][str(last_MSI-1)]["Rush_hour_lane"] and lane != str(last_MSI-1))):
                RHL_neighbor = True

        N_row = int(lane)

    MSI_nr = int(MSI)
    N_T = len(T)
    N_W = len(W)
    MSI_data = {
        "RSU": f"{RSU}",
        "c": f"[{RSU},{MSI}]",
        "d": f"{d}" if d else d,
        "ds": ds ,
        "dt": f"{dt}" if dt else dt,
        "db": f"{db}" if db else db,
        "dn": f"{dn}" if dn else dn,
        "u": f"{u}" if u else u,
        "us": f"{us}" if us else us,
        "ut": f"{ut}" if ut else ut,
        "ub": f"{ub}" if ub else ub,
        "un": f"{un}" if un else un,
        "r": r,
        "l": l,
        "STAT-V": road_layout[RSU]["Stat-V"],
        "DYN-V": road_layout[RSU]["Dyn-V"],
        "C-X": road_layout[RSU]["Continue-X"],
        "C-V": road_layout[RSU]["Continue-V"],
        "T": T,
        "T_num": road_layout[RSU]["MSI"][MSI]["TrafficStream"],
        "T_right": T_right,
        "T_left": T_left,
        "DIF-V_right": road_layout[RSU]["MSI"][MSI]["TrafficStream_Influence"]["Right"],
        "DIF-V_left": road_layout[RSU]["MSI"][MSI]["TrafficStream_Influence"]["Left"],
        "W": W,
        "W_num": road_layout[RSU]["MSI"][MSI]["Carriageway"],
        "W_right": W_right,
        "W_left": W_left,
        "row": row,
        "RHL": road_layout[RSU]["MSI"][MSI]["Rush_hour_lane"],
        "Exit-Entry": road_layout[RSU]["MSI"][MSI]["Exit-Entry"],
        "RHL_neighbor": RHL_neighbor,
        "Hard_shoulder_right": road_layout[RSU]["hard_shoulder"]["right"],
        "Hard_shoulder_left": road_layout[RSU]["hard_shoulder"]["left"],
        "N_row": N_row,
        "N_T": N_T,
        "N_W": N_W,
        "State": ["Blank"]
    }

    return MSI_data


def createJSON(all_data, MSI_data):

    all_data[MSI_data['c']] = {key: value for key,
                               value in MSI_data.items()}

    return all_data


def postprocess(data_set, model, msi_data):
    # TODO: Dit kan weg, hier kan mijn eigen dataset komen te staan.
    if data_set["name"] == "Knooppunt Galder":
        svg, msi_data = createSVG_A16_A58(model, msi_data)
    elif data_set["name"] == "Apeldoorn Arnhem A50":
        svg, msi_data = createSVG_A50(model, msi_data)
    elif data_set["name"] == "Test rush hour lane":
        svg, msi_data = createSVG_test_RHL(model, msi_data)
    elif data_set["name"] == "XXL":
        svg, msi_data = createSVG_Klaverblad_A15_A27(model, msi_data)
    elif data_set["name"] == "Klaverblad A15 A27":
        svg, msi_data = createSVG_Klaverblad_A15_A27(model, msi_data)
    elif data_set["name"] == "Eight lane road":
        svg, msi_data = createSVG_Eight_Lane(model, msi_data)
    elif data_set["name"] == "Eight lanes, two carriageways":
        svg, msi_data = createSVG_Eight_Lane_2(model, msi_data)
    elif data_set["name"] == "A15 Tunnel":
        svg, msi_data = createSVG_A15_Tunnel(model, msi_data)
    elif data_set["name"] == "Circle":
        svg, msi_data = createSVG_Circle(model, msi_data)
    elif data_set["name"] == "Presentatie":
        svg, msi_data = createSVG_Presentatie(model, msi_data)
    elif data_set["name"] == "Demo":
        svg, msi_data = createSVG_Demo(model, msi_data)
    elif data_set["name"] == "Demo2":
        svg, msi_data = createSVG_Demo2(model, msi_data)
    else:
        raise LookupError("create SVG function not found.")
    return svg, msi_data
