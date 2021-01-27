from template.page import *
from template.index import Index
from time import time

INDIRECTION_COLUMN = 0
RID_COLUMN = 1
TIMESTAMP_COLUMN = 2
SCHEMA_ENCODING_COLUMN = 3


class Record:

    def __init__(self, rid, key, columns):
        self.rid = rid
        self.key = key
        self.columns = columns

class Table:

    """
    :param name: string         #Table name
    :param num_columns: int     #Number of Columns: all columns are integer
    :param key: int             #Index of table key in columns
    """
    def __init__(self, name, num_columns, key):
        self.name = name
        self.key = key
        self.num_columns = num_columns
        self.page_directory = {} # needs to point to a page within a page range when given a certain RID
        self.index = Index(self)
        self.actualTable = [                          \
                               [[],[]]                        \ #This would be page range #1         
                           ]

        pass

    def __merge(self):
        pass

