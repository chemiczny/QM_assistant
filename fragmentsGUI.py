#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:36:36 2018

@author: michal
"""
try:
    from pymol import cmd
except:
    pass
    
class FragmentsGUI():
    def __init__(self):
        self.fragments= {}
    
    def removeSelectedFragment(self):
#        currentSel = self.tree_scannedBonds.focus()
#        if not currentSel:
#            return
#        
#        currentSel = self.tree_scannedBonds.index(currentSel)
#        
#        del self.scannedBonds[currentSel]
#        self.printScannedBonds()
        pass
    
    def modifySelectedFragment(self):
#        currentSel = self.tree_scannedBonds.focus()
#        if not currentSel:
#            return
#        
#        currentSel = self.tree_scannedBonds.index(currentSel)
#        bond2modify = self.scannedBonds[currentSel]
#        self.modifyScannedBond = currentSel
#        self._clearScannedBondEntries()
#        self._insertScannedBondEntries(bond2modify)
        pass
    
    def fragmentFromSelection(self):
#        try:
        self.updateModel()
        
        stateNo = cmd.get_state()
        atoms = cmd.get_model("sele", stateNo)
        
        atomsId = [ a.index -1 for a in atoms.atom  ]
        name = self.ent_fragment.get()
        
        self._clearFragmentEntries()
        self._insertFragment(name, atomsId)
#        except:
#            print("lo kurla")
            
    def _clearFragmentEntries(self):
        self.ent_fragment.delete(0, "end")
        
    def _insertFragment(self, name, atoms):
        self.fragments[name] = atoms
        self.fragmentsList.insert("end", name)
        
    def showFragment(self):
        self.updateModel()
        currentFragment = self.fragmentsList.get( self.fragmentsList.curselection() )
        frozenSelections = ""
        for fa in self.fragments[currentFragment]:
            if frozenSelections != "":
                frozenSelections += "or id "+str(fa+1)
            else:
                frozenSelections = "id "+str(fa+1)
                
        cmd.select("fragment"+currentFragment, frozenSelections)
        cmd.show("spheres", "fragment"+currentFragment )
        cmd.set ("sphere_scale", 0.5, "fragment"+currentFragment)
        
    def _findFragmentId(self, atomId):
        for key in self.fragments:
            if atomId in self.fragments[key]:
                return "(Fragment="+key+")"
            
        return ""