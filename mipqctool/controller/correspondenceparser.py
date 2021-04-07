#!/usr/bin/env python3
import os
import re
from mipqctool.config import LOGGER
from mipqctool.exceptions import ExpressionError, FunctionNameError, ArgsFunctionError

class CorrespondenceParser():
 
    PARENTH_REG = '([a-zA-Z_]{1}[a-zA-Z_\d]*\s?)\(([a-zA-Z\d\_,\(\)\s]*)\)'
    TABLE_DOT_COL_REG = '([a-zA-Z_\d]*)\.([a-zA-Z_\d]*)'

    #Doing a syntax check without actually running the mipmap-Engine. Returns False if there is a problem.
    """@staticmethod
    def firstCheckParentheses(expr):
        openPar = expr.count("(")
        closePar = expr.count(")")
        if openPar == closePar:
            return True
        return False"""
    @staticmethod
    def firstCheckParentheses(expr):
        openPar = 0
        closePar = 0
        for c in expr:
            if c == "(":
                openPar+=1
            elif c == ")":
                closePar+=1
            else:
                continue
            if closePar > openPar:
                raise SyntaxError("Syntax error in the given expression: Parentheses issue.")
        if closePar != openPar:
            raise SyntaxError("Syntax error in the given expression: Parentheses issue. Not all parantheses have been closed.")

    #Separates Source Columns and Functions. Returns a tuple with the Source Columns list and the Functions list
    #parameters: the expression, the dict with the functions from the drop down list
    @staticmethod
    def extractSColumnsFunctions(expr, ddlFunctions):
        try:
            CorrespondenceParser.firstCheckParentheses(expr)#If it fails it will raise an Exception
        except SyntaxError as se:
            LOGGER.info(str(se))
            raise ExpressionError(str(se))
        columns = []
        functions = []
        try:
            CorrespondenceParser.extractSColumnsFunctionsR(expr, columns, functions, ddlFunctions, expr)
        except FunctionNameError as fne:
            LOGGER.info(str(fne))
            raise ExpressionError(str(fne))
        except ArgsFunctionError as afe:
            LOGGER.info(str(afe))
            raise ExpressionError(str(afe))
        #return columns, functions

    @staticmethod
    def extractSColumnsFunctionsR(expr, columns, functions, ddlFunctions, wholeExpr):
        match = re.match(CorrespondenceParser.PARENTH_REG, expr, flags=re.UNICODE)
        if match:
            label_name = match.group(1)
            args = match.group(2)
            function_key_label = CorrespondenceParser.findInDict(label_name, ddlFunctions)
            if function_key_label is None:
                raise FunctionNameError("'"+label_name+"' is not an existing function.")
            countCommasFromDDL = ddlFunctions[function_key_label].count(',')
            #print("~~~countCommasFromDDL="+countCommasFromDDL)
            if args.count(',') < countCommasFromDDL:
                raise ArgsFunctionError("Function '"+label_name+"' does not have enough arguments..!")
            #expression_name = ddlFunctions.get(label_name)
            functions.add(label_name)
            for arg in args:
                self.extractSColumnsFunctionsR(arg, columns, functions, ddlFunctions, wholeExpr)
            self.extractSColumnsFunctionsR(wholeExpr.split(arg,1)[1], columns, functions, ddlFunctions, wholeExpr)

    #Auxiliary function that searches in the Functions Dict to see if there is a function with that expression or not...
    @staticmethod
    def findInDict(expression, functionsDict):
        for key, value in functionsDict.items():
            if expression == value.split("(")[0]:
                return key
        return None

   
    ### ADDED THIS functionality of parsing a column to model/datadb.py
    #class ParsingColumn(object):
    #    """An auxiliary class for storing a variable's name from source and adding all the prefixes MIPMAP wants"""
    #    def __init__(self, v_short_name, source_table_name, source_db_name):
    #        self.v_short_name = v_short_name
    #        self.v_long_name=source_db_name+"."+source_table_name+"."+source_table_name+"Tuple."+v_short_name