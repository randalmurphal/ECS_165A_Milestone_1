
class PageRange:

    def __init__(self):
        # 1st index is for base pages
        # 2nd index is for tail pages
        self.Range = [[],[]]
        self.num_base_pages = 0

    def return_page(self):
        pass

    def full(self):
        if self.num_base_pages == 16:
            return True
        else:
            return False
    def append_base_page(self,conceptual_page):
        self.num_base_pages += 1
        self.Range[0].append(conceptual_page)

    def append_tail_page(self,conceptual_page):
        # map our base pages to tail pages
        self.Range[1].append(conceptual_page)

    def merge(self,pages):
        pass
