

class Oppervlak:
    def __init__(self, km_start: float, km_end: float, lanes: list) -> None:
        self._km_start = km_start
        self._km_end = km_end
        self._lanes = lanes


class Werkvak(Oppervlak):
    def __init__(self, km_start: float, km_end: float, lanes: list) -> None:
        super().__init__(km_start, km_end, lanes)
        self._color = "cyan"


class Aanvraag(Oppervlak):
    def __init__(self, km_start: float, km_end: float, lanes: list, roadside: str, afzetting: str) -> None:
        super().__init__(km_start, km_end, lanes)
        self._color = "green"


