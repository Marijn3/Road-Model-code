import gurobipy as gp

from Server.Library.Model_objects import MsiVariables, Molecule, LEGEND_ORDER


def addConstraints(msi_data, row_data, ts_data, model):
    # Loop over all MSIs.
    for c_name in msi_data:
        pos_vars = Molecule(msi_data, c_name, model)
        c = pos_vars.c
        l = pos_vars.l
        r = pos_vars.r
        d = pos_vars.d
        u = pos_vars.u
        ds_list = pos_vars.ds
        dt = pos_vars.dt
        dn = pos_vars.dn
        us = pos_vars.us
        ut = pos_vars.ut
        ub = pos_vars.ub
        rr = pos_vars.rr
        ll = pos_vars.ll

        rsu_name = pos_vars.rsu_name
        continue_v = pos_vars.continue_v
        continue_x = pos_vars.continue_x
        dyn_v = pos_vars.dyn_v
        stat_v = pos_vars.stat_v
        row = pos_vars.row

        cw = pos_vars.cw
        cw_l = pos_vars.cw_l
        cw_r = pos_vars.cw_r

        ts = pos_vars.ts
        ts_num = pos_vars.ts_num
        dif_v_left = pos_vars.dif_v_left
        dif_v_right = pos_vars.dif_v_right
        exit_lane = pos_vars.exit_lane
        rhl = pos_vars.rhl
        rhl_neighbor = pos_vars.rhl_neighbor
        hs_left = pos_vars.hard_shoulder_left
        hs_right = pos_vars.hard_shoulder_right

        show_at_most_one_legend(model, c)
        addSpeedConstraints(model, c, l, r, d, ll, rr, continue_v, stat_v, ts, dif_v_left, dif_v_right)

        # with msi_data for cross arrow lead-in constraints
        # with row_data for v-vrij constraints
        addCrossConstraints(model, msi_data, row_data, c, l, r, d, rsu_name, row, ts, continue_x, hs_left, hs_right)
        addFlasherRedRingConstraints(model, c, d, dyn_v, stat_v, row)

        if ds_list:
            for i, ds in enumerate(ds_list):
                add_downstream_secondary_constraints(model, c, continue_v, ds, i)

        if dt:
            # with msi_data for cross arrow lead-in constraints
            add_dowstream_taper_constraints(model, msi_data, c, l, r, dt, continue_v, continue_x)

        # 19
        if ub:
            broadeningCrossConstraint(model, c, r, ub)
            broadeningCrossConstraint(model, c, l, ub)

        # 18
        if dn:
            narrowingCrossConstraint(model, c, dn)

        # with data for access to downstream CWs
        addIslandConstraints(model, msi_data, c, l, r, d, u, row, cw, cw_l, cw_r)

        # Rush-hour lane constraints:
        no_green_arrow_without_RHL(model, c, rhl_neighbor)
        addRushHourLaneConstraints(model, c, l, r, u, d, dn, row, exit_lane, rhl)

        # AIDConstraints: with ts_data to access downstream TSs
        ts_name = f"[{rsu_name},{ts_num}]"
        ts1_data = ts_data[ts_name]
        model.update()

        # Ensure the aid_request variable exists
        if not model.getConstrByName(f"AID_TS_{ts_name}_no_request"):
            aid_var = model.getVarByName(f"aid_trafficstream_req{ts_name}")
            model.addConstr(aid_var == 0, name=f"AID_TS_{ts_name}_no_request")

        # 38
        add_aid_active_constraints(model, ts1_data, c, ts, row, ts_num)

        # 39
        aid_extend_speed50(model, c, d, "")
        aid_extend_speed50(model, c, dt, "_taper")
        if ds_list:
            for msi_index, ds in enumerate(ds_list):
                aid_extend_speed50(model, c, ds, f"_secondary_{msi_index}")

        # 40
        flasherSpeedRequirements(model, c, u, "upstream")
        flasherSpeedRequirements(model, c, us, "_secondary")
        flasherSpeedRequirements(model, c, ut, "_taper")

        eor_constraints(model, row, c, u, us)

        model.update()


def add_aid_active_constraints(model, ts1_data, c, ts, row, ts_num):
    cvar_speed = []
    for msi in ts:
        cvar_speed.append(msi.e)
        cvar_speed.append(msi.g)

    cvar = []
    current_T = -1
    for msi in row:
        if current_T != msi.T and not msi.is_rhl:
            current_T = msi.T
            cvar.append(msi.aid_trafficstream)
            if current_T == ts_num:
                model.addGenConstrOr(msi.aid_speed, cvar_speed, name=f"{c.name}_aid_speed")
    model.addGenConstrOr(c.aid_row, cvar, name=f"{c.name}_aid_in_row")

    ts_d = ts1_data['ts_d']
    if not ts_d:
        ts_d = []
    ts_ds = ts1_data['ts_ds']
    if not ts_ds:
        ts_ds = []
    ts_dt = ts1_data['ts_dt']
    if not ts_dt:
        ts_dt = []
    aid_active_downstream = []
    for ts_index, downstream_ts in enumerate(ts_d + ts_ds + ts_dt):
        var_aid_speed = model.getVarByName(f"aid_speed{downstream_ts}")
        var_aid_ts = model.getVarByName(f"aid_trafficstream{downstream_ts}")
        aid_active = model.addVar(vtype=gp.GRB.BINARY, name=f"aid_d{ts_index}_ts_{c.name}")
        # ts_aid_speed_TS(theta) ^ ts_aid_TS(theta)
        model.addGenConstrAnd(aid_active, [var_aid_speed, var_aid_ts], name=f"ts_{c.name}_aid_d{ts_index}")
        aid_active_downstream.append(aid_active)

    if aid_active_downstream:
        model.addGenConstrOr(c.aid_downstream, aid_active_downstream, name=f"ts_{c.name}_aid_downstream_any")
        model.addGenConstrOr(c.aid_trafficstream, [c.aid_downstream, c.aid_trafficstream_req],
                             name=f"ts_{c.name}_aid_trafficstream")
    else:
        model.addLConstr(c.aid_trafficstream_req - c.aid_trafficstream == 0,
                         name=f"ts_{c.name}_aid_trafficstream")


def aid_extend_speed50(model, c, d, relation):
    if d:
        model.addConstr((d.aid_trafficstream_req == 1) >> (d.e - c.up_to('e') - c.rhl <= 0),
                        name=f"{c.name}_aid_pattern_lead_in{relation}")


def add_downstream_secondary_constraints(model, c, continue_v, ds, i):
    # 5
    if continue_v:
        continue_v_constraints(model, c, ds, f"_secondary_{i}")
    # 6
    speedLeadInConstraints(model, c, ds, f"_secondary_{i}")
    # 24
    redRingDownstream(model, c, ds, f"_secondary_{i}")
    # new rule
    model.addConstr(ds.add('xrl') - c.up_to('i') <= 0, name=f"{c.name}_new_rule")



def add_dowstream_taper_constraints(model, json_data, c, l, r, dt, continue_v, continue_x):
    # 5
    if continue_v:
        continue_v_constraints(model, c, dt, "_taper")
    # 6
    speedLeadInConstraints(model, c, dt, "_taper")
    # 13
    if continue_x:
        continue_x_constraints(model, c, dt, "_taper")
    # 14-17
    crossArrowLeadInConstraints(model, json_data, c, dt, l, r, "_taper")
    # 24
    redRingDownstream(model, c, dt, "_taper")


def show_at_most_one_legend(model, c):
    # A maximum of one legend may be shown on an MSI at any time.
    model.addConstr(c.add(LEGEND_ORDER) + c.rhl <= 1, f"{c.name}_max_one_legend")


def addSpeedConstraints(model, c, l, r, d, ll, rr, continue_v, stat_v, ts, dif_v_left, dif_v_right):
    # 2
    maxSpeedConstraint(model, stat_v, c, f'{c.name}_stat')
    # 3 - 4
    trafficStreamConstraints(model, c, l, r, ll, rr, ts, dif_v_left, dif_v_right)
    if d:
        # 5
        if continue_v:
            continue_v_constraints(model, c, d, "")
        # 6
        speedLeadInConstraints(model, c, d, "")


def addCrossConstraints(model, json_data, row_data, c, l, r, d, rsu_name, row, ts, continue_x, hs_left, hs_right):
    # 7 - 8
    vVrijConstraints(model, row_data, c, l, r, ts, row, rsu_name)
    # 10 - 12
    arrowConstraints(model, c, l, r, hs_left, hs_right)
    # 13
    if continue_x:
        continue_x_constraints(model, c, d, "")
    # 14-17
    crossArrowLeadInConstraints(model, json_data, c, d, l, r, "")


def addFlasherRedRingConstraints(model, c, d, dyn_v, stat_v, row):
    # 20
    model.addConstr(c.add('rl') - c.a <= 0, f"{c.name}_flashers_on_arrow")
    # 21
    model.addConstr(c.b - c.add('eghij') <= 0, f"{c.name}_red_ring_only_on_speed")
    if d:
        # 22
        redRingSpeedRequirements(model, c, dyn_v, stat_v)
        # 23
        if len(row) > 1:
            redRingRowConstraints(model, row, c)
        # 24
        redRingDownstream(model, c, d)


