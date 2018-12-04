#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:34:24 2018

@author: michal
"""

from gaussianParser import GaussianParser
from terachemParser import TerachemParser
from xyzParser import XYZParser

class Parser(GaussianParser, TerachemParser, XYZParser):
    def __init__(self):
        pass