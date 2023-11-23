# coding=ascii

import json
import os
import traceback

from maya import cmds

from HodoRig.Core.logger import log


class Hotkey:

    def __init__(self, **kwargs):

        self.name = kwargs.get("name", "")
        self.release_name = kwargs.get("releasecommand", "")
        self.key = kwargs.get("key", None)
        self.category = kwargs.get("category", "QD_HOTKEY")
        self.language = kwargs.get("language", "python")
        self.command = kwargs.get("command", "")
        self.release_command = kwargs.get("releasecommand", "")
        self.annotation = kwargs.get("annotation", "")
        self.ctrl_modifier = kwargs.get("ctrl_mod", False)
        self.alt_modifier = kwargs.get("alt_mod", False)
        self.shift_modifier = kwargs.get("shift_modifier", False)
        self.use_release = kwargs.get("use_release", False)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.category})"

    @property
    def cmd_name(self) -> str:
        return f"{self.name}_CMD"
    
    def _add_on_press(self):
        self._add_command(self.name, self.command)
        cmds.hotkey(name=self.cmd_name,
                    keyShortcut=self.key,
                    altModifier=self.alt_modifier,
                    ctrlModifier=self.ctrl_modifier,
                    shiftModifier=self.shift_modifier)

        log.info(f"Add HotKey {self.cmd_name}")
    
    def _add_on_release(self):
        if self.release_command:
            return
        
        self._add_command(self.release_name, self.release_command)      
        cmds.hotkey(name="",
                    releaseName=self.release_name,
                    keyShortcut=self.key,
                    altModifier=self.alt_modifier,
                    ctrlModifier=self.ctrl_modifier,
                    shiftModifier=self.shift_modifier)

        log.info(f"Add release HotKey {self.cmd_name}")
    
    def add(self):
        self._add_on_press()
        self._add_on_release()

    def _add_command(self, name: str, cmd: str):
        self.removecommand(name)
        cmds.runTimeCommand(name, annotation=self.annotation,
                            category=self.category,
                            command=cmd,
                            commandLanguage=self.language)

        cmds.nameCommand(self.cmd_name,
                         annotation=f"{self.annotation}_CMD",
                         command=name, sourceType="mel")

    @staticmethod
    def command_exists(name: str) -> bool:
        return cmds.runTimeCommand(name, query=True, exists=True)
    
    @classmethod
    def removecommand(cls, name):
        if cls.command_exists(name):
            cmds.runTimeCommand(name, edit=True, delete=True)
            log.info(f"Remove HotKey command {name}")

    @classmethod
    def from_file(cls, path: str) -> list:
        """!@Brief"""
        if not os.path.exists(path):
            raise RuntimeError("Path {0} does not exists !".format(path))

        try:
            with open(path, "r") as stream:
                data = json.load(stream)
        except Exception as e:
            cls.log.debug(traceback.format_exc())
            cls.log.error("Error on read file {0} !".format(path))

        hotkeys = []
        for name, kwargs in list(data.items()):
            try:
                new_cls = cls(name=name, **kwargs)
                new_cls.add()
                hotkeys.append(new_cls)
            except Exception as e:
                cls.log.debug(traceback.format_exc())
                cls.log.error("Error on add hotkey {0} !".format(name))
        
        return hotkeys