def arrowConstraints(model, c, l, r, hs_left, hs_right):
    if l:
        # 11
        model.addConstr(c.l + c.rhl_arrow + l.add("xrl") <= 1, f"{c.name}_no_left_arrow_to_cross_or_arrow")
        # 10
        model.addConstr(l.add('rl') - c.up_to('i') - c.rhl <= 0, f"{c.name}_90_next_to_arrow_left")
    else:
        # 12
        if hs_left is None:
            model.addConstr(c.l == 0, name=f"{c.name}_no_left_arrow_away_from_road")

    if r:
        # 11
        model.addConstr(c.r + c.rhl_arrow + r.add("xrl") <= 1, f"{c.name}_no_right_arrow_to_cross_or_arrow")
        # 10
        model.addConstr(r.add('rl') - c.up_to('i') - c.rhl <= 0, f"{c.name}_90_next_to_arrow_right")
    else:
        # 12
        if hs_right is None:
            model.addConstr(c.r == 0, name=f"{c.name}_no_right_arrow_away_from_road")


def maxSpeedConstraint(model, max_speed, c, name):
    # nr 2a
    if max_speed == 50:
        model.addConstr(
            c.add("xrle") + c.rhl == 1,
            f"{name}_max_speed_50"
        )
    # nr 2b
    if max_speed == 70:
        model.addConstr(
            c.add("xrleg") + c.rhl == 1,
            f"{name}_max_speed_70"
        )
    # nr 2c
    if max_speed == 80:
        model.addConstr(
            c.add("xrlegh") + c.rhl == 1,
            f"{name}_max_speed_80"
        )
    # nr 2d
    if max_speed == 90:
        model.addConstr(
            c.add("jk") == 0,
            f"{name}_max_speed_90"
        )


def trafficStreamConstraints(model, c, l, r, ll, rr, ts, dif_v_left, dif_v_right):
    # nr 3
    if len(ts) > 1:
        add_one_speed_in_ts_constraint(model, ts, c)

    # nr 4
    if dif_v_left == 0:
        add_dif_v_0_constraints(model, c, l, ll, "left")
    elif dif_v_left == 20:
        add_dif_v_20_constraints(model, c, l, ll, "left")
    elif dif_v_left == 40:
        add_dif_v_40_constraints(model, c, l, "left")

    # nr 4
    if dif_v_right == 0:
        add_dif_v_0_constraints(model, c, r, rr, "right")
    elif dif_v_right == 20:
        add_dif_v_20_constraints(model, c, r, rr, "right")
    elif dif_v_right == 40:
        add_dif_v_40_constraints(model, c, r, "right")

    # nr 9
    if dif_v_left is not None:
        if r:
            model.addConstr((c.vvrij == 1) >> (l.x + c.add('rl') - 2 * r.up_to('e') <= 1),
                            f"{c.name}_DIF-V_left_XRL_VVRIJ")
            model.addConstr(l.x + c.add('rl') - 2 * r.up_to('g') <= 1, f"{c.name}_DIF-V_left_XRL")

    # nr 9
    if dif_v_right is not None:
        if l:
            model.addConstr((c.vvrij == 1) >> (r.x + c.add('rl') - 2 * l.up_to('e') <= 1),
                            f"{c.name}_DIF-V_right_XRL_VVRIJ")
            model.addConstr(r.x + c.add('rl') - 2 * l.up_to('g') <= 1, f"{c.name}_DIF-V_right_XRL")


def add_one_speed_in_ts_constraint(model, ts, c):
    prefix = f"{c.name}_traffic_stream_speed"
    # Show at most one speed in a traffic stream.
    n = len(ts)
    model.addConstr(sum(msi.e for msi in ts) - n * c.add('xrle') - n * c.rhl <= 0, f"{prefix}_50")
    model.addConstr(sum(msi.g for msi in ts) - n * c.add('xrlg') - n * c.rhl <= 0, f"{prefix}_70")
    model.addConstr(sum(msi.h for msi in ts) - n * c.add('xrlh') - n * c.rhl <= 0, f"{prefix}_80")
    model.addConstr(sum(msi.i for msi in ts) - n * c.add('xrli') - n * c.rhl <= 0, f"{prefix}_90")
    model.addConstr(sum(msi.j for msi in ts) - n * c.add('xrlj') - n * c.rhl <= 0, f"{prefix}_100")
    model.addConstr(sum(msi.k for msi in ts) - n * c.add('xrlk') - n * c.rhl <= 0, f"{prefix}_above_100")


def add_dif_v_0_constraints(model, c, side, far, side_name):
    prefix = f"{c.name}_DIF-V_{side_name}_D0"
    # Increase speed legends on neighboring MSI if there is a Dif-V relation between MSIs.
    model.addConstr(side.e - c.up_to('e') <= 0, f"{prefix}_50")
    model.addConstr(side.g - c.up_to('g') <= 0, f"{prefix}_70")
    model.addConstr(side.h - c.up_to('h') <= 0, f"{prefix}_80")
    model.addConstr(side.i - c.up_to('i') <= 0, f"{prefix}_90")
    model.addConstr(side.j - c.up_to('j') <= 0, f"{prefix}_100")

    # nr 9
    if far:
        model.addConstr(far.x + side.add('rl') - 2 * c.up_to('i') <= 1, f"{prefix}_XRL_1")
        model.addConstr((c.vvrij == 1) >> (far.x + side.add('rl') - 2 * c.up_to('e') <= 1), f"{prefix}_XRL_VVRIJ_1")


def add_dif_v_20_constraints(model, c, side, far, side_name):
    prefix = f"{c.name}_DIF-V_{side_name}_D20"
    # Increase speed legends on neighboring MSI if there is a Dif-V relation between MSIs.
    model.addConstr(side.e - c.up_to('g') <= 0, f"{prefix}_50")
    model.addConstr(side.g - c.up_to('i') <= 0, f"{prefix}_70")
    model.addConstr(side.h - c.up_to('i') <= 0, f"{prefix}_80")
    model.addConstr(side.i - c.up_to('k') <= 0, f"{prefix}_90")
    model.addConstr(side.j - c.up_to('k') <= 0, f"{prefix}_100")

    # nr 9
    if far:
        model.addConstr((c.vvrij == 1) >> (far.x + side.add('rl') - 2 * c.up_to('i') <= 1), f"{prefix}_XRL_VVRIJ_1")


def add_dif_v_40_constraints(model, c, side, side_name):
    prefix = f"{c.name}_DIF-V_{side_name}_D40"
    # Increase speed legends on neighboring MSI if there is a Dif-V relation between MSIs.
    model.addConstr(side.e - c.up_to('i') <= 0, f"{prefix}_50")
    model.addConstr(side.g - c.up_to('i') <= 0, f"{prefix}_70")
    model.addConstr(side.h - c.up_to('i') <= 0, f"{prefix}_80")
    model.addConstr(side.i - c.up_to('k') <= 0, f"{prefix}_90")
    model.addConstr(side.j - c.up_to('k') <= 0, f"{prefix}_100")


def continue_v_constraints(model, c, d, relation):
    prefix = f"{c.name}_continue-V_{relation}"
    # Maintain speed legends upstream if there is a Continue-V relation between RSUs.
    model.addConstr(d.e - c.up_to('e') <= 0, f"{prefix}_50")
    model.addConstr(d.g - c.up_to('g') <= 0, f"{prefix}_70")
    model.addConstr(d.h - c.up_to('h') <= 0, f"{prefix}_80")
    model.addConstr(d.i - c.up_to('i') <= 0, f"{prefix}_90")
    model.addConstr(d.j - c.up_to('j') <= 0, f"{prefix}_100")


def continue_x_constraints(model, c, d, relation):
    # Cross legends must be propagated upstream if there is a Continue-X relation between RSU’s.
    model.addConstr(d.x - c.x <= 0, f"{c.name}_continue-X{relation}")
    # No arrow may be placed if the RSU has a continue-X relation.
    model.addConstr(c.add("rl") == 0, f"{c.name}_continue-X{relation}_no_arrow")


def crossArrowLeadInConstraints(model, json_data, c, d, l, r, relation):
    if d:
        # A cross legend must be preceded by a cross or a directional arrow legend.
        model.addConstr(d.x - c.add("xrl") <= 0, f"{c.name}_cross_or_arrow_before_cross{relation}")
        # A directional arrow legend must always be preceded by a speed of 90 or a more restrictive legend.
        model.addConstr(d.add("rl") - c.up_to("i") <= 0, f"{c.name}_90_before_directional_arrow{relation}")

        # 17
        x_list = []
        for msi in json_data[d.name]["row"]:
            msi_vars = MsiVariables(json_data[msi], model, 'c')
            x_list.append(msi_vars.x)
            if msi_vars.x_rhl:
                x_list.append(msi_vars.x_rhl)

        n_row = json_data[d.name]['N_row']
        if not r:
            model.addConstr(n_row * c.r - sum(x_list) <= 0, name=f"{c.name}_keep_traffic_on_road_right{relation}")
        if not l:
            model.addConstr(n_row * c.l - sum(x_list) <= 0, name=f"{c.name}_keep_traffic_on_road_left{relation}")


