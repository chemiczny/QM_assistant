#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:46:10 2018

@author: michal
"""

import sys
from fetchDialog import fetchdialog

if sys.version_info[0] < 3:
    from pymol import plugins
else:
    pass

def __init_plugin__(self=None):
    plugins.addmenuitem('QM assistant', fetchdialog)
    
   
if __name__ == "__main__":
    fetchdialog(True)