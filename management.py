import logging
import os
import sys
from .settings import get_settings
from .strings import is_chars, regex_default

__author__ = 'nekmo'


class Subcommand(object):
    """Base para crear subcomandos. Éstos podrán tener propiedades como los argumentos
    que tendrá por línea de comandos y método para validaciones."""
    pass


class ManagementBase(object):
    _subcommand_pattern = 'subcommand_{}'
    _subcommand_pattern_regex = 'subcommand_(.+)'
    settings_type = 'python_file'
    default_settings_environ_key = 'NEKMO_SETTINGS_MODULE'
    default_settings_value = None  # En función a settings_type
    prog = None
    description = None
    default_level = logging.INFO
    parser = None
    _subcommands = {}  # Diccionario con asignaciones subcommand: function
    subcommands = []  # Listado con los nombres de los subcomandos para su uso
    settings = None  # Clase de settings

    def __init__(self, settings=None, description=None, default_level=None):
        self.parser = self.argument_parser(settings, description, default_level)
        self.subparser = self.argument_subparser()

    def argument_parser(self, settings=None, description=None, default_level=None):
        parser = self.get_parser(description)
        self.add_basic_arguments(parser, settings or self.get_default_settings_value(), default_level)
        self.add_extra_arguments(parser)
        return parser

    def get_parser(self, description=None):
        import argparse
        return argparse.ArgumentParser(prog=self.get_prog(),
                                       description=self.get_description(description))

    def argument_subparser(self, parser=None):
        parser = parser or self.parser
        subparser = self.get_subparser(parser)
        self.add_extra_subarguments(subparser)
        self.add_subcommands(subparser)
        return subparser

    def get_subparser(self, parser=None):
        parser = parser or self.parser
        return parser.add_subparsers()

    def add_basic_arguments(self, parser=None, settings=None, default_level=None):
        parser = parser or self.parser
        default_level = default_level or self.default_level
        parser.add_argument('-q', '--quiet', help='set logging to ERROR',
                            action='store_const', dest='loglevel',
                            const=logging.ERROR, default=default_level)
        parser.add_argument('-d', '--debug', help='set logging to DEBUG',
                            action='store_const', dest='loglevel',
                            const=logging.DEBUG, default=default_level)
        parser.add_argument('-v', '--verbose', help='set logging to COMM',
                            action='store_const', dest='loglevel',
                            const=5, default=default_level)
        parser.add_argument('-s', '--settings', help='Settings file module',
                            default=settings)
        return parser

    def parse_arguments(self, ns):
        self.set_settings(ns.settings)

    def add_extra_arguments(self, parser=None):
        parser = parser or self.parser
        return parser

    def add_extra_subarguments(self, subparser=None):
        subparser = subparser or self.subparser
        return subparser

    def add_subcommands(self, subparser=None, subcommands=None):
        subparser = subparser or self.subparser
        subcommands = subcommands or self.subcommands
        for subcommand in subcommands:
            subcommand_name = None
            if is_chars(subcommand):
                subcommand_name = subcommand
                subcommand_function = self._subcommand_pattern.format(subcommand)
                if not hasattr(self, subcommand_function):
                    raise NotImplementedError('Oops! Please, create "{}" function.'.format(subcommand))
                subcommand = getattr(self, subcommand_function)
            self.add_subcommand_function(subcommand, subcommand_name, subparser=subparser)
        return subparser

    def add_subcommand_function(self, function, name=None, help_=None, subparser=None):
        subparser = subparser or self.subparser
        name = name or getattr(function, 'name', None) or regex_default(self._subcommand_pattern_regex,
                                                                        function.__name__, None)
        if name is None:
            raise ValueError('Please, provide a valid name for subcommand function "{}"'.format(function))
        help_ = help_ or getattr(function, 'name', '')
        self._subcommands[name] = function
        self.add_subcommand_argument(name, help_, subparser=subparser)

    def add_subcommand_argument(self, name, help_, subparser=None):
        subparser = subparser or self.subparser
        subcommand = subparser.add_parser(name, help=help_)
        subcommand.set_defaults(which=name)
        return subcommand

    def get_default_settings_value(self):
        return os.environ.get(self.default_settings_environ_key, None) or self.default_settings_value or \
               {'python_file': 'settings'}[self.settings_type]

    def get_prog(self, prog=None):
        return prog or self.prog or sys.argv[0]

    def get_description(self, description=None):
        description = description or self.description
        if description:
            return description
        from __main__ import __doc__ as description
        return description

    def set_settings(self, settings):
        self.settings = get_settings(self.settings_type, settings)
        self.settings_ready(self.settings)

    def settings_ready(self, settings):
        pass

    def execute(self):
        self.execute_from_command_line(sys.argv)

    def execute_from_command_line(self, argv):
        ns = self.parser.parse_args(argv[1:])
        self.parse_arguments(ns)
        self.execute_subcommand(ns)

    def execute_subcommand(self, ns):
        if ns.which in self._subcommands:
            self._subcommands[ns.which]()
