# coding=ascii

from functools import partial
import traceback
import uuid

from maya import cmds

from HodoRig.Core.logger import log


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
                func = partial(self._execute, self._command)
                cmds.menuItem(self.path, edit=True, command=func)
        except Exception as e:
            log.error(f"Error on create item {self._name} !")
            log.debug(traceback.format_exc())
            raise e
        
        for item in self._items:
            item.create()

    def _execute(self, command, *args, **kwargs):
        command()
