from table import Table, Record
from index import Index
from conceptual_page import ConceptualPage
from page_range import PageRange
from page import Page

import time

class Query:
    """
    # Creates a Query object that can perform different queries on the specified table
    Queries that fail must return False
    Queries that succeed should return the result or True
    Any query that crashes (due to exceptions) should return False
    """

    def __init__(self, table):
        self.table = table
        pass

    """
    # internal Method
    # Read a record with specified RID
    # Returns True upon succesful deletion
    # Return False if record doesn't exist or is locked due to 2PL
    """
    def delete(self, key):
        pass

    def add_meta(self, new_base, page_index, values):
        for i, value in enumerate(values):
            new_base.pages[i][page_index].write(value)

    """
    # Insert a record with specified columns
    # Return True upon succesful insertion
    # Returns False if insert fails for whatever reason
    """
    # Tuple of columns(Key,Value)
    def insert(self, *columns):
        available_RIDS = [0]

        new_page_range   = self.table.RID_count % 65536 == 0
        page_range_index = self.table.RID_count // 65536
        new_base_page    = self.table.RID_count % 4096 == 0
        base_page_index  = (self.table.RID_count % 65536) // 4096
        new_page         = self.table.RID_count % 512 == 0
        page_index       = (self.table.RID_count % 4096) // 512

        new_base  = ConceptualPage(columns)
        new_range = PageRange()

        if new_page_range:
		    # create new page range
            new_range.append_base_page(new_base) # [0].append(new_base)
            self.table.page_directory.append(new_range)
            for i, col in enumerate(columns):
            	new_base.pages[i+4][page_index].write(col)

            values = [0, self.table.RID_count, 0, 0]
            self.add_meta(new_base, page_index, values)
        else:
            if new_base_page:
                self.table.page_directory[page_range_index].append_base_page(new_base)

                values = [0, self.table.RID_count, 0, 0]
                self.add_meta(new_base, page_index, values)

                for i, col in enumerate(columns):
                	new_base.pages[i+4][page_index].write(col)
            else:
                if new_page:
		            # append new page to current conceptualpage
                    new_base = self.table.page_directory[page_range_index].range[0][base_page_index]
                    for i in range(len(new_base.pages)):
                        new_base.pages[i].append(Page())

                    for i, col in enumerate(columns):
                        new_base.pages[i+4][page_index].write(col)

                    values = [0, self.table.RID_count, 0, 0]
                    self.add_meta(new_base, page_index, values)
                else:
                    new_base = self.table.page_directory[page_range_index].range[0][base_page_index]

                    for i, col in enumerate(columns):
                        new_base.pages[i+4][page_index].write(col)

                    values = [0, self.table.RID_count, 0, 0]
                    self.add_meta(new_base, page_index, values)

        self.table.RID_count += 1
        return True

    """
    # Read a record with specified key
    # :param key: the key value to select records based on
    # :param query_columns: what columns to return. array of 1 or 0 values.
    # Returns a list of Record objects upon success
    # Returns False if record locked by TPL
    # Assume that select will never be called on a key that doesn't exist
    """
    def select(self, key, column, query_columns):
        # table -> page_directory -> page range -> conceptual page -> physical page -> record index
        ind = Index(self.table)
        locations = ind.locate(column, key)
        records = []

        for location in locations:
            p_range = location[0]
            base_pg = location[1]
            page    = location[2]
            record  = location[3]
            rid     = self.table.page_directory[p_range].range[0][base_pg].pages[1][page].retrieve(record)
            key     = self.table.page_directory[p_range].range[0][base_pg].pages[4][page].retrieve(record)

            columns = []
            for i, col in enumerate(query_columns[1:]):
                if col:
                    columns.append(self.table.page_directory[p_range].range[0][base_pg].pages[i+5][page].retrieve(record))

            rec = Record(rid, key, columns)
            records.append(rec)
        return records

    """
    # Update a record with specified key and columns
    # Returns True if update is succesful
    # Returns False if no records exist with given key or if the target record cannot be accessed due to 2PL locking
    """
    def update(self, key, *columns):
        # Create tail pages -- TODO:
        pass

    """
    :param start_range: int         # Start of the key range to aggregate
    :param end_range: int           # End of the key range to aggregate
    :param aggregate_columns: int  # Index of desired column to aggregate
    # this function is only called on the primary key.
    # Returns the summation of the given range upon success
    # Returns False if no record exists in the given range
    """
    def sum(self, start_range, end_range, aggregate_column_index):
        pass

    """
    incremenets one column of the record
    this implementation should work if your select and update queries already work
    :param key: the primary of key of the record to increment
    :param column: the column to increment
    # Returns True is increment is successful
    # Returns False if no record matches key or if target record is locked by 2PL.
    """
    def increment(self, key, column):
        r = self.select(key, self.table.key, [1] * self.table.num_columns)[0]
        if r is not False:
            updated_columns = [None] * self.table.num_columns
            updated_columns[column] = r[column] + 1
            u = self.update(key, *updated_columns)
            return u
        return False
