LEGEND_ORDER = "xrleghijkyz"


class MsiVariables:
    """" All the ilp variables for an MSI"""

    def __init__(self, msi_data, model, pos=None):
        """ Constructor for the PositionVariable class

        :param msi_data: The data of all MSIs or of a single MSI?
        :param model: The ILP model
        :param pos: optional letter to specify which MSI is used.
        """

        # Use the correct data
        if pos is None:
            self.name = msi_data
        else:
            self.name = msi_data[pos]

        # set all legend variables
        self.x = model.getVarByName(f"x{self.name}")
        self.r = model.getVarByName(f"r{self.name}")
        self.l = model.getVarByName(f"l{self.name}")
        self.e = model.getVarByName(f"e{self.name}")
        self.g = model.getVarByName(f"g{self.name}")
        self.h = model.getVarByName(f"h{self.name}")
        self.i = model.getVarByName(f"i{self.name}")
        self.j = model.getVarByName(f"j{self.name}")
        self.k = model.getVarByName(f"k{self.name}")
        self.y = model.getVarByName(f"y{self.name}")
        self.z = model.getVarByName(f"z{self.name}")
        self.a = model.getVarByName(f"a{self.name}")
        self.b = model.getVarByName(f"b{self.name}")

        self.rhl = 0
        self.rhl_arrow = 0

        self.rhl_open = None
        self.rhl_closing = None
        self.rhl_closed = None
        self.x_rhl = None
        self.r_rhl = None
        self.l_rhl = None
        self.exit_lane = None
        self.carriageway_all_cross = None
        self.carriageway_cross_arrow = None
        self.carriageway_closed_or = None
        self.carriageway_closed = None
        self.aid_trafficstream = None
        self.aid_trafficstream_req = None
        self.aid_row = None
        self.row_all_cross = None

        rsu_str = f"{self.name.split(',')[0]}]"
        if pos == 'c':
            RSU = msi_data['RSU']
            self.is_rhl = False
            if msi_data['RHL']:
                self.is_rhl = True
                self.RHL = msi_data['RHL']
                self.rhl_open = model.getVarByName(f"rhl_open[{self.RHL}]")
                self.rhl_closing = model.getVarByName(f"rhl_closing[{self.RHL}]")
                self.rhl_closed = model.getVarByName(f"rhl_closed[{self.RHL}]")
                self.x_rhl = model.getVarByName(f"x_rhl{self.name}")
                self.r_rhl = model.getVarByName(f"r_rhl{self.name}")
                self.l_rhl = model.getVarByName(f"l_rhl{self.name}")
                self.exit_lane = model.getVarByName(f"exit_lane{self.name}")
                self.rhl = self.x_rhl + self.r_rhl if self.r_rhl else self.x_rhl + self.l_rhl
                self.rhl_arrow = self.r_rhl if self.r_rhl else self.l_rhl

            self.W = msi_data['W_num']
            self.T = msi_data['T_num']

            self.carriageway_all_cross = model.getVarByName(f"carriageway_all_cross[{RSU},{self.W}]")
            self.carriageway_cross_arrow = model.getVarByName(f"carriageway_cross_arrow[{RSU},{self.W}]")
            self.carriageway_closed_or = model.getVarByName(f"carriageway_closed_or[{RSU},{self.W}]")
            self.carriageway_closed = model.getVarByName(f"carriageway_closed[{RSU},{self.W}]")

            self.aid_trafficstream = model.getVarByName(f"aid_trafficstream[{RSU},{self.T}]")
            self.aid_trafficstream_req = model.getVarByName(f"aid_trafficstream_req[{RSU},{self.T}]")
            self.aid_row = model.getVarByName(f"aid_row{rsu_str}")
            self.aid_speed = model.getVarByName(f"aid_speed[{RSU},{self.T}]")
            self.aid_downstream = model.getVarByName(f"aid_downstream[{RSU},{self.T}]")

        self.vvrij = model.getVarByName(f"vvrij{rsu_str}")
        self.cross_row = model.getVarByName(f"cross_in_row{rsu_str}")
        self.vvrij_opa = model.getVarByName(f"vvrij_opa{rsu_str}")
        self.vvrij_or = model.getVarByName(f"vvrij_or{rsu_str}")
        self.row_all_cross = model.getVarByName(f"row_all_cross{rsu_str}")

    def add(self, legends):
        temp_list = []
        last_matched_index = -1

        for legend in legends:
            i = LEGEND_ORDER.index(legend)
            if i <= last_matched_index:
                raise ValueError("Wrong letter order in the add function")
            last_matched_index = i

            temp_list.append(self.__dict__[legend]) if legend in self.__dict__.keys(
            ) else temp_list.append(legend)
        return sum(temp_list)

    def up_to(self, legend):
        if len(legend) != 1 or (legend not in LEGEND_ORDER):
            raise ValueError("Wrong letter in the up_to function")
        i = LEGEND_ORDER.index(legend)
        legend_list = LEGEND_ORDER[:i + 1]
        return self.add(legend_list)


