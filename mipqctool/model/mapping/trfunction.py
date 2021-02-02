class TrFunction(object):
    """Class for defining every transformation function used in a mapping correspondence"""
    def __init__(self, label, expression, arguments=[]):
        self.label_name = label              #the name of the function --> parsed from the text in 
        self.expression_name = expression    #the actual name of the function in MIPMAP terms
        self.arguments = arguments#list of arguments. Every arg can be plain String or another TrFunction obj
