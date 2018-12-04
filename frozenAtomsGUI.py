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
    
class FrozenAtomsGUI():
    def __init__(self):
        self.frozen = []
    
    def showFrozen(self):
        frozenSelections = ""
        for fa in self.frozen:
            if frozenSelections != "":
                frozenSelections += "or id "+str(fa+1)
            else:
                frozenSelections = "id "+str(fa+1)
                
        cmd.select("frozen", frozenSelections)
        cmd.show("spheres", "frozen" )
        cmd.set ("sphere_scale", 0.5, 'frozen')
        
    def hideFrozen(self):
        cmd.hide("spheres", self.objectName)
        
    def addSelection2Frozen(self):
        try:
            self.updateModel()
            
            stateNo = cmd.get_state()
            atoms = cmd.get_model("sele", stateNo)

            for at in atoms.atom:       
                newId = at.index-1
                self.frozen.append(newId)
        except:
            print("lo kurla")
            
    def removeSelectionFromFrozen(self):
        try:
            self.updateModel()
            stateNo = cmd.get_state()
            atoms = cmd.get_model("sele", stateNo)
            
            for at in atoms.atom:       
                id2remove = at.index-1
                if id2remove in self.frozen:
                    self.frozen.remove(id2remove)
            
        except:
            print("lo kurla")