def speedLeadInConstraints(model, c, d, relation):
    # nr 6
    model.addConstr(d.e - c.add('xrleg') <= 0,
                    f"{c.name}_speed_lead_in_50{relation}")
    model.addConstr((c.aid_trafficstream == 0) >> (d.g - c.add('xrleghi') <= 0),
                    f"{c.name}_speed_lead_in_70{relation}")


def vVrijConstraints(model, row_data, c, l, r, ts, row, rsu_name):
    model.update()

    if r:
        model.addConstr(r.x - c.up_to('g') - c.rhl <= 0, f"{c.name}_70_next_to_cross_right")
    if l:
        model.addConstr(l.x - c.up_to('g') - c.rhl <= 0, f"{c.name}_70_next_to_cross_left")

    n_ts = len(ts)
    model.addConstr(sum(msi.x for msi in ts) - n_ts * c.up_to('g') - n_ts * c.rhl <= 0,
                    f"{c.name}_traffic_stream_vvrij_70")

    if not model.getConstrByName(f"VVrij_ROW_[{rsu_name}]_no_request"):
        vvrij_var = model.getVarByName(f"vvrij_opa[{rsu_name}]")
        model.addConstr(vvrij_var == 0, name=f"VVrij_ROW_[{rsu_name}]_no_request")

    # V-Vrij 50
    if len(row) > 1:
        cross_list = [msi.x for msi in row]

        model.addGenConstrOr(c.cross_row, cross_list, f"{c.name}_X_in_row")

        downstream_rsus = row_data[rsu_name]['rsu_d']
        if downstream_rsus:
            d_vvrij = [model.getVarByName(f"vvrij[{rsu}]") for rsu in downstream_rsus]
            d_vvrij.append(c.vvrij_opa)
            model.addGenConstrOr(c.vvrij_or, d_vvrij, f"{c.name}_v_vrij_or")
            model.addGenConstrAnd(c.vvrij, [c.vvrij_or, c.cross_row], f"{c.name}_v_vrij")
        else:
            model.addGenConstrAnd(c.vvrij, [c.vvrij_opa, c.cross_row], f"{c.name}_v_vrij")

        if r:
            model.addConstr((c.vvrij == 1) >> (r.x - c.add('xrle') - c.rhl <= 0), f"{c.name}_50_next_to_cross_right")
        if l:
            model.addConstr((c.vvrij == 1) >> (l.x - c.add('xrle') - c.rhl <= 0), f"{c.name}_50_next_to_cross_left")
        model.addConstr((c.vvrij == 1) >> (sum(msi.x for msi in ts) - n_ts * c.add('xrle') - n_ts * c.rhl <= 0),
                        f"{c.name}_traffic_stream_vvrij_50")


def flasherSpeedRequirements(model, c, u, relation):
    prefix = f"{c.name}_flasher_{relation}"
    if u:
        model.addConstr((c.aid_row == 1) >> (c.add('egh') - u.up_to('h') - c.a <= 0), f"{prefix}_less_restrictive_80")
        model.addConstr((c.aid_row == 1) >> (c.add('eg') - u.up_to('g') - c.a <= 0), f"{prefix}_less_restrictive_70")
        model.addConstr((c.aid_row == 1) >> (c.e - u.up_to('e') - c.a <= 0), f"{prefix}_less_restrictive_50")


def redRingDownstream(model, c, d, relation=None):
    model.addConstr(d.b + c.add('eghij') - c.b <= 1, f"{c.name}_continue_red_ring{relation}")


def redRingSpeedRequirements(model, c, dyn_v, stat_v, kind=None):
    if dyn_v:
        v_max = min(dyn_v, stat_v)
    else:
        v_max = stat_v
        kind = "stat"

    if v_max == 50:
        model.addConstr(c.e - c.b <= 0, f"{kind}_{c.name}_red_ring_on_max-v_50")
    if v_max == 70:
        model.addConstr(c.g - c.b <= 0, f"{kind}_{c.name}_red_ring_on_max-v_70")
    if v_max == 80:
        model.addConstr(c.h - c.b <= 0, f"{kind}_{c.name}_red_ring_on_max-v_80")
    if v_max == 90:
        model.addConstr(c.i - c.b <= 0, f"{kind}_{c.name}_red_ring_on_max-v_90")
    if v_max == 100:
        model.addConstr(c.j - c.b <= 0, f"{kind}_{c.name}_red_ring_on_max-v_100")


