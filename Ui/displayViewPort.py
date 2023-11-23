from maya import cmds

kGreen = 0x00379F29
kYellow = 0x00D8641A
kRed = 0x00AF1D1D
kBlue = 0x001D4CAF

kTopLeft = "topLeft"
kTopCenter = "topCenter"
kTopRight = "topRight"
kMidLeft = "midLeft"
kMidCenter = "midCenter"
kMidCenterTop = "midCenterTop"
kMidCenterBot = "midCenterBot"
kMidRight = "midRight"
kBotLeft = "botLeft"
kBotCenter = "botCenter"
kBotRight = "botRight"

kBlocSize = 15


def _display(msg: str, color: hex, pos: str = kBotRight, block_size: int = kBlocSize):
    cmds.inViewMessage(statusMessage=msg,
                       position=pos,
                       fade=True,
                       backColor=color,
                       clickKill=True,
                       textAlpha=1.0,
                       textOffset=block_size)

def display_info(msg: str, pos: str = kBotRight, block_size: int = kBlocSize):
    _display(msg, kGreen, pos=pos, block_size=block_size)


def display_warning(msg: str, pos: str = kBotRight, block_size: int = kBlocSize):
    _display(msg, kYellow, pos=pos, block_size=block_size)


def display_error(msg: str, pos: str = kBotRight, block_size: int = kBlocSize):
    _display(msg, kRed, pos=pos, block_size=block_size)


def display_debug(msg: str, pos: str = kBotRight, block_size: int = kBlocSize):
    _display(msg, kBlue, pos=pos, block_size=block_size)
