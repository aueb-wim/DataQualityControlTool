
class Correspondence(object):
    def __init__(self, source_paths, target_path, expression):
        self.source = source_paths #list of source variables
        self.target = target_path #the target CDE
        self.expression = expression
        self.firstSyntaxCheck()

    #Doing a syntax check without actually running the mipmap-Engine
    def firstSyntaxCheck(self):
        return