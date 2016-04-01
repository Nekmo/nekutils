__author__ = 'nekmo'


def get_int(value, min=None, max=None):
    """Devuelve un int, pero en unos márgenes de mínimo y máximo.
    Si value es mayor a max, devuelve max. Si es menor que min,
    devuelve min.
    """
    if min is not None and value < min:
        return min
    elif max is not None and value > max:
        return max
    return value
