class Mapping(object):
    """Class for creating a mapping task xml for mipmap engine."""
    def __init__(self):
        self.config = None
        self.source = None
        self.target = None
        self.correspondences = {}#Dict: key:CDE code ->Value: correspondence

    def add_correspondence(self, key, value):
        self.correspondences.add(key, value)

    def del_correspondence(self, key):
        self.correspondences.pop(key)#throughs KeyError exception

    #examines if there already exists a correspondence for this CDE
    def contains(self, code):
        return code in self.correspondences