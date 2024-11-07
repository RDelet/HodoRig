from __future__ import annotations

from ..Core.nameBuilder import NameBuilder


class Color:
    
    def __init__(self, name, rgb, maya_index):
        self.name = name
        self.rgb = rgb
        self.maya_index = maya_index
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return f"Color(name: {self.name}, rgb: {self.rgb}, MayaIndex: {self.maya_index})"
    
    @classmethod
    def from_name(cls, name: str | NameBuilder):
        if isinstance(name, str):
            name = NameBuilder.from_name(name)
        
        if name.side == "L":
            return kAll["Red"]
        elif name.side == "R":
            return kAll["Blue"]
        else:
            return kAll["Yellow"]



kAll = {"Black": Color("Black", (0, 0, 0), 1),
        "LightBlue": Color("LightBlue", (0, 229, 255), 18),
        "Blue": Color("Blue", (0, 0, 153), 6),
        "DarkBlue": Color("DarkBlue", (0, 0, 51), 5),
        "LightBrown": Color("LightBrown", (178, 102, 0), 24),
        "Brown": Color("Brown", (71, 30, 18), 10),
        "MidBrown": Color("MidBrown", (114, 0, 0), 12),
        "DarkBrown": Color("DarkBrown", (41, 15, 10), 11),
        "Green": Color("Green", (0, 255, 0), 14),
        "DarkGreen": Color("DarkGreen", (0, 38, 0), 7),
        "LightPink": Color("LightPink", (0, 0, 255), 20),
        "Purple": Color("Purple", (178, 0, 178), 9),
        "DarkPurple": Color("DarkPurple", (33, 0, 51), 8),
        "Red": Color("Red", (255, 0, 0), 13),
        "DarkRed": Color("DarkRed", (140, 0, 20), 4),
        "White": Color("White", (255, 255, 255), 16),
        "LightYellow": Color("LightYellow", (255, 255, 76), 22),
        "Yellow": Color("Yellow", (255, 255, 0), 17)}
