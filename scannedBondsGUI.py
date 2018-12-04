#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:36:36 2018

@author: michal
"""
import sys
from scannedBond import ScannedBond
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
    
class ScannedBondsGUI():
    def __init__(self):
        self.scannedBonds = []
        self.scannedBondsNames = []
    
    def showScannedBonds(self):
        self.updateModel()
        self.hideScannedBonds()
        for i, pair in enumerate(self.scannedBonds):
            self._showScannedBond(pair, i)
            
    def showSelectedScannedBond(self):
        self.updateModel()
        self.hideScannedBonds()
        currentSel = self.tree_scannedBonds.focus()
        if not currentSel:
            return
        
        currentSel = self.tree_scannedBonds.index(currentSel)
        
        selectedBond = self.scannedBonds[currentSel]
        self._showScannedBond(selectedBond, 0)
        
    def modifySelectedScannedBond(self):
        currentSel = self.tree_scannedBonds.focus()
        if not currentSel:
            return
        
        currentSel = self.tree_scannedBonds.index(currentSel)
        bond2modify = self.scannedBonds[currentSel]
        self.modifyScannedBond = currentSel
        self._clearScannedBondEntries()
        self._insertScannedBondEntries(bond2modify)
    
    def printScannedBonds(self):
        self.tree_scannedBonds.delete(*self.tree_scannedBonds.get_children())
        
        for scannedBond in self.scannedBonds:
            self.tree_scannedBonds.insert('', "end" , values = [  str(scannedBond.atom1), str(scannedBond.atom2),
                                                                str(scannedBond.start), str(scannedBond.stop), str(scannedBond.step), str(scannedBond.points)]  )
        
    def _clearScannedBondEntries(self):
        self.ent_atom1.delete(0, "end")
        self.ent_atom2.delete(0, "end")
        self.ent_start.delete(0, "end")
        self.ent_stop.delete(0, "end")
        self.ent_step.delete(0, "end")
        self.ent_points.delete(0, "end")
        
    def _insertScannedBondEntries(self, scannedBond):
        self.ent_atom1.insert("end", str(scannedBond.atom1))
        self.ent_atom2.insert( "end",str(scannedBond.atom2))
        self.ent_start.insert( "end",str(scannedBond.start))
        self.ent_stop.insert( "end",str(scannedBond.stop))
        self.ent_step.insert( "end",str(scannedBond.step))
        self.ent_points.insert( "end",str(scannedBond.points))
    
    def scannedBondFromSelection(self):
        try:
            self.updateModel()
            
            stateNo = cmd.get_state()
            atoms = cmd.get_model("sele", stateNo)
            
            if len(atoms.atom) != 2:
                return
            
            id1 = atoms.atom[0].index-1
            id2 = atoms.atom[1].index-1
            coord1 = atoms.atom[0].coord
            coord2 = atoms.atom[1].coord
            
            dist = 0
            for c1, c2 in zip(coord1, coord2):
                dist +=  (c1-c2)*(c1-c2 )
            dist = sqrt(dist)
            
            self._clearScannedBondEntries()
            newBond = ScannedBond( {"atom1" : id1, "atom2" : id2, "start" : dist})
            self._insertScannedBondEntries(newBond)
            self.modifyScannedBond = -1
        except:
            print("lo kurla")
            
    def addScannedBond(self):
        dataDict = {}

        dataDict["atom1"] = self.ent_atom1.get()
        dataDict["atom2"] = self.ent_atom2.get()
        dataDict["start"] = self.ent_start.get()
        dataDict["stop"] = self.ent_stop.get()
        dataDict["step"] = self.ent_step.get()
        dataDict["points"] = self.ent_points.get()
        newBond = ScannedBond(dataDict)
        if newBond.bondOk():
            if self.modifyScannedBond >= 0:
                self.scannedBonds[self.modifyScannedBond] =  newBond
            else:
                self.scannedBonds.append(newBond)
            self.printScannedBonds()
            
        self.modifyScannedBond = -1
        self._clearScannedBondEntries()
        
    def removeSelectedScannedBond(self):
        currentSel = self.tree_scannedBonds.focus()
        if not currentSel:
            return
        
        currentSel = self.tree_scannedBonds.index(currentSel)
        
        del self.scannedBonds[currentSel]
        self.printScannedBonds()
        
    def _showScannedBond(self, pair, i):
        coords1 = self.xyz[-1][ self.atomIds.index(pair.atom1) ]
        coords2 = self.xyz[-1][ self.atomIds.index(pair.atom2) ]
        
        arguments = [ 9.0 ] + coords1 + coords2 + [ 0.28  , 0 , 0, 1, 0, 0 ,1 ]
        
        cmd.load_cgo( arguments , "scannedBond"+str(i)  )
        self.scannedBondsNames.append("scannedBond"+str(i))
        
    def hideScannedBonds(self):
        for scannedName in self.scannedBondsNames:
            cmd.delete(scannedName)