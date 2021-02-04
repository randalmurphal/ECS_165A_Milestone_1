from table import Table, Record
from index import Index
from conceptual_page import ConceptualPage
from page_range import PageRange
from page import Page

import numpy as np
import time
import math

MAX_INT = int(math.pow(2, 63) - 1)

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
        return True # Deleted :)

    def add_meta(self, new_base, page_index, values):
        new_base.pages[1][page_index].write(values[0])
        new_base.pages[2][page_index].write(values[1])
        new_base.pages[3].append(np.zeros(len(new_base.pages) - 4))

    """
    # Insert a record with specified columns
    # Return True upon succesful insertion
    # Returns False if insert fails for whatever reason
    """
    # Tuple of columns(Key,Value)
    def insert(self, *columns):
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

            values = [self.table.RID_count, 0, 0]
            self.add_meta(new_base, page_index, values)
        else:
            if new_base_page:
                self.table.page_directory[page_range_index].append_base_page(new_base)

                values = [self.table.RID_count, 0, 0]
                self.add_meta(new_base, page_index, values)

                for i, col in enumerate(columns):
                	new_base.pages[i+4][page_index].write(col)
            else:
                if new_page:
		            # append new page to current conceptualpage
                    new_base = self.table.page_directory[page_range_index].range[0][base_page_index]
                    for i in range(len(new_base.pages)):
                        if not i == 0 and not i == 3:
                            new_base.pages[i].append(Page())

                    for i, col in enumerate(columns):
                        new_base.pages[i+4][page_index].write(col)

                    values = [self.table.RID_count, 0, 0]
                    self.add_meta(new_base, page_index, values)
                else:
                    new_base = self.table.page_directory[page_range_index].range[0][base_page_index]

                    for i, col in enumerate(columns):
                        new_base.pages[i+4][page_index].write(col)

                    values = [self.table.RID_count, 0, 0]
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
        # print(len(locations))

        for location in locations:
            # print("loc:", location)
            p_range = location[0]
            base_pg = location[1]
            page    = location[2]
            record  = location[3]
            base_pages = self.table.page_directory[p_range].range[0][base_pg].pages
            rid     = base_pages[1][page].retrieve(record)
            key     = base_pages[4][page].retrieve(record)
            rec_i   = page * 512 + record
            base_schema = base_pages[3][rec_i]
            indirection = base_pages[0]

            columns = []
            # populate with base page values
            for i, col in enumerate(query_columns):
                columns.append(base_pages[i+4][page].retrieve(record))

            # Grab updated values in tail page
            if rid in indirection.keys():
                tail_rid     = indirection[rid]
                tail_page_i  = (tail_rid % 65536) // 4096
                page_i       = (tail_rid % 4096) // 512
                tail_page    = self.table.page_directory[p_range].range[1][tail_page_i].pages
                for i, col in enumerate(tail_page[4:]):
                    value = col[page_i].retrieve(tail_rid % 512)
                    if value == MAX_INT:
                        columns[i] = base_pages[i+4][page].retrieve(record)
                    else:
                        columns[i] = col[page_i].retrieve(tail_rid % 512)

            rec = Record(rid, key, columns)
            records.append(rec)
        return records

    """
    # Update a record with specified key and columns
    # Returns True if update is succesful
    # Returns False if no records exist with given key or if the target record cannot be accessed due to 2PL locking
    """
    def update(self, key, *columns):
        ind = Index(self.table)
        location = ind.locate(0, key)

        query_columns = []
        for i, col in enumerate(columns):
            if col != None:
                query_columns.append(1)
            else:
                query_columns.append(0)

        record = self.select(key, 0, query_columns)
        p_range_loc = location[0][0]
        b_page_loc  = location[0][1]
        page_loc    = location[0][2]
        record_loc  = location[0][3]

        base_page  = self.table.page_directory[p_range_loc].range[0][b_page_loc].pages

        indirection = base_page[0]
        base_schema = base_page[3][page_loc]
        record_rid  = base_page[1][page_loc].retrieve(record_loc)
        cols        = []

        tail_RID = self.table.tail_RID
        prev_tail_RID = tail_RID
        # Base Page stuff
        if record_rid in indirection.keys(): # if update has happened already (ie tail page exists for record)
            tail = indirection[record_rid]
            tail_page_i  = tail // 4096
            page_i       = (tail % 4096) // 512
            record_i     = tail % 512
            # Add updated values to cols
            for i, col in enumerate(self.table.page_directory[p_range_loc].range[1][tail_page_i].pages[4:]):
                if columns[i]==None and not base_schema[i]:
                    cols.append(MAX_INT)
                elif columns[i] == None:
                    cols.append(col[page_i].retrieve(record_i))
                else:
                    cols.append(columns[i])

            prev_tail_RID = tail
        else: # no updates for that record yet
            for col in columns:
                if col != None:
                    cols.append(col)
                else:
                    cols.append(MAX_INT)

        indirection[record_rid] = tail_RID
        self.table.tail_RID += 1

        ## FIGURING OUT WHICH TAIL PAGE TO APPEND TO, CREATE IF DOESNT EXIST
        tail_pages = self.table.page_directory[p_range_loc].range[1]
        p_range = self.table.page_directory[p_range_loc]
        if not tail_pages: # If no tail pages created, create new
            p_range.append_tail_page(ConceptualPage(columns))
        elif tail_pages[-1].full(): # if tail page full, create new
            p_range.append_tail_page(ConceptualPage(columns))
        else:
            tail_pages[-1].pages[3].append(np.zeros(len(columns)))
        # Append to most recent tail page
        # If the last tail page is full
        # print(tail_pages[-1].num_records)
        if tail_pages[-1].num_records % 512 == 0:
            for i, col in enumerate(tail_pages[-1].pages):
                # Not indirection & schema
                if not i == 0 and not i == 3:
                    col.append(Page())
        tail_page_i = tail_pages[-1].num_records // 512
        # if not tail_page_i <=512 and not tail_page_i >= 0:
        #     print(tail_page_i)
        tail_pages[-1].pages[4][tail_page_i].write(key)
        tail_pages[-1].num_records += 1
        # write column values into new tail page record
        # print(len(tail_pages[-1].pages[5:]))
        for i, col in enumerate(tail_pages[-1].pages[5:]):
            col[tail_page_i].write(cols[i+1])
        # Update Indirection for tail page
        tail_indirection = tail_pages[-1].pages[0]
        tail_indirection[tail_RID] = prev_tail_RID

        tail_schema = tail_pages[-1].pages[3][-1] # Get most recently added schema encoding
        # update base page schema encoding
        for i, col in enumerate(columns):
            if col != None:
                base_schema[i] = 1
                tail_schema[i] = 1

        return True

    """
    :param start_range: int         # Start of the key range to aggregate
    :param end_range: int           # End of the key range to aggregate
    :param aggregate_columns: int   # Index of desired column to aggregate
    # this function is only called on the primary key.
    # Returns the summation of the given range upon success
    # Returns False if no record exists in the given range
    """
    def sum(self, start_range, end_range, aggregate_column_index):
        ind = Index(self.table)
        values = ind.locate_range(start_range, end_range, aggregate_column_index)
        return sum(values)

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
