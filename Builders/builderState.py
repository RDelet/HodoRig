class BuilderState(object):

    kToBuild = "ToBuild"
    kBuilt = "Built"
    kToUpdate = "ToUpdate"
    kError = "Error"

    kRed = [200, 50, 50]
    kDarkRed = [200, 20, 20]
    kGreen = [20, 200, 20]
    kOrange = [200, 150, 20]

    kStates = {kToBuild: kRed,
               kBuilt: kGreen,
               kToUpdate: kOrange,
               kError: kDarkRed}

    def __init__(self):
        self._value = self.kToBuild
        self._color = self.kRed

    @property
    def color(self) -> list:
        return self._color

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        if value not in self.kStates:
            raise RuntimeError("Invalid state given")
        self._value = value
        self._color = self.kStates[value]
