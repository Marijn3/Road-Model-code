from road_model import *
logger = logging.getLogger(__name__)


class MSIRow:
    def __init__(self, msi_network: 'MSINetwerk', msi_row_info: ObjectInfo):
        self.msi_network = msi_network
        self.info = msi_row_info
        self.properties = self.info.obj_eigs
        self.local_road_info = self.msi_network.wegmodel.get_one_section_at_point(self.info.pos_eigs.geometrie)
        self.local_road_properties = self.local_road_info.obj_eigs
        self.name = make_MTM_row_name(self.info)
        self.lane_numbers = []
        self.n_lanes = 0
        self.n_msis = 0
        self.MSIs = {}
        self.cw = {}
        self.downstream = {}
        self.upstream = {}

    def __repr__(self):
        return self.name

    def fill_row_properties(self):
        # Determine everything there is to know about the road in general
        self.lane_numbers = sorted([lane_nr for lane_nr, lane_type in self.local_road_properties.items()
                                    if isinstance(lane_nr, int) and lane_type not in ["Puntstuk"]])
        self.n_lanes = len(self.lane_numbers)
        self.n_msis = len(self.properties["Rijstrooknummers"])

        # Create all MSIs in row, passing the parent row class as argument
        self.MSIs = {msi_numbering: MSI(self, msi_numbering) for msi_numbering in self.properties["Rijstrooknummers"]}

        # Determine carriageways based on road properties
        self.cw = {}
        cw_index = 1
        lanes_in_current_cw = [1]

        for lane_number in self.lane_numbers:
            # Add final lane and stop
            if lane_number == self.n_lanes:
                last_lane = [self.MSIs[i].name for i in lanes_in_current_cw if i in self.MSIs.keys()]
                if last_lane:
                    self.cw[cw_index] = last_lane
                break

            current_lane = self.local_road_properties[lane_number]
            next_lane = self.local_road_properties[lane_number + 1]
            if current_lane == next_lane:
                lanes_in_current_cw.append(lane_number + 1)
            else:
                self.cw[cw_index] = [self.MSIs[i].name for i in lanes_in_current_cw if i in self.MSIs.keys()]
                lanes_in_current_cw = [lane_number + 1]
                cw_index += 1

    def determine_msi_row_relations(self):
        downstream_rows = self.msi_network.travel_roadmodel(self, True)
        for row in downstream_rows:
            for msi_row, desc in row.items():
                if msi_row is not None:
                    logger.debug(f"Conclusion: {msi_row.name} {desc}")
                    self.downstream[msi_row] = desc

        upstream_rows = self.msi_network.travel_roadmodel(self, False)
        for row in upstream_rows:
            for msi_row, desc in row.items():
                if msi_row is not None:
                    logger.debug(f"Conclusion: {msi_row.name} {desc}")
                    self.upstream[msi_row] = desc

    def fill_msi_properties(self):
        for msi in self.MSIs.values():
            msi.determine_properties()
            msi.determine_relations()
        # Separate loop to ensure all normal relations are in place before this is called.
        for msi in self.MSIs.values():
            msi.ensure_upstream_relation()


