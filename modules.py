# coding=utf-8
from importlib import import_module
import traceback
import six
import sys

__author__ = 'nekmo'


def get_module(path, print_traceback=False):
    missing_module = True
    try:
        return __import__(path, globals(), locals(), [path.split('.')[-1]])
    except ImportError as e:
        if print_traceback and e.msg not in ['No module named %s' % path.split('.')[-1],
                                                 'No module named %s' % path]:
            missing_module = False
            print(traceback.format_exc())
        # Puede ser un método  o propiedad
        module = '.'.join(path.split('.')[:-1])
        module = __import__(module, globals(), locals(), [module.split('.')[-1]])
        try:
            return getattr(module, path.split('.')[-1])
        except AttributeError as e:
            if print_traceback and e.msg != "'module' object has no attribute '%s'" % path.split('.')[-1]:
                missing_module = False
                print(traceback.format_exc())
    exception = ImportError('Missing module' if missing_module else 'Programming error')
    exception.missing_module = missing_module
    raise exception


def get_main_class(module, name):
    if hasattr(module, name.capitalize()):
        instance = getattr(module, name.capitalize())
    else:
        raise ImportError
    return instance


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])
