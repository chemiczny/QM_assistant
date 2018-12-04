#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:36:36 2018

@author: michal
"""
import sys
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
    
class FrozenBondsGUI():
    def __init__(self):
        self.frozenBonds = []
        self.frozenBondsNames = []
    
    def showFrozenBonds(self):
        self.updateModel()
        self.hideFrozenBonds()
        for i, pair in enumerate(self.frozenBonds):
            self._showFrozenBond(pair, i)
        
    def _showFrozenBond(self, pair, i):
        coords1 = self.xyz[-1][ self.atomIds.index(pair[0]) ]
        coords2 = self.xyz[-1][ self.atomIds.index(pair[1]) ]
        
        arguments = [ 9.0 ] + coords1 + coords2 + [ 0.28  , 1 , 0, 0, 1, 0 ,0 ]
        
        cmd.load_cgo( arguments , "frozenBond"+str(i)  )
        self.frozenBondsNames.append("frozenBond"+str(i))
        
    def hideFrozenBonds(self):
        for frozenName in self.frozenBondsNames:
            cmd.delete(frozenName)
        
    def addSelection2FrozenBonds(self):
        try:
            self.updateModel()
            
            stateNo = cmd.get_state()
            atoms = cmd.get_model("sele", stateNo)
            
            if len(atoms.atom) != 2:
                return
            
            id1 = atoms.atom[0].index-1
            id2 = atoms.atom[1].index-1
            
            self.frozenBonds.append([id1, id2 ])
        except:
            print("lo kurla")
            
    def removeSelectionFromFrozenBonds(self):
        try:
            self.updateModel()
            stateNo = cmd.get_state()
            atoms = cmd.get_model("sele", stateNo)
            
            if len(atoms.atom) != 2:
                return
            
            id1 = atoms.atom[0].index-1
            id2 = atoms.atom[1].index-1
            
            for bond in self.frozenBonds:
                if id1 in bond and id2 in bond:
                    self.frozenBonds.remove(bond)
                    break
            
        except:
            print("lo kurla")