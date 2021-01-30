from table import Table, Record
from index import Index
from conceptual_page import ConceptualPage

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

    """
    # Insert a record with specified columns
    # Return True upon succesful insertion
    # Returns False if insert fails for whatever reason
    """
    # Tuple of columns(Key,Value)
    def insert(self, *columns):
        schema_encoding = '0' * self.table.num_columns
        dir_len = len(self.table.page_directory)
        if dir_len == 0:
            newPage = ConceptualPage()
            # Add an iterator to add keys based off of page_directory length
            self.table.page_directory[dir_len] = newPage
        else:
            # Go to most recent directory and insert pages here
            self.table.page_directory[dir_len] ### go to dir_len - (num_columns // 8) ??? if more than 8 num_columns ###
        if newPage.
		### Want to also iterate through each conceptual page in page directory, can change map to new conc page when overflow for insert ###
        for page_cols in range (self.table.num_columns + 4): # If num_columns > 8, should be on diff conceptual pages
            # Add columns to conceptual page
            newPage.add_column()
        newRecord = Record(rid,key,columns)
        if newPag
        for i in range(len(columns)):
            # Add pages to the columns
            newPage.pages[i+4].add_page(columns[i]) ### Only add a new page if previous page is full (num_records % 512 == 0)
        # Make a loop to populate the pages
    """
    # Read a record with specified key
    # :param key: the key value to select records based on
    # :param query_columns: what columns to return. array of 1 or 0 values.
    # Returns a list of Record objects upon success
    # Returns False if record locked by TPL
    # Assume that select will never be called on a key that doesn't exist
    """
    def select(self, key, column, query_columns):
        pass

    """
    # Update a record with specified key and columns
    # Returns True if update is succesful
    # Returns False if no records exist with given key or if the target record cannot be accessed due to 2PL locking
    """
    def update(self, key, *columns):
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
