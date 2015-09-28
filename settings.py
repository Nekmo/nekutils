from importlib import import_module
import inspect

__author__ = 'nekmo'


class MetaSettings(type):
    registers_attr = 'registers'
    class_name_attr = 'settings_type'

    def __new__(mcs, clsname, bases, attrs):
        newclass = super().__new__(mcs, clsname, bases, attrs)
        name = getattr(newclass, mcs.class_name_attr)
        parents = filter(lambda x: hasattr(x, mcs.registers_attr), inspect.getmro(newclass))
        for parent in parents:
            getattr(parent, mcs.registers_attr)[name] = newclass
        return newclass


class Settings(metaclass=MetaSettings):
    settings_type = None
    registers = {}
    _settings_attrs = []

    @staticmethod
    def only_upper(params):
        return {key: value for key, value in params.items() if key.isupper()}

    def populate_from_dict(self, params):
        for key, value in params.items():
            self._settings_attrs.append(key)
            setattr(self, key, value)

    def get_dict(self):
        return {key: getattr(self, key) for key in self._settings_attrs}


class PythonFileSettings(Settings):
    settings_type = 'python_file'
    settings_path = None

    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.initialize()

    def initialize(self):
        mod = import_module(self.settings_path)
        self.populate_from_dict(self.only_upper(vars(mod)))


def get_settings(settings_type, *args, **kwargs):
    setting_class = Settings.registers[settings_type]
    return setting_class(*args, **kwargs)
