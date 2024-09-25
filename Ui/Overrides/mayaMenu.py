import traceback
import uuid

from maya import cmds

from ...Core.logger import log
from ...Helpers import quickScripts


kMainWindow = "MayaWindow"


class MenuItem(object):

    def __init__(self, label: str, annotation: str = None, parent: str = kMainWindow):
        self._label = label
        self._annotation = annotation
        self._parent = parent
        self._name = f"{self._label}_{str(uuid.uuid4()).replace('-', '_')}"
        self._full_path = None
        self._items = []
    
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}(name: {self._name}, label: {self._label}"
    
    @property
    def path(self):
        return self._full_path
    
    def add_item(self, item):
        item.parent = self
        self._items.append(item)

    def create(self):
        log.warning(f"Create menu {self._name}")
        self._full_path = cmds.menu(self._name,
                                    parent=self._parent,
                                    visible=True,
                                    tearOff=True,
                                    allowOptionBoxes=True,
                                    label=self._label)

        for item in self._items:
            item.create()


class Item(MenuItem):

    def __init__(self, label: str, annotation: str = None,
                 image: str = None, command: str = None):
        super(Item, self).__init__(label, annotation)

        self._parent = None
        self._image = image
        self._command = command
    
    @property
    def parent(self) -> MenuItem:
        return self._parent
    
    @parent.setter
    def parent(self, value: MenuItem):
        self._parent = value

    def create(self):
        try:
            is_sub = bool(len(self._items))
            self._full_path = cmds.menuItem(self._name,
                                            parent=self._parent.path,
                                            tearOff=True,
                                            label=self._label,
                                            annotation=self._annotation,
                                            image=None if is_sub else self._image,
                                            subMenu=is_sub)
            
            if not is_sub and self._command:
                cmds.menuItem(self.path, edit=True, command=self._command)
        except Exception as e:
            log.error(f"Error on create item {self._name} !")
            log.debug(traceback.format_exc())
            raise e
        
        for item in self._items:
            item.create()


_sub_menu = {}

def __build_sub_menu(menu_name: str, parent: MenuItem = None):
    if not menu_name:
        return

    sub_menu = None
    if menu_name in _sub_menu:
        sub_menu = _sub_menu[menu_name]
    else:
        sub_menu = Item(menu_name, annotation="")
        _sub_menu[menu_name] = sub_menu
        if parent:
            parent.add_item(sub_menu)

    return sub_menu


def build_hodorig_menu():
    main_menu = MenuItem("HodoRig", annotation="HodoRig Tools")
    scripts = quickScripts.get_scripts()
    for name, mod in scripts.items():
        if not mod.kMayaMenu:
            continue
        sub_menu = __build_sub_menu(mod.kCategory, parent=main_menu)
        item = Item(name, annotation=mod.kAnnotation, image=mod.kImage,
                    command=f"from {mod.__name__} import main as hodorMain; hodorMain()")
        sub_menu.add_item(item) if sub_menu else main_menu.add_item(item)
    main_menu.create()