def redRingRowConstraints(model, row, c):
    model.addConstr(sum(msi.b for msi in row) - len(row) * (c.add('xrlky') + c.b + c.rhl) <= 0,
                    f"{c.name}_red_ring_across_row")


def broadeningCrossConstraint(model, c, neighbor, ub):
    if neighbor:
        c_var = c.x + c.x_rhl if c.x_rhl else c.x
        model.addConstr(ub.x + neighbor.x - c_var <= 1, f"{c.name}_broadening_cross")


def narrowingCrossConstraint(model, c, dn):
    dn_var = dn.x + dn.x_rhl if dn.x_rhl else dn.x
    model.addConstr(dn_var - c.x <= 0, f"{c.name}_narrowing_cross")


def eor_constraints(model, row, c, u, us):
    # After every legend an end of restrictions legend must be shown, if no other legend is shown.
    if u:
        model.addConstr(u.up_to('y') - c.up_to('z') - c.rhl <= 0, f"{c.name}_EoR_after_legend")
    if us:
        model.addConstr(us.up_to('y') - c.up_to('z') - c.rhl <= 0, f"{c.name}_EoR_after_legend_sec")

    # End of restrictions legends must be shown across the row. No other legends may be shown at any MSI in the row,
    # except for RHL legends.
    if len(row) > 1:
        model.addConstr(sum(msi.z for msi in row) - len(row) * (c.z + c.rhl) <= 0, f"{c.name}_EoR_across_row")


def addRushHourLaneConstraints(model, c, l, r, u, d, dn, row, exit_lane, rhl):

    if rhl:
        if not model.getConstrByName(f"Request_[{rhl}]_closed"):
            rhl_closed = model.getVarByName(f"rhl_closed[{rhl}]")
            model.addConstr(rhl_closed == 1, name=f"Request_[{rhl}]_closed")

        if c.l_rhl:
            sideDependentRHLConstraints(model, c, d, u, dn, l.r, c.l_rhl, exit_lane, True)
        else:
            sideDependentRHLConstraints(model, c, d, u, dn, r.l, c.r_rhl, exit_lane, False)

        # An RHL can either be open, closing or closed.
        model.addConstr(c.rhl_closed + c.rhl_closing + c.rhl_open == 1, f"{c.name}_RHL_state")

        # If the RHL is open or closing, shown green arrows on all non-RHL MSIs.
        for msi in row:
            if msi.name == c.name:
                continue
            model.addConstr(c.rhl_open + c.rhl_closing - msi.up_to('y') <= 0, f"{msi.name}_green_arrow_across_row")


def no_green_arrow_without_RHL(model, c, rhl_neighbor):
    if not rhl_neighbor:
        model.addConstr(c.y == 0, name=f"{c.name}_no_green_arrow_without_RHL")


def sideDependentRHLConstraints(model, c, d, u, dn, arrow_to_rhl, arrow_to_road, exit_lane, spits):
    # 29
    model.addConstr(((c.rhl_closing == 1) >> (arrow_to_road + c.add('xrl') == 1)), f"{c.name}_RHL_closing")
    # 30
    model.addConstr((arrow_to_road + c.x_rhl + arrow_to_rhl <= 1), f"{c.name}_no_arrow_to_arrow_RHL")
    # 31
    model.addConstr((arrow_to_road - c.a <= 0), f"{c.name}_flasher_arrow_RHL")
    # 32
    if dn:
        model.addConstr((c.rhl_open == 1) >> (arrow_to_road + c.add('xrl') == 1),
                        f"{c.name}_RHL_open_arrow_at_narrowing")

    if d:
        # 33
        if d.rhl_closed:
            # 33
            model.addConstr((d.rhl_closed == 1) >> (c.rhl_open - arrow_to_road - c.add('xrl') <= 0),
                            f"{c.name}_downstream_rhl_closed")
            # 34
            model.addConstr((d.rhl_open == 1) >> (c.rhl_open - c.add('xrleghijy') <= 0),
                            f"{c.name}_downstream_rhl_open")
        if d.rhl_open is None:
            # 34
            model.addConstr(c.rhl_open - c.add('xrleghijy') <= 0, f"{c.name}_no_ds_rhl_open")

    if not spits:
        # 35
        model.addConstr((c.rhl_closed == 1) >> (c.x_rhl + c.x == 1), f"{c.name}_rhl_closed_cross")
    else:
        # 36
        if exit_lane:
            model.addConstr(c.exit_lane == 1, f"{c.name}_exit_lane_present")
        else:
            model.addConstr(c.exit_lane == 0, f"{c.name}_exit_lane_absent")
        if u:
            if u.exit_lane:
                model.addConstr((c.rhl_closed == 1) >> (c.exit_lane + u.exit_lane - arrow_to_road - c.x <= 1),
                                f"{c.name}_rhl_closed_arrow")
        model.addConstr((c.rhl_closed == 1) >> (c.exit_lane + c.x_rhl == 1), f"{c.name}_rhl_closed_cross")