class Molecule:
    """ An MSI and all its neighbors."""

    def __init__(self, road_data, c_name, model):
        """ Constructor for the PositionVariable class.

        :param road_data: The data of all MSIs.
        :type road_data: dict
        :param c_name: The name of the central msi in this molecule.
        :type c_name: str
        :param model: The ILP model
        """
        c_data = road_data[c_name]
        self.c = MsiVariables(c_data, model, "c")
        self.d = get_msi_if_present(road_data, c_data["d"], model)
        self.u = get_msi_if_present(road_data, c_data["u"], model)
        self.l = get_msi_if_present(road_data, c_data["l"], model)
        self.r = get_msi_if_present(road_data, c_data["r"], model)
        self.ds = get_msis_if_present(road_data, c_data["ds"], model)
        self.dt = get_msi_if_present(road_data, c_data["dt"], model)
        self.db = get_msi_if_present(road_data, c_data["db"], model)
        self.dn = get_msi_if_present(road_data, c_data["dn"], model)
        self.us = get_msi_if_present(road_data, c_data["us"], model)
        self.ut = get_msi_if_present(road_data, c_data["ut"], model)
        self.ub = get_msi_if_present(road_data, c_data["ub"], model)
        self.un = get_msi_if_present(road_data, c_data["un"], model)
        self.ll = None
        if self.l:
            l_data = road_data[c_data['l']]
            if l_data['l']:
                self.ll = MsiVariables(l_data, model, "l")
        self.rr = None
        if self.r:
            r_data = road_data[c_data['r']]
            if r_data['r']:
                self.rr = MsiVariables(r_data, model, "r")

        self.continue_v = c_data["C-V"]
        self.continue_x = c_data["C-X"]
        self.dyn_v = c_data['DYN-V']
        self.stat_v = c_data["STAT-V"]

        self.rsu_name = c_data['RSU']
        self.row = [MsiVariables(road_data[msi_name], model, 'c') for msi_name in c_data['row']]
        if len(self.row) != c_data['N_row']:
            raise ValueError("Inconsistent number of MSIs in row")

        self.cw = [MsiVariables(road_data[msi_name], model, 'c') for msi_name in c_data['W']]
        if len(self.cw) != c_data['N_W']:
            raise ValueError("Inconsistent number of MSIs in carriageway")
        self.cw_l = c_data['W_left']
        self.cw_r = c_data['W_right']

        self.ts = [MsiVariables(road_data[msi_name], model, 'c') for msi_name in c_data["T"]]
        if len(self.ts) != c_data['N_T']:
            raise ValueError("Inconsistent number of MSIs in traffic streams")
        self.ts_num = c_data['T_num']

        self.dif_v_left = c_data["DIF-V_left"]
        self.dif_v_right = c_data["DIF-V_right"]

        self.hard_shoulder_left = c_data["Hard_shoulder_left"]
        self.hard_shoulder_right = c_data["Hard_shoulder_right"]

        self.rhl = c_data['RHL']
        self.rhl_neighbor = c_data['RHL_neighbor']
        self.exit_lane = c_data['Exit-Entry']

    def has_composite_relation(self):
        return self.ds or self.dt or self.db or self.dn or self.us or self.ut or self.ub or self.un


def get_msi_if_present(road_data, msi_name, model) -> MsiVariables:
    if msi_name:
        return MsiVariables(road_data[msi_name], model, "c")
    else:
        return None


def get_msis_if_present(road_data, msi_or_list, model):
    if isinstance(msi_or_list, list):
        group = []
        for msi in msi_or_list:
            group.append(MsiVariables(road_data[msi], model, "c"))
    elif msi_or_list:
        return [MsiVariables(road_data[msi_or_list], model, "c")]
    else:
        return None
