'''
Created on 26 janv. 2015

@author: AChang-Wailing
'''
from enum import Enum


class Statut(Enum):
    '''
    classdocs
    '''

    undefined = -1,
    submit
    pending
    pending0
    pending1
    pending2
    valid
    valid0
    reject
    reject0
        