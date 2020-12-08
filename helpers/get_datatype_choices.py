""" Create a list of datatype choices """
from apps.datasets.dtos import ColumnType


def get_datatype_choises():
    """ retruns set of choices for Column model """
    return tuple((c.name, c.value) for c in ColumnType)
