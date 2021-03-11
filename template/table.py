from template.page import *
from template.index import Index
from template.bufferpool import BufferPool
from template.lock_manager import LockManager
# from page_range import PageRange
from time import time

# These are indexes
INDIRECTION_COLUMN = 0
RID_COLUMN = 1
TIMESTAMP_COLUMN = 2
SCHEMA_ENCODING_COLUMN = 3
# Database -> Tables of diff classes -> Page Range -> Column of Data(Pages)

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
    def __init__(self, name, num_columns, key, path):
        self.currbp       = 0            # base page
        self.currpr       = 0            # page range
        self.name         = name         # table name
        self.key          = key          # table key
        self.num_columns  = num_columns  # table num columns
        self.index        = Index(self)  # index columns-
        self.buffer_pool  = None         # main Buffer Pool object
        self.lock_manager = LockManager()# if path in dict, it is locked (remove when unlocked)
        self.merge_count  = 0            # increments after update, merges when count reaches threshold
        self.merge_frequency = 100       # number of updates inbetween each time merge is called
        self.path         = path
