#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:48:12 2018

@author: michal
"""

import sys
from os.path import join, expanduser, isdir
import json
from os import mkdir

if sys.version_info[0] < 3:
    import Tkinter
    from Tkinter import LEFT, RIGHT
    import tkMessageBox, tkFileDialog
    from pymol import cmd
    import ttk
else:
    import tkinter as Tkinter
    from tkinter import LEFT, RIGHT
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
    import tkinter.ttk as ttk
    
from parser import Parser
from GUI import GUI

class Model(Parser, GUI):
    def __init__(self):
        self.scrDir = expanduser("~/.qm_assistant")
        
        if not isdir(self.scrDir):
            mkdir(self.scrDir)
        
        self.resetAtributes()
        self.exists = False
        
    def resetAtributes(self):
        self.xyz = {}
        self.elements = {}
        self.frozen = set([])
        self.frozenBonds = set([])
        self.scannedBonds = []
        self.sourceType = None
        self.sourceFile = None
        self.energyPlot = None
        self.fragments = {}
        self.atomId2atomIndex = {}
        
#        self.exists = False
        self.objectName = "MortalKombat"
        self.frozenBondsNames = []
        self.scannedBondsNames = []
        self.modifyScannedBond = -1

    
    def plot(self):
        if self.energyPlot != None:
            self.energyPlot.plot()
        
        
    def updateModel(self):
        try:
            stateNo = cmd.get_state()
            atoms = cmd.get_model(self.objectName, stateNo)
            newXYZ = {}
            newElements = {}
#            newAtomsIdDecr = [ atId -1 for atId in newAtomsId ]
            for at in atoms.atom:
                newXYZ[at.id] =  at.coord
                newElements[at.id] = at.symbol
             
            self.xyz = newXYZ
            self.elements = newElements
        except:
            print("simulation")
        
    def saveLastGeomAsG16Inp(self):
        if not self.xyz and not self.sourceFile:
            return
        
        self._saveAsG16()
                
    def saveCurrentViewAsG16Inp(self):
        self.updateModel()
        self._saveAsG16()

        
    def loadFreqsFromJson(self):
        freqFile = tkFileDialog.askopenfilename(title = "Select file", filetypes = (("JSON files","*.json"), ("all files","*.*")) )
        
        if freqFile == "" or freqFile == ():
            return
        
        freqF = open(freqFile, 'r')
        self.freqs = json.load(freqF)
        freqF.close()
        
        self.tree_frequencies.delete(*self.tree_frequencies.get_children())
        
        for item in self.freqs:
            self.tree_frequencies.insert('', "end" , values = [  str(item["Frequency"]), str(item["IRintensity"]) ] )
            
    def showFreq(self):
        currentSel = self.tree_frequencies.focus()
        if not currentSel:
            return
        
        currentSel = self.tree_frequencies.index(currentSel)
        selectedFreq = self.freqs[currentSel]
        
        self.updateModel()
        self.writeFreqAsXyz(selectedFreq)
        
        cmd.disable(self.objectName)
        cmd.load(join(self.scrDir, "freq.xyz"))
    

    