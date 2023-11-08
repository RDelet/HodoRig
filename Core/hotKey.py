# coding=ascii

import collections
import json
import logging
import os
import traceback

from maya import cmds


class Hotkey(object):

    def __init__(self, **kwargs):

        self._name = kwargs.get('name', None)
        self._release_name = kwargs.get('release_command', None)
        self._key = kwargs.get('key', None)
        self._category = kwargs.get('category', 'QD_HOTKEY')
        self._language = kwargs.get('language', 'python')
        self._command = kwargs.get('command', None)
        self._release_command = kwargs.get('release_command', None)
        self._annotation = kwargs.get('annotation', None)
        self._ctrl_modifier = kwargs.get('ctrl_mod', False)
        self._alt_modifier = kwargs.get('alt_mod', False)
        self._shift_modifier = kwargs.get('shift_modifier', False)
        self._use_release = kwargs.get('use_release', None)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{0}({1}, {2})'.format(self.__class__.__name__, self._name, self._category)

    def add(self):
        """!@Brief Create MarkingMenu from dictionnary datas."""

        if not self.command_exists(self._name):
            self.add_command(self._name, self._command)
        cmds.hotkey(name='{0}_CMD'.format(self._name),
                    keyShortcut=self._key,
                    altModifier=self._alt_modifier,
                    ctrlModifier=self._ctrl_modifier,
                    shiftModifier=self._shift_modifier)

        if self._release_command:
            if self.command_exists(self._release_name):
                self.add_command(self._release_name, self._release_command)
            cmds.hotkey(name='',
                        releaseName='{0}'.format(self._release_name),
                        keyShortcut=self._key,
                        altModifier=self._alt_modifier,
                        ctrlModifier=self._ctrl_modifier,
                        shiftModifier=self._shift_modifier)

    def add_command(self, name, cmd):
        """!@Brief"""
        self.remove_command(name)
        cmds.runTimeCommand(name, annotation=self._annotation, category=self._category, command=cmd,
                            commandLanguage=self._language)
        cmds.nameCommand('{0}_CMD'.format(name), annotation='{0}_CMD'.format(self._annotation),
                         command=name, sourceType='mel')

    @staticmethod
    def command_exists(name):
        """Check if a runTimeCommand exists"""
        return cmds.runTimeCommand(name, query=True, exists=True)

    @classmethod
    def from_file(cls, path):
        """!@Brief"""
        if not os.path.exists(path):
            raise RuntimeError('Path "{0}" does not exists !'.format(path))

        try:
            with open(path, 'r') as stream:
                data = json.load(stream, object_pairs_hook=collections.OrderedDict)
        except Exception as e:
            cls.log.debug(traceback.format_exc())
            cls.log.error('Error on read file "{0}" !'.format(path))

        for name, kwargs in list(data.items()):
            kwargs['name'] = name
            try:
                cls(**kwargs).add()
            except Exception as e:
                cls.log.debug(traceback.format_exc())
                cls.log.error('Error on add hotkey "{0}" !'.format(name))

    @classmethod
    def remove_command(cls, name):
        """!@Brief"""
        if cls.command_exists(name):
            cmds.runTimeCommand(name, edit=True, delete=True)
