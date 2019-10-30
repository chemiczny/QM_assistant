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
    
class FrozenBondsGUI():
    def __init__(self):
        self.frozenBonds = set([])
        self.frozenBondsNames = []
    
    def showFrozenBonds(self):
        self.updateModel()
        self.hideFrozenBonds()
        
        for i, pair in enumerate(self.frozenBonds):
            self._showFrozenBond(pair, i)
        
    def _showFrozenBond(self, pair, i):
        pairList = list(pair)
        coords1 = self.xyz[ pairList[0] ]
        coords2 = self.xyz[ pairList[1] ]
        
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
                tkMessageBox.showinfo("Cannot remove bond", "You have to select exacly 2 atoms!")
                return
            
            id1 = atoms.atom[0].id
            id2 = atoms.atom[1].id
            
            self.frozenBonds.add(frozenset([id1, id2 ]))
        except:
            print("lo kurla")
            
    def removeSelectionFromFrozenBonds(self):
        try:
            self.updateModel()
            stateNo = cmd.get_state()
            atoms = cmd.get_model("sele", stateNo)
            
            if len(atoms.atom) != 2:
                tkMessageBox.showinfo("Cannot remove bond", "You have to select exacly 2 atoms!")
                return
            
            id1 = atoms.atom[0].id
            id2 = atoms.atom[1].id
            
            self.frozenBonds.discard( frozenset(id1, id2) )
            
        except:
            print("lo kurla")