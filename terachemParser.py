#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:23:15 2018

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
    
from os.path import basename

class TerachemParser:
    def __init__(self):
        pass
    
    def loadTerachemFiles(self):
        terachemInp = self.inpList.get( self.inpList.curselection() )
        xyzFile = self.xyzList.get( self.xyzList.curselection() )
        
        if xyzFile == "" or terachemInp == "":
            return
        
        if self.exists:
            cmd.delete(self.objectName)
        self.resetAtributes()
        self._loadTerachemInp(terachemInp)
        self._loadXYZ(xyzFile)
        self.printScannedBonds()
        try:
            if self.exists:
                cmd.delete(self.objectName)
            cmd.load(xyzFile, self.objectName)
            cmd.show("sticks", self.objectName)
            self.exists = True
        except:
            print("simulation")
                       
    def _loadTerachemInp(self, terachemSource):
        terachemF = open(terachemSource, 'r')
        
        line = terachemF.readline()
        frozenAtoms = []
        frozenBonds = []
        
        terachemRoute= ""
        endFound = False
        
        while line:
            if "$constraint_freeze" in line:
                while not "$end" in line:
                    if "xyz" in line:
                        frozenAtoms +=  line.replace("xyz", "").strip().split(",") 
                    if "bond" in line:
                        frozenBonds += line.replace("bond", "").strip().split(",")
                    line = terachemF.readline()
                    
            if "$constraint_scan" in line:
                while not "$end" in line:
                    if "bond" in line:
                        lineS = line.split()
                        dataDict = {}
                        atoms = lineS[4].split("_")
                        dataDict["atom1"] = int(atoms[0])-1
                        dataDict["atom2"] = int(atoms[1])-1
                        dataDict["start" ] = float(lineS[1])
                        dataDict["stop"] = float(lineS[2])
                        dataDict["points"] = int(lineS[3])
                        self.scannedBonds.append(ScannedBond(dataDict))
                    line = terachemF.readline()
            
            if line.strip() == "end":
                endFound = True
            
            if not endFound:
                if not "coordinates" in line:
                    terachemRoute += line
            line = terachemF.readline()
        
        self.frozen = [ int(fA) - 1 for fA in frozenAtoms ]
        self.frozenBonds = []
        for bond in frozenBonds:
            [a, b] = bond.split("_")
            self.frozenBonds.append( [ int(a)-1, int(b)-1 ]  )
            
        self.routeSectionTerachem.delete(1.0, "end")
        self.routeSectionTerachem.insert("end", terachemRoute)
        
    def saveCurrentViewAsTerachemInp(self):
        self.updateModel()
        self._saveAsTerachem()
        
    def _saveAsTerachem(self):
        inpName = tkFileDialog.asksaveasfilename(defaultextension = ".inp", filetypes = (("Inp files","*.inp") , ("Com files", "*.com")) )
        if inpName == () or inpName == "":
            return
        
        inputFile = open(inpName, 'w')
        inpNameBase = basename(inpName)
        xyzName = inpNameBase[:-3]+"xyz"
        
        routeSection = self.routeSectionTerachem.get("1.0", "end")
        
        inputFile.write(routeSection)
        inputFile.write("coordinates "+xyzName+"\nend\n\n")
        
        frozen = []
        for f in self.frozen:
            atomIn = self.atomIds.index(f)
            frozen.append(str(atomIn+1))
            
        frozenBonds = []
        
        for fb in self.frozenBonds:
            atom1 = self.atomIds.index(fb[0]) + 1
            atom2 = self.atomIds.index(fb[1]) + 1
            frozenBonds.append( str(atom1)+"_"+str(atom2) )
            
        if frozen or frozenBonds:
            inputFile.write("$constraint_freeze\n")
            if frozen:
                inputFile.write("xyz "+",".join(frozen)+"\n")
            if frozenBonds:
                inputFile.write("bond "+",".join(frozenBonds)+"\n")
                
            inputFile.write("$end\n")
        
        if self.scannedBonds:
            inputFile.write("\n$constraint_scan\n")
            for bond in self.scannedBonds:
                inputFile.write(bond.toTerachem())
            inputFile.write("$end\n")
            
            
        inputFile.close()
        
        slurmName = inpName[:-3]+"slurm"
        slurmFile = open(slurmName, 'w')
        
        slurmHead = self.slurmTextTerachem.get("1.0", "end")
        
        slurmFile.write(slurmHead)
        slurmFile.write("\nmodule add  plgrid/apps/terachem\n")
        slurmFile.write("$TERACHEMRUN  "+inpNameBase+" > "+ inpNameBase[:-3] + "log \n")
        
        slurmFile.close()
        
#        lastXyz = self.xyz[-1]
        xyzFile = open(xyzName, 'w')
        xyzFile.write(str(len(self.elements))+"\n\n")
        
        for el, coord in zip(self.elements, self.xyz[-1]):
            xyzFile.write(el+" "+" ".join([ str(c) for c in coord ])+"\n")
        xyzFile.close()
