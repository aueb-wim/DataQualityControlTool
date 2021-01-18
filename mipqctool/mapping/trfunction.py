class TrFunction(object):
    """Class for defining every transformation function available in the GUI"""
    def __init__(self, label, expression):
        self.label = label              #the label depicted in the ComboBox
        self.expression = expression    #the actual expression in MIPMAP terms

