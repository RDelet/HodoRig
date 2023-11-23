class Vertex:

    def __init__(self, name, index):
        self.name = name
        self.index = index

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(node: {self.name}, index: {self.index})"

    @property
    def attribute(self) -> str:
        return '{0}.vtx[{1}]'.format(self.name, self.index)


class SoftVertex(Vertex):

    def __init__(self, name, index, weight):
        super().__init__(name, index)
        self.weight = weight

    def __repr__(self) -> str:
        return f"{super().__repr__()[:-1]}, weight: {self.weight})"