def addIslandConstraints(model, json_data, c, l, r, d, u, row, cw, cw_l, cw_r):
    x_list = []
    xrl_list = []

    # 26a start
    for msi in cw:
        x_list.append(msi.x)
        xrl_list.append(msi.x)
        xrl_list.append(msi.r)
        xrl_list.append(msi.l)

    model.addGenConstrAnd(c.carriageway_all_cross, x_list, f"{c.name}_carriageway_all_cross")
    model.addGenConstrOr(c.carriageway_cross_arrow, xrl_list, f"{c.name}_carriageway_cross_arrow")

    if d:
        if json_data[d.name]["N_W"] >= len(cw):
            model.addGenConstrAnd(c.carriageway_closed_or, [d.carriageway_closed, c.carriageway_cross_arrow],
                                  f"{c.name}_carriageway_downstream_closed")
            model.addGenConstrOr(c.carriageway_closed, [c.carriageway_closed_or, c.carriageway_all_cross],
                                 f"{c.name}_carriageway_closed")
        else:
            d_closed = []
            current_W = -1
            for msi_name in json_data[d.name]["row"]:
                if current_W != json_data[msi_name]["W_num"]:
                    current_W = json_data[msi_name]["W_num"]
                    msi = MsiVariables(json_data[msi_name], model, 'c')
                    d_closed.append(msi.carriageway_closed)
            d_closed.append(c.carriageway_cross_arrow)
            model.addGenConstrAnd(c.carriageway_closed_or, d_closed, f"{c.name}_carriageway_downstream_closed")
            model.addGenConstrOr(c.carriageway_closed, [c.carriageway_closed_or, c.carriageway_all_cross],
                                 f"{c.name}_carriageway_closed")
    else:
        model.addLConstr(c.carriageway_all_cross - c.carriageway_closed == 0, name=f"{c.name}_carriageway_closed")

    # 26b
    if cw_l:
        model.addConstr((c.carriageway_closed == 0) >> (c.l == 0), name=f"{c.name}_keep_traffic_in_carriageway_left")
    if cw_r:
        model.addConstr((c.carriageway_closed == 0) >> (c.r == 0), name=f"{c.name}_keep_traffic_in_carriageway_right")

    # 25
    if len(row) > 2:
        if u:
            if l:
                model.addLConstr(c.x - u.l + l.l <= 1, name=f"{c.name}_left_right_arrow_split_left")
            if r:
                model.addLConstr(c.x - u.r + r.r <= 1, name=f"{c.name}_left_right_arrow_split_right")


def addLegendRequest(model, data, json_file, full_constr_list):
    request_name = data.name
    constraints_list = []
    for request in data.legend_requests:
        legend = request[0]
        msi = request[1:]
        add_legend_request_constraint(model, msi, legend, f"{request_name}_{request}")
        constraints_list.append(f"{request_name}_{request}")

    for (opt, value) in data.options.items():
        if opt == "V_Vrij_50":
            add_v_vrij50_constraints(model, request_name, value, constraints_list)
        elif opt == "DYN-V":
            add_dyn_v_constraints(model, request_name, value, constraints_list, json_file)
        elif opt == "RHL":
            add_rush_hour_lane_constraints(model, value, constraints_list, full_constr_list)
        elif opt == "AID":
            add_aid_request_constraints(model, value, constraints_list, json_file)
        else:
            raise ValueError("Unknown option: %s" % opt)

    full_constr_list[request_name] = constraints_list
    return full_constr_list


def add_legend_request_constraint(model, msi, legend, name):
    c = MsiVariables(msi, model)
    if legend == "x":
        constraint = c.x
    elif legend == "r":
        constraint = c.add('xr')
    elif legend == "l":
        constraint = c.add('xrl')
    elif legend == "e":
        constraint = c.add('xrle')
    elif legend == "g":
        constraint = c.add('xrleg')
    elif legend == "h":
        constraint = c.add('xrlegh')
    elif legend == "i":
        constraint = c.add('xrleghi')
    elif legend == "j":
        constraint = c.add('xrleghij')
    elif legend == "y":
        constraint = c.add('xrleghijky')
    elif legend == "z":
        constraint = c.add('xrleghijkyz')
    else:
        raise ValueError("Unknown legend requested.")
    model.addConstr(constraint == 1, name)


def add_v_vrij50_constraints(model, request_name, value, constraints_list):
    for msi in value:
        c = MsiVariables(msi, model)
        rsu = msi.split('[')[1].split(',')[0]
        VVrij_constr = model.getConstrByName(f"VVrij_ROW_[{rsu}]_no_request")
        model.remove(VVrij_constr)
        model.addConstr(c.vvrij_opa == 1, name=f"{request_name}_{msi}_v_vrij")
        constraints_list.append(f"{request_name}_{msi}_v_vrij")


def add_dyn_v_constraints(model, request_name, value, constraints_list, json_file):
    for msi in value["MSI"]:
        json_file[msi]["DYN-V"] = value["max_speed"]
        c = MsiVariables(json_file[msi], model, 'c')
        maxSpeedConstraint(model, value["max_speed"], c, f'{request_name}_{msi}_dyn')
        dyn_v = json_file[msi]["DYN-V"]
        stat_v = json_file[msi]["STAT-V"]
        redRingSpeedRequirements(model, c, dyn_v, stat_v, kind=f'{request_name}_dyn')
        constraints_list.append(f'{request_name}_dyn_{msi}_red_ring_on_max-v_{value["max_speed"]}')
        if value["max_speed"] != 100:
            constraints_list.append(f'{request_name}_{msi}_dyn_max_speed_{value["max_speed"]}')


def add_rush_hour_lane_constraints(model, value, constraints_list, full_constr_list):
    for RHL in value["RHL"]:
        constr1 = model.getConstrByName(f'Request_[{RHL}]_open')
        constr2 = model.getConstrByName(f'Request_[{RHL}]_closing')
        constr3 = model.getConstrByName(f'Request_[{RHL}]_closed')
        removedConstr = False

        if constr1:
            model.remove(constr1)
            removedConstr = True
        if constr2:
            model.remove(constr2)
            removedConstr = True
        if constr3:
            model.remove(constr3)
            removedConstr = True

        if removedConstr:
            keys_to_pop = []
            for myKey, myValue in full_constr_list.items():
                for item in myValue:
                    if f'Request_[{RHL}]' in item:
                        keys_to_pop.append(myKey)
            for item in keys_to_pop:
                full_constr_list.pop(item)
    if value["state"] == "open":
        for RHL in value["RHL"]:
            rhl_open = model.getVarByName(f"rhl_open[{RHL}]")
            model.addConstr(rhl_open == 1, name=f'Request_[{RHL}]_open')
            constraints_list.append(f'Request_[{RHL}]_open')
    if value["state"] == "closed":
        for RHL in value["RHL"]:
            rhl_closed = model.getVarByName(f"rhl_closed[{RHL}]")
            model.addConstr(rhl_closed == 1, name=f'Request_[{RHL}]_closed')
            constraints_list.append(f'Request_[{RHL}]_closed')
    if value["state"] == "closing":
        for RHL in value["RHL"]:
            rhl_closing = model.getVarByName(f"rhl_closing[{RHL}]")
            model.addConstr(rhl_closing == 1, name=f'Request_[{RHL}]_closing')
            constraints_list.append(f'Request_[{RHL}]_closing')


def add_aid_request_constraints(model, value, constraints_list, json_file):
    for T in value["trafficstream"]:
        cvar = model.getVarByName(f"aid_trafficstream_req[{T}]")
        aid_constr = model.getConstrByName(f"AID_TS_[{T}]_no_request")
        model.remove(aid_constr)
        model.addConstr(cvar == 1, name=f'Request_trafficstream[{T}]_aid')
        constraints_list.append(f'Request_trafficstream[{T}]_aid')

        rsu = T.split(',')[0]
        for msi in json_file:
            if json_file[msi]['RSU'] == rsu and T.split(',')[1] == json_file[msi]["T_num"]:
                c = MsiVariables(json_file[msi], model, 'c')

                if value["speed"] == 50:
                    model.addConstr(c.add('xrle') + c.rhl == 1,
                                    name=f'Request_speed_{value["speed"]}{msi}_aid')
                if value["speed"] == 70:
                    model.addConstr(c.add('xrleg') + c.rhl == 1,
                                    name=f'Request_speed_{value["speed"]}{msi}_aid')
                constraints_list.append(f'Request_speed_{value["speed"]}{msi}_aid')
