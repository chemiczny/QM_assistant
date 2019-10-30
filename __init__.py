#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:46:10 2018

@author: michal
"""

from fetchDialog import fetchdialog

try:
    from pymol import plugins
except:
    pass

def __init_plugin__(self=None):
    plugins.addmenuitem('QM assistant', fetchdialog)
    
   
if __name__ == "__main__":
    fetchdialog(True)