class MSINetwerk:
    def __init__(self, wegmodel: WegModel, maximale_zoekafstand: int = 1500, alle_secundaire_relaties: bool = True):
        """
        Instantiates an MSI network based on the provided road model and settings.
            wegmodel (WegModel): The road model on which the lane signalling relations will be based.
            maximale_zoekafstand (int): Max search distance in meters. Guidelines say there should be
                at most 1200 m between MSI rows. In terms of geometry lengths, this can sometimes be exceeded.
            alle_secundaire_relaties (bool): Indication whether all additionally determined
                secundary relation types, which are not in the guidelines, should be added.
        """
        self.wegmodel = wegmodel
        self.add_secondary_relations = alle_secundaire_relaties
        self.max_search_distance = maximale_zoekafstand

        self.MSIrows = []
        self.construct_msi_network()

    def construct_msi_network(self):
        logger.info(f"MSI-netwerk opzetten...")

        self.MSIrows = [MSIRow(self, msi_info) for msi_info in self.wegmodel.get_points_info("MSI")]

        for msi_row in self.MSIrows:
            msi_row.fill_row_properties()

        # These can only be called once all msi_rows are initialised.
        for msi_row in self.MSIrows:
            msi_row.determine_msi_row_relations()
            msi_row.fill_msi_properties()

        self.log_network()

    def log_network(self):
        # Log resulting properties once everything has been determined
        for msi_row in self.MSIrows:
            for msi in msi_row.MSIs.values():
                filtered_properties = {key: value for key, value in msi.properties.items() if value is not None}
                logger.debug(f"{msi.name} heeft de volgende eigenschappen:\n{filtered_properties}")

    def travel_roadmodel(self, msi_row: 'MSIRow', downstream: bool) -> list:
        """
        Initiates travel through the road model in upstream or downstream direction,
        starting from the indicated MSI row, and finds MSI rows in specified direction.
        Args:
            msi_row (MSIRow): MSIRow class object which is the starting point of the search.
            downstream: Boolean to indicate search direction. False for upstream search.
        Returns:
            List containing the first MSI rows encountered in the specified direction.
            Every MSI also has a shift and annotation value, depending on what was encountered
            during the travel towards that MSI row from the start MSI row.
        """
        starting_section_id = self.__get_travel_starting_section_id(msi_row, downstream)
        current_km = msi_row.info.pos_eigs.km
        travel_direction = msi_row.local_road_info.pos_eigs.rijrichting

        logger.debug(f"Starting recursive search for {starting_section_id}, {current_km}, {downstream}, {travel_direction}")
        msis = self.find_msi_recursive(starting_section_id, current_km, downstream, travel_direction)

        if isinstance(msis, dict):
            return [msis]
        return msis

    def __get_travel_starting_section_id(self, msi_row: MSIRow, downstream: bool) -> int:
        """
        Obtain section ID of section under MSI row. In case there are multiple sections,
        the upstream/downstream section will be taken as the starting section, depending
        on the indicated direction.
        Args:
            msi_row (MSIRow): MSI row instance to find section ID for.
            downstream (bool): Boolean to indicate search direction. False for upstream search.
        Returns:
            Section ID of starting section, considering the MSI row and the
            downstream/upstream search direction.
        """
        start_sections = self.wegmodel.get_sections_by_point(msi_row.info.pos_eigs.geometrie)

        if len(start_sections) == 0:  # Nothing found
            raise Exception(f"Geen secties gevonden voor deze MSI locatie: {msi_row.info.pos_eigs}.")

        if len(start_sections) == 1:  # Obtain first (and only) ID in dict.
            return next(iter(start_sections.keys()))

        logger.warning(f"Meer dan één sectie gevonden op MSI locatie. Keuze op basis van zoekrichting.")
        if ((downstream and msi_row.local_road_info.pos_eigs.rijrichting == "L")
                or (not downstream and msi_row.local_road_info.pos_eigs.rijrichting == "R")):
            km_registration_to_equate = 1
        else:
            km_registration_to_equate = 0

        for section_id, section in start_sections.items():
            if section.pos_eigs.km[km_registration_to_equate] == msi_row.info.pos_eigs.km:
                return section_id

    def find_msi_recursive(self, current_section_id: int, current_km: float, downstream: bool, travel_direction: str,
                           shift: int = 0, current_distance: float = 0, annotation: dict = None) -> list | dict:
        """
        This is recursive function, meaning that it calls itself. The function requires
        variables to keep track of where a branch of the recursive search is. These have
        to be specified, forming the starting point of the recursive search. The function
        also logs the shift, distance and annotation of that branch. The latter do not
        have to be specfied when calling the function.
        Args:
            current_section_id (int): ID of section in current iteration.
            current_km (float): Latest km registration encountered.
            downstream (bool): Value representing the search direction.
            travel_direction (str): Travel direction of traffic on the road ("L" or "R").
            shift (int): Amount of lanes shifted from the leftmost lane of the
                original road section so far.
            current_distance (float): Distance travelled through model so far. This is
                used to cut off search after passing a threshold.
            annotation (dict): Annotation so far.
        Returns:
            (List of) dictionaries, structured as: {MSIRow object: (shift, annotation)}.
            In case only one MSI row is found, the dictionary is returned directly.
            In case multiple are found, their dictionaries are placed in a list. This
            should be handled outside the function.
        """
        if current_section_id is None:
            return {None: (shift, annotation)}

        current_section = self.wegmodel.sections[current_section_id]

        first_iteration = False
        if annotation is None:
            first_iteration = True
            current_distance -= current_section.pos_eigs.geometrie.length
            annotation = {}

        other_points_on_section, msis_on_section = (
            self.evaluate_section_points(current_section_id, current_km, travel_direction, downstream, first_iteration))

        # Base case 1: Single MSI row found.
        if len(msis_on_section) == 1:
            logger.debug(f"MSI row gevonden op {current_section_id}: {msis_on_section[0].pos_eigs.km}")
            shift, annotation = self.update_shift_annotation(shift, annotation, current_section.verw_eigs,
                                                             downstream, first_iteration, True)
            return {self.get_msi_row_by_pos(msis_on_section[0].pos_eigs): (shift, annotation)}

        # Base case 2: Multiple MSI rows found.
        if len(msis_on_section) > 1:
            nearest_msi = min(msis_on_section, key=lambda msi: abs(current_km - msi.pos_eigs.km))
            logger.debug(f"Meerdere MSIs gevonden bij {current_section_id}. Dichtstbijzijnde: {nearest_msi.pos_eigs.km}")
            shift, annotation = self.update_shift_annotation(shift, annotation, current_section.verw_eigs,
                                                             downstream, first_iteration, True)
            return {self.get_msi_row_by_pos(nearest_msi.pos_eigs): (shift, annotation)}

        # Base case 3: Maximum depth reached.
        current_distance += current_section.pos_eigs.geometrie.length
        logger.debug(f"Zoekdiepte: {current_distance}")
        if current_distance >= self.max_search_distance:
            logger.debug(f"De maximale zoekdiepte is overschreden: {current_distance}")
            return {None: (shift, annotation)}

        # Recursive case 1: No other points on the section.
        if not other_points_on_section:
            logger.debug(f"No other points on {current_section_id}.")
            if downstream:
                connecting_section_ids = [sid for sid in (current_section.verw_eigs.sectie_stroomafwaarts,
                                                          current_section.verw_eigs.sectie_afbuigend_stroomafwaarts)
                                          if sid is not None]

            else:
                connecting_section_ids = [sid for sid in (current_section.verw_eigs.sectie_stroomopwaarts,
                                                          current_section.verw_eigs.sectie_afbuigend_stroomopwaarts)
                                          if sid is not None]

            if not connecting_section_ids:
                # There are no further sections connected to the current one. Return empty-handed.
                logger.debug(f"No connections at all with {current_section_id}")
                return {None: (shift, annotation)}
            elif len(connecting_section_ids) > 1:
                # This happens in the case of intersections. These are of no interest for MSI relations.
                logger.debug(f"It seems that more than one section is connected to {current_section_id}:"
                            f"{connecting_section_ids}. Stopping.")
                return {None: (shift, annotation)}
            else:
                # Find an MSI row in the next section.
                next_section_id = connecting_section_ids[0]
                logger.debug(f"Looking for MSI row in the next section, {next_section_id}")
                shift, annotation = self.update_shift_annotation(shift, annotation, current_section.verw_eigs,
                                                                 downstream, first_iteration)
                return self.find_msi_recursive(connecting_section_ids[0], current_km, downstream, travel_direction,
                                               shift, current_distance, annotation)

        assert len(other_points_on_section) == 1 or len(other_points_on_section) == 2, \
            f"Onverwacht aantal punten op lijn: {[point for point in other_points_on_section]}"

        # Recursive case 2: *vergence point on the section.
        if len(other_points_on_section) == 1:
            other_point = other_points_on_section[0]
        if len(other_points_on_section) == 2:
            if (downstream and current_section.pos_eigs.rijrichting == "R" or
                    not downstream and current_section.pos_eigs.rijrichting == "L"):
                other_point = [point for point in other_points_on_section if point.pos_eigs.km > current_km][0]
            if (downstream and current_section.pos_eigs.rijrichting == "L" or
                    not downstream and current_section.pos_eigs.rijrichting == "R"):
                other_point = [point for point in other_points_on_section if point.pos_eigs.km < current_km][0]

        downstream_split = downstream and other_point.obj_eigs["Type"] in ["Splitsing", "Uitvoeging"]
        upstream_split = not downstream and other_point.obj_eigs["Type"] in ["Samenvoeging", "Invoeging"]

        if not (downstream_split or upstream_split):
            # The recursive function can be called once, for the (only) section that is in the travel direction.
            next_section_id = other_point.verw_eigs.uitgaande_secties[0] if downstream \
                else other_point.verw_eigs.ingaande_secties[0]
            if "Puntstuk" not in current_section.obj_eigs.values():  # TODO: remove this assumption.
                # This is the diverging section. Determine annotation.
                if downstream:
                    puntstuk_section_id = list(set(other_point.verw_eigs.ingaande_secties) - {current_section_id})[0]
                else:
                    puntstuk_section_id = list(set(other_point.verw_eigs.uitgaande_secties) - {current_section_id})[0]
                n_lanes_other, _ = get_n_lanes(self.wegmodel.sections[puntstuk_section_id].obj_eigs)
                shift = shift + n_lanes_other

            shift, annotation = self.update_shift_annotation(shift, annotation, current_section.verw_eigs,
                                                             downstream, first_iteration)

            logger.debug(f"The *vergence point leads to section {next_section_id}")
            logger.debug(f"Marking {next_section_id} with +{shift}")

            return self.find_msi_recursive(next_section_id, other_point.pos_eigs.km, downstream, travel_direction,
                                           shift, current_distance, annotation)

        if upstream_split:
            cont_section_id = current_section.verw_eigs.sectie_stroomopwaarts
            div_section_id = current_section.verw_eigs.sectie_afbuigend_stroomopwaarts
            logger.debug(f"The *vergence point is an upstream split into {cont_section_id} and {div_section_id}")
        else:
            cont_section_id = current_section.verw_eigs.sectie_stroomafwaarts
            div_section_id = current_section.verw_eigs.sectie_afbuigend_stroomafwaarts
            logger.debug(f"The *vergence point is a downstream split into {cont_section_id} and {div_section_id}")

        _, shift_div = get_n_lanes(self.wegmodel.sections[cont_section_id].obj_eigs)

        # Store negative value in this direction.
        logger.debug(f"Marking {div_section_id} with -{shift_div}")

        shift, annotation = self.update_shift_annotation(shift, annotation, current_section.verw_eigs,
                                                         downstream, first_iteration)

        # Make it do the recursive function twice. Then return both options as a list.
        option_continuation = self.find_msi_recursive(cont_section_id, other_point.pos_eigs.km,
                                                      downstream, travel_direction,
                                                      shift, current_distance, annotation)
        option_diversion = self.find_msi_recursive(div_section_id, other_point.pos_eigs.km,
                                                   downstream, travel_direction,
                                                   shift - shift_div, current_distance, annotation)
        if isinstance(option_continuation, list):
            return option_continuation + [option_diversion]
        elif isinstance(option_diversion, list):
            return option_diversion + [option_continuation]
        else:
            return [option_continuation, option_diversion]

    def evaluate_section_points(self, current_section_id: int, current_km: float,
                                travel_direction: str, downstream: bool, first_iteration: bool) -> tuple[list, list]:
        # Only takes points that are upstream/downstream of current point.
        if (travel_direction == "L" and downstream) or (travel_direction == "R" and not downstream):
            if first_iteration:
                other_points_on_section = [point_info for point_info in self.wegmodel.get_points_info() if
                                           current_section_id in point_info.verw_eigs.sectie_ids
                                           and point_info.pos_eigs.km < current_km]
            else:
                other_points_on_section = [point_info for point_info in self.wegmodel.get_points_info() if
                                           current_section_id in point_info.verw_eigs.sectie_ids
                                           and point_info.pos_eigs.km != current_km]
        else:
            if first_iteration:
                other_points_on_section = [point_info for point_info in self.wegmodel.get_points_info() if
                                           current_section_id in point_info.verw_eigs.sectie_ids
                                           and point_info.pos_eigs.km > current_km]
            else:
                other_points_on_section = [point_info for point_info in self.wegmodel.get_points_info() if
                                           current_section_id in point_info.verw_eigs.sectie_ids
                                           and point_info.pos_eigs.km != current_km]

        # Further filters for MSIs specifically
        msis_on_section = [point for point in other_points_on_section if
                           point.obj_eigs["Type"] == "Signalering"]

        return other_points_on_section, msis_on_section

    def update_shift_annotation(self, shift: int, annotation: dict,
                                current_section_verw_eigs: LijnVerwerkingsEigenschappen, downstream: bool,
                                is_first_iteration: bool = False, is_last_iteration: bool = False) -> tuple[int, dict]:
        """
        Adapts the shift and annotation value according to the previous shift and annotation
        and the processing properties of the provided section.
        Args:
            shift (int): Shift so far.
            annotation (dict): Annotation so far.
            current_section_verw_eigs (LijnVerwerkingsEigenschappen): Processing properties of the section.
            downstream (bool): Indication of search direction. True => Downstream, False => Upstream .
            is_first_iteration (bool): Indicate if it is first iteration, in which case the start processing
                values of the provided section will be ignored.
            is_last_iteration (bool): Indicate if it is last iteration, in which case the end processing
                values of the provided section will be ignored.
        Returns:
            Adjusted shift and annotation.
        """
        new_annotation = self.get_annotation(current_section_verw_eigs, is_first_iteration, is_last_iteration)

        if not new_annotation:
            return shift, annotation

        if (downstream and "ExtraRijstrook" in new_annotation.values()
                or not downstream and "Rijstrookbeeindiging" in new_annotation.values()):
            shift = shift + 1
        elif (downstream and "Rijstrookbeëindiging" in new_annotation.values()
                or not downstream and "ExtraRijstrook" in new_annotation.values()):
            shift = shift - 1

        # Join dicts while preventing aliasing issues.
        return shift, dict(list(annotation.items()) + list(new_annotation.items()))

    @staticmethod
    def get_annotation(section_verw_eigs: LijnVerwerkingsEigenschappen,
                       start_skip: bool = False, end_skip: bool = False) -> dict:
        """
        Determines the annotation to be added to the current recursive
        search based on processing properties of the current section.
        Args:
            section_verw_eigs (LijnVerwerkingsEigenschappen): Processing properties of section
            start_skip (bool): Indicate whether the start values of the section should be considered.
            end_skip (bool): Indicate whether the end values of the section should be considered.
        Returns:
            Dict indicating the lane number and the annotation - the type of special case encountered.
        """
        annotation = {}

        if not start_skip:
            if "Uitrijstrook" in section_verw_eigs.start_kenmerk.values():
                annotation.update({lane_nr: lane_type for lane_nr, lane_type in
                                   section_verw_eigs.start_kenmerk.items() if lane_type == "Uitrijstrook"})

            if "Samenvoeging" in section_verw_eigs.start_kenmerk.values():
                annotation.update({lane_nr: lane_type for lane_nr, lane_type in
                                   section_verw_eigs.start_kenmerk.items() if lane_type == "Samenvoeging"})

            if "Weefstrook" in section_verw_eigs.start_kenmerk.values():
                annotation.update({lane_nr: lane_type for lane_nr, lane_type in
                                   section_verw_eigs.start_kenmerk.items() if lane_type == "Weefstrook"})

        if not end_skip:
            if "Invoegstrook" in section_verw_eigs.einde_kenmerk.values():
                annotation.update({lane_nr: lane_type for lane_nr, lane_type in
                                   section_verw_eigs.einde_kenmerk.items() if lane_type == "Invoegstrook"})

            if "Special" in section_verw_eigs.einde_kenmerk.keys():
                annotation.update({value[1]: value[0] for keyword, value in
                                   section_verw_eigs.einde_kenmerk.items() if keyword == "Special"})

        return annotation

    def get_msi_row_by_pos(self, pos_eigs: PositieEigenschappen) -> MSIRow | None:
        """
        Find the MSI row in self.MSIrows with the provided km registration and hectoletter.
        Args:
            pos_eigs (str): Point hectoletter registration to compare to.
        Returns:
            MSIRow object as specified.
        """
        for msi_row in self.MSIrows:
            if msi_row.info.pos_eigs == pos_eigs:
                return msi_row
        return None


class MSI:
    def __init__(self, parent_msi_row: MSIRow, lane_nr: int):
        self.row = parent_msi_row

        # Store all that is unique to the MSI
        self.lane_nr = lane_nr

        self.name = f"{self.row.name}:{str(self.lane_nr)}"

        self.properties = {
            "c": None,  # Current MSI (center)
            "r": None,  # MSI right
            "l": None,  # MSI left
            "d": None,  # MSI downstream
            "ds": None,  # MSI downstream secondary
            "dt": None,  # MSI downstream taper
            "db": None,  # MSI downstream broadening (extra rijstrook)
            "dn": None,  # MSI downstream narrowing (rijstrookbeëindiging)
            "u": None,  # MSI upstream
            "us": None,  # MSI upstream secondary
            "ut": None,  # MSI upstream taper
            "ub": None,  # MSI upstream broadening (extra rijstrook)
            "un": None,  # MSI upstream narrowing (rijstrookbeëindiging)

            "STAT_V": None,  # Static maximum speed
            "DYN_V": None,  # Static maximum speed
            "C_V": None,  # True if continue-V relation
            "C_X": None,  # True if continue-X relation

            "N_row": None,  # [~] Number of MSIs in row.
            "N_TS": None,  # Number of MSIs in traffic stream.
            "N_CW": None,  # Number of MSIs in carriageway.

            "CW": None,  # All MSIs in CW.
            "CW_num": None,  # CW numbering.
            "CW_right": None,  # All MSIs in CW to the right.
            "CW_left": None,  # All MSIs in CW to the left.

            "TS": None,  # All MSIs in TS.
            "TS_num": None,  # TS numbering.
            "TS_right": None,  # All MSIs in TS to the right.
            "TS_left": None,  # All MSIs in TS to the left.

            "DIF_V_right": None,  # DIF-V influence from the right
            "DIF_V_left": None,  # DIF-V influence from the left

            "row": None,  # All MSIs in row.

            "RHL": None,  # [V] True if MSI in RHL. (Any lane that is open sometimes)
            "Exit_Entry": None,  # True if MSI in RHL and normal lanes left and right.
            "RHL_neighbor": None,  # [V] True if RHL in row.

            "Hard_shoulder_right": None,  # [V] True if hard shoulder directly to the right.
            "Hard_shoulder_left": None,  # [V] True if hard shoulder directly to the left.
        }

    def determine_properties(self):
        if "Maximumsnelheid" in self.row.local_road_properties.keys():
            self.properties["STAT_V"] = self.row.local_road_properties["Maximumsnelheid"]

        # Add DYN_V if it is applied and it is smaller than STAT_V
        dyn_v1, dyn_v2 = None, None
        if "Maximumsnelheid_Open_Spitsstrook" in self.row.local_road_properties.keys():
            dyn_v1 = self.row.local_road_properties["Maximumsnelheid_Open_Spitsstrook"]
        if "Maximumsnelheid_Beperkt_Overdag" in self.row.local_road_properties.keys():
            dyn_v2 = self.row.local_road_properties["Maximumsnelheid_Beperkt_Overdag"]
        if dyn_v1 and dyn_v2:
            self.properties["DYN_V"] = min(dyn_v1, dyn_v2)
        elif dyn_v1:
            self.properties["DYN_V"] = dyn_v1
        elif dyn_v2:
            self.properties["DYN_V"] = dyn_v2

        # TODO: Determine when C_V and C_X are true, based on road properties.
        #  This is implemented as a continue-V relation with the upstream RSUs.
        #  This can be found through WEGGEG/kunstinweg 'viaduct', 'tunnel', 'brug' registrations.
        self.properties["C_X"] = False
        self.properties["C_V"] = False

        self.properties["N_row"] = self.row.n_msis

        cw_number = None
        at_border_left = False
        at_border_right = False

        for index, msi_names in self.row.cw.items():
            if self.name in msi_names:
                cw_number = index
                at_border_left = self.name == msi_names[0]
                at_border_right = self.name == msi_names[-1]
                break

        assert cw_number, f"Er is iets misgegaan met het bepalen van het cw_nummer voor {self.name}"

        self.properties["N_CW"] = len(self.row.cw[cw_number])
        self.properties["N_TS"] = self.properties["N_CW"]

        self.properties["CW"] = self.row.cw[cw_number]
        self.properties["CW_num"] = cw_number
        self.properties["CW_right"] = self.row.cw[cw_number + 1] if cw_number + 1 in self.row.cw.keys() else None
        self.properties["CW_left"] = self.row.cw[cw_number - 1] if cw_number - 1 in self.row.cw.keys() else None

        # Assumption: traffic stream == carriageway
        self.properties["TS"] = self.properties["CW"]
        self.properties["TS_num"] = self.properties["CW_num"]
        self.properties["TS_right"] = self.properties["CW_right"]
        self.properties["TS_left"] = self.properties["CW_left"]

        # Safest assumption: 0 for both directions.
        # Influence levels are only filled in when the MSI borders a different traffic stream.
        self.properties["DIF_V_right"] = 0 if at_border_right and cw_number + 1 in self.row.cw.keys() else None
        self.properties["DIF_V_left"] = 0 if at_border_left and cw_number - 1 in self.row.cw.keys() else None

        self.properties["row"] = [msi.name for msi in self.row.MSIs.values()]

        if (self.lane_nr in self.row.local_road_properties.keys()
                and self.row.local_road_properties[self.lane_nr] in ["Spitsstrook", "Plusstrook"]):
            self.properties["RHL"] = True  # TODO: Replace with RHL section name! See report Jeroen 2 p67.

        if (self.lane_nr in self.row.local_road_properties.keys() and
                self.row.local_road_properties[self.lane_nr] in ["Spitsstrook", "Plusstrook"] and
                self.row.n_lanes > self.lane_nr > 1):
            self.properties["Exit_Entry"] = True

        if ("Spitsstrook" in self.row.local_road_properties.values() or
                "Plusstrook" in self.row.local_road_properties.values()):
            self.properties["RHL_neighbor"] = True

        if self.lane_nr < self.row.n_lanes and self.row.local_road_properties[self.lane_nr + 1] == "Vluchtstrook":
            self.properties["Hard_shoulder_right"] = True
        if self.lane_nr > 1 and self.row.local_road_properties[self.lane_nr - 1] == "Vluchtstrook":
            self.properties["Hard_shoulder_left"] = True

    def determine_relations(self):
        # Center and neighbors
        self.properties["c"] = self.name
        if self.lane_nr + 1 in self.row.MSIs.keys():
            self.properties["r"] = self.row.MSIs[self.lane_nr + 1].name
        if self.lane_nr - 1 in self.row.MSIs.keys():
            self.properties["l"] = self.row.MSIs[self.lane_nr - 1].name

        # Downstream relations
        for d_row, desc in self.row.downstream.items():
            shift, annotation = desc
            this_lane_projected = self.lane_nr + shift

            # Basic primary
            if this_lane_projected in d_row.MSIs.keys():
                self.properties["d"] = d_row.MSIs[this_lane_projected].name
                d_row.MSIs[this_lane_projected].properties["u"] = self.name

            if annotation:
                lane_numbers = list(annotation.keys())
                lane_types = list(annotation.values())

                # Broadening
                if (self.lane_nr in lane_numbers and annotation[self.lane_nr] == "ExtraRijstrook"
                        and this_lane_projected - 1 in d_row.MSIs.keys()):
                    logger.debug(f"Extra case with {self.lane_nr}")
                    self.properties["db"] = d_row.MSIs[this_lane_projected - 1].name
                    d_row.MSIs[this_lane_projected - 1].properties["ub"] = self.name
                # Narrowing
                if (self.lane_nr in lane_numbers and annotation[self.lane_nr] == "Rijstrookbeëindiging"
                        and this_lane_projected + 1 in d_row.MSIs.keys()):
                    logger.debug(f"Eindiging case with {self.lane_nr}")
                    self.properties["dn"] = d_row.MSIs[this_lane_projected + 1].name
                    d_row.MSIs[this_lane_projected + 1].properties["un"] = self.name

                # Secondary
                if (self.lane_nr in lane_numbers and annotation[self.lane_nr] == "Invoegstrook"
                        and this_lane_projected - 1 in d_row.MSIs.keys()):
                    logger.debug(f"Invoegstrook case with {self.lane_nr}")
                    self.make_secondary_connection(d_row.MSIs[this_lane_projected - 1], self)

                if (self.lane_nr + 1 in lane_numbers and annotation[self.lane_nr + 1] == "Uitrijstrook"
                        and this_lane_projected + 1 in d_row.MSIs.keys()):
                    logger.debug(f"Uitrijstrook case with {self.lane_nr}")
                    self.make_secondary_connection(d_row.MSIs[this_lane_projected + 1], self)

                # MSIs that encounter a samenvoeging or weefstrook downstream could have a cross relation.
                if ("Samenvoeging" in lane_types or "Weefstrook" in lane_types) and True:
                    # Relation from weefstrook/join lane to normal lane
                    if (this_lane_projected in lane_numbers
                            and annotation[this_lane_projected] in ["Samenvoeging", "Weefstrook"]):
                        if (this_lane_projected - 1 in d_row.local_road_properties.keys() and
                                d_row.local_road_properties[this_lane_projected - 1] != annotation[this_lane_projected]):
                            if this_lane_projected - 1 in d_row.MSIs.keys():
                                logger.debug(f"Cross case 1 with {self.lane_nr}")
                                self.make_secondary_connection(d_row.MSIs[this_lane_projected - 1], self)
                    # Relation from normal lane to weefstrook/join lane
                    if (this_lane_projected + 1 in lane_numbers
                            and annotation[this_lane_projected + 1] in ["Samenvoeging", "Weefstrook"]):
                        if (this_lane_projected + 1 in d_row.local_road_properties.keys() and
                                d_row.local_road_properties[this_lane_projected] != annotation[this_lane_projected + 1]):
                            if this_lane_projected + 1 in d_row.MSIs.keys():
                                logger.debug(f"Cross case 2 with {self.lane_nr}")
                                self.make_secondary_connection(d_row.MSIs[this_lane_projected + 1], self)

        # Remaining upstream primary relations
        if not self.properties["u"]:
            for u_row, desc in self.row.upstream.items():
                shift, _ = desc  # Why is annotation not used here??
                this_lane_projected = self.lane_nr + shift
                if this_lane_projected in u_row.MSIs.keys():
                    self.properties["u"] = u_row.MSIs[this_lane_projected].name

    def ensure_upstream_relation(self):
        # MSIs that do not have any upstream relation, get a secondary relation
        if (self.row.upstream and not (self.properties["u"] or self.properties["us"]
                                       or self.properties["ub"] or self.properties["un"] or self.properties["ut"])):
            logger.debug(f"{self.name} kan een bovenstroomse secundaire relatie gebruiken: {self.properties}")

            if self.row.msi_network.add_secondary_relations:
                u_row, desc = next(iter(self.row.upstream.items()))
                if u_row.local_road_info.pos_eigs.hectoletter == self.row.local_road_info.pos_eigs.hectoletter:
                    highest_msi_number = max([msi_nr for msi_nr in u_row.MSIs.keys()])
                    logger.debug(f"Relatie wordt toegepast.")
                    self.make_secondary_connection(self, u_row.MSIs[highest_msi_number])
                elif (u_row.local_road_info.pos_eigs.hectoletter != self.row.local_road_info.pos_eigs.hectoletter
                      and self.lane_nr == 1):
                    # This should not occur in the Netherlands, but is here for safety.
                    logger.warning(f"Relatie wordt toegepast (onverwachte situatie).")
                    lowest_msi_number = min([msi_nr for msi_nr in u_row.MSIs.keys()])
                    self.make_secondary_connection(self, u_row.MSIs[lowest_msi_number])
                else:
                    logger.warning(f"{self.name} heeft alsnog geen bovenstroomse relatie, "
                                   f"omdat dit geval nog niet ingeprogrammeerd is.")

    @staticmethod
    def make_secondary_connection(row1, row2):
        """
        First entry is the row that should have an upstream secondary relation to the second entry.
        """
        row1.properties["us"] = row2.name
        if not row2.properties["ds"]:
            row2.properties["ds"] = []
        if row1.name not in row2.properties["ds"]:
            row2.properties["ds"].append(row1.name)


def make_MTM_row_name(point_info: ObjectInfo) -> str:
    if point_info.pos_eigs.hectoletter:
        return f"{point_info.pos_eigs.wegnummer}_{point_info.pos_eigs.hectoletter.upper()}:{point_info.pos_eigs.km}"
    else:
        return f"{point_info.pos_eigs.wegnummer}{point_info.pos_eigs.rijrichting}:{point_info.pos_eigs.km}"
