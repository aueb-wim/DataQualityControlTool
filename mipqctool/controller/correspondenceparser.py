#!/usr/bin/env python3
import os
import re

class CorrespondenceParser():
 
    PARENTH_REG = '([a-zA-Z_]{1}[a-zA-Z_\d]*\s?)\(([a-zA-Z\d\_,\(\)\s]*)\)'

    #Doing a syntax check without actually running the mipmap-Engine
    @staticmethod
    def firstCheckParentheses(expr):
        openPar = expr.count("(")
        closePar = expr.count(")")
        if openPar == closePar:
            return True
        return False

    #Separates Source Columns and Functions. Returns a tuple with the Source Columns list and the Functions list
    @staticmethod
    def separateSColumnsFunctions(expr, ddlFunctions):
        if not CorrespondenceParser.firstCheckParentheses(expr):
            raise SyntaxError("Syntax error in the given expression: Parentheses issue.")
        columns = []
        functions = []
        columns, functions = separateSColumnsFunctionsR(expr, columns, functions, ddlFunctions)
        return columns, functions

    @staticmethod
    def separateSColumnsFunctionsR(expr, columns, functions, ddlFunctions):
        match = re.match(CorrespondenceParser.PARENTH_REG, expr, flags=re.UNICODE)
        if match:
            label_name=match.group(1)
            expression_name=ddlFunctions.get(label_name)
            #functions.append(TrFunction(label_name, expression_name,....... ))

            
        
        countOpenP = 0  #count twn "(" pou den exoun kleisei
        

    class ParsingColumn(object):
        """An auxiliary class for storing a variable's name from source and adding all the prefixes MIPMAP wants"""
        def __init__(self, v_short_name, source_table_name, source_db_name):
            self.v_short_name = v_short_name
            self.v_long_name=source_db_name+"."+source_table_name+"."+source_table_name+"Tuple."+v_short_name