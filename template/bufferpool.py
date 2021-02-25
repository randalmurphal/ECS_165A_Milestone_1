from config import *
from page import Page
import pickle
import os
#we probably want meta data to be stored in the files
class MetaData():
    # data = some tuple of info we can extract below
    def __init__(self):
        # curr_table & curr_page_range is the currently opened file
        self.currpr = 0
        self.currbp = 0

        self.curr_page_range = 0
        self.curr_base_range = 0
        self.curr_physical_page = 0
        self.curr_tail_page = 0
        self.record_num = 0
        # last_table & last_page_range keep track of the most recently created table and page_range
        self.last_page_range = 0
        self.last_base_page = 0
        self.last_physical_page = 0 # THIS WILL BE THE PATH TO THE
        self.last_record = 0
        # currently opened curr_baseRID and curr_tailRID
        self.baseRID_count = 0
        self.tailRID_count = 0
        # Key:(table,page_range)
        # Might want to make this a file
        self.key_dict = {} #Which file to look at structed key:path
        self.indexes = {} #This is for create_index in index.py
        self.newPageNecessary = False
        # For Inserting Records
        # self.insertion_conceptual_page =
        # self.insertion_conceptual_page_path =

class BufferPool():
    def __init__(self, table_name):
        self.meta_data = MetaData()
        self.max_capacity = 16
        self.capacity = 0
        # self.array = [None] * self.max_capacity #array of pages
    #    self.array=[]
        self.conceptual_pages = []
        self.buffer_keys = {}
        self.next_evict = 0
        self.table_name = table_name

    def load(self, path):      #loads page associated with path, returns index of bufferpool the loaded page is in
        if self.capacity == self.max_capacity:
            self.evict()
        with open(path, 'rb') as db_file:
            temp_page = pickle.load(db_file)
        for i,value in enumerate(self.array):
            if value == None:
                self.array[i] = temp_page
                self.capacity += 1
                return i
    def createConceptualPage(self, path, columns):
        #1. Collect physical pages from array the conceptual page
        my_conceptual_page = ConceptualPage()
        my_conceptual_page.add_columns(columns)
        my_conceptual_page.path = path
        self.populateConceptualPage(columns, my_conceptual_page) ### TODO:
        self.addConceptualPage(my_conceptual_page)

    def addConceptualPage(self, conceptualPage):
        ### Check if bufferpool is full & evict if necessary ###
        # Check if conceptual_pages length > limit
        if len(self.conceptual_pages) >= self.max_capacity:
            # 1.Write to disk
            # 2.Kick out conceptual_page
            self.evict()

        self.conceptual_pages.append(conceptualPage)


    def populateConceptualPage(self, values, conceptualPage):
        ### TODO: Make work with values instead of record ###
        # conceptualPage.pages[1].write(record.rid)
        # conceptualPage.pages[2].write(record.time)
        # conceptualPage.pages[3].append(np.zeros(len(base_page.pages) - 6))
        # conceptualPage.pages[4].write(record.TPS)
        # conceptualPage.pages[5].write(record.baseRID)
        # for i, col in enumerate(record.columns):
        #     conceptualPage.pages[i+6].write(col)
        #
        # self.num_records += 1

    ### Assuming pages stack will be LRU at top of stack (index 0)
    def evict(self):   #evict a physical page from bufferpool (LRU)
        # Write to disk whatever is at the top of stack
        temp_cpage = self.conceptual_pages.pop(0)
        with open(temp_cpage.path, 'wb') as db_file:
            pickle.dump(temp_cpage, path)



    #def commit(self):  #commit changes in bufferpool to memory

    def checkBuffer(self,path):  #given a path to disk, check if that page is already in bufferpool
        for i,value in enumerate(self.array):
            if value:
                if value.path == path:
                    return i
        return -1

    def close(self):# evict everything from bufferpool
        for i,value in enumerate(self.array):
            if value:
                with open(value.path, 'wb') as db_file:
                    pickle.dump(value,db_file)

    def merge(self):
        '''
        1.  Identify which tail pages are to be merged:
        Possible methods for this:
            - Tail page records we are merging should be consecutive
            - Preferably use tail page records that are filled
            - Records should be committed
        after 4096 updates
        2. Load corresponding base pages for tail pages
            - Create copies, NOT references to the original base pages
        3. Consolide (actually do the fucking merge)
        4. Update the key_dir in bufferpool metadata to ensure
        '''

        merge_base_pages, merge_tail_pages = identify_pages_to_merge()

        merge_RID_dir = copy.copy(self.buffer_pool.meta_data.key_dir)
        merge_RID_dict = {}
        # Identify base pages and tail pages we will be using during merge, add them to the appropriate arrays

        def identify_pages_to_merge():
            #if conceptual_page.pages[0]
            #check through all  base pages and  check if
            merge_base_pages=[]
            merge_tail_pages=[]
            for conceptual_page  in # BP directory :
                if conceptual_page.pages[3]== 1 :

                    if conceptual_page in merge_base_pages:
                        continue
                    else:
                        merge_base_pages.append(conceptual_page)
                    #find tail pages associated w/ this  base pages
                    # ignore the tail page if we already have it in our list
                    #otherwise append
                    #PLACEHOLDER CODE
                    tail_page_path = conceptual_page.pages[0]
                    tail_page= tail_page_path[0]
                    if tail_page in merge_tail_pages:
                        continue
                    else:
                        merge_tail_pages.append(tail_page)
            return merge_base_pages, merge_tail_pages


        #key:rid value:path to tail page
        #indirec colum gives tail rid -> figure out which tail page
        #key -> tuple->path  to tail page





        # add base record RIDs to local merge dict
        for base_page in merge_base_pages:
            for base_record_num in range(512):
                base_record_RID = base_page.pages[1].retrieve(base_record_num)
                merge_key_dict[base_record_RID] = (base_page, base_record_num)

        # to check if the base record has already had an update merged with it
        base_records_already_updated = []

        # iterate through all tail pages we pulled in
        for tail_page in merge_tail_pages:
            # iterate through all tail records in a given tail page
            for tail_record_num in range(511, -1, -1):
                # Determine the original base record for this tail record
                tail_record_BaseRID = tail_page.pages[5].retrieve(tail_record_num)

                # Check if we have already merged an update to this base record. If we have merged an update: skip this tail record.
                if tail_record_BaseRID in base_records_already_updated:
                    continue

                # grab the record TID and check if it is less than the TPS number of the base record: if so, skip this tail record.
                tail_record_TID = tail_page.pages[1].retrieve(tail_record_num)
                base_page_containing_base_record, base_record_num = merge_RID_dict[tail_record_BaseRID][0], merge_RID_dict[tail_record_BaseRID][1]
                base_record_TPS = base_page_containing_base_record.pages[4].retrieve(base_record_num)
                if base_record_TPS >= tail_record_TID:
                    continue

                # We can now proceed with updating the values in the base record with the appropriate values from the tail record
                num_columns = len(tail_page.pages[6:])
                offset = 6

                for column_num in range(offset, num_columns + offset):
                    new_value = tail_page.pages[column_num].retrieve(tail_record_num)
                    # skips to the next column if null
                    if new_value == MAX_INT:
                        continue
                    else:
                        # writes the new value into the base record
                        base_page_containing_base_record.pages[column_num].overWrite(base_record_num, new_value)
