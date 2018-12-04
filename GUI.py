#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:35:26 2018

@author: michal
"""
from fragmentsGUI import FragmentsGUI
from scannedBondsGUI import ScannedBondsGUI
from frozenAtomsGUI import FrozenAtomsGUI
from frozenBondsGUI import FrozenBondsGUI


class GUI(FragmentsGUI, ScannedBondsGUI, FrozenAtomsGUI, FrozenBondsGUI):
    def __init__(self ):
        pass