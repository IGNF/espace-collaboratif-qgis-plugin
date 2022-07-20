"""
Created on 1 oct. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""


class RipartException (Exception):
    """
    classdocs
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
