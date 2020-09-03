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
    import ttk
else:
    import tkinter as Tkinter
    from tkinter import LEFT, RIGHT
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
    import tkinter.ttk as ttk
    
try:
    from pymol import cmd
except:
    pass
    
from parser import Parser
from GUI import GUI

class ModelData():
    def __init__(self, name, frozenAtoms, frozenBonds, scannedBonds, energyPlot, fragments, slurmSection, routeSection):
        self.name = name
        self.frozenAtoms = frozenAtoms
        self.frozenBonds = frozenBonds
        self.scannedBonds = scannedBonds
        self.energyPlot = energyPlot
        self.fragments = fragments
        self.slurmSection = slurmSection
        self.routeSection = routeSection

class Model(Parser, GUI):
    def __init__(self):
        self.scrDir = expanduser("~/.qm_assistant")
        
        if not isdir(self.scrDir):
            mkdir(self.scrDir)
        
        self.resetAtributes()
        self.exists = False
        self.savedModels = {}
        
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
        
    def saveActualModel(self):
        if not self.exists:
            return
        
        self.savedModels[ self.objectName ] = ModelData( self.objectName, self.frozen, self.frozenBonds,
                        self.scannedBonds, self.energyPlot, self.fragments, self.slurmTextG16.get("1.0", "end"), self.routeSectionG16.get("1.0", "end") )
        
        savedKeys = self.modelsListVariable.get()
        if self.objectName in savedKeys:
            return
        
        self.modelsList.insert("end", self.objectName)
        
        self.loadedModel.configure(state = "normal")
        self.loadedModel.delete(0,"end")
        self.loadedModel.insert(0, self.objectName)
        self.loadedModel.configure(state = "readonly")

    def loadModel(self):
        modelKey = self.modelsList.get( self.modelsList.curselection() )
        if modelKey == "" :
            return
        
        if not modelKey in self.savedModels:
            return
        
        self._loadModel( self.savedModels[modelKey] )
        
        self.loadedModel.configure(state = "normal")
        self.loadedModel.delete(0,"end")
        self.loadedModel.insert(0, modelKey)
        self.loadedModel.configure(state = "readonly")
        cmd.enable(modelKey)
        cmd.center(modelKey)

    def _loadModel(self, modelData):
        self.objectName = modelData.name
        self.frozen = modelData.frozenAtoms
        self.frozenBonds = modelData.frozenBonds
        self.scannedBonds = modelData.scannedBonds
        self.energyPlot = modelData.energyPlot
        self.fragments = modelData.fragments
        
        self.printScannedBonds()
        self.routeSectionG16.delete(1.0, "end")
        self.routeSectionG16.insert("end", modelData.routeSection)
        
        self.slurmTextG16.delete("1.0", "end")
        self.slurmTextG16.insert( "end", modelData.slurmSection)
    
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
    

    