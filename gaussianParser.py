#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:23:01 2018

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
    
from os.path import join, basename, isdir
from os import mkdir
from rewriteG16Inp2xyz import rewriteG16Inp2xyz
class GaussianParser:
    def __init__(self):
        pass
    
    def loadG16Inp(self):
        gaussianInp = tkFileDialog.askopenfilename(title = "Select file", filetypes = (("Inp files","*.inp"), ("Txt files", "*.txt") ,("Com files","*.com"), ("all files","*.*")) )

        if gaussianInp != ():
            self.resetAtributes()
            moleculeData = rewriteG16Inp2xyz(gaussianInp, join(self.scrDir, "temp.xyz")  )
            try:
                if self.exists:
                    cmd.delete(self.objectName)
                cmd.load(join(self.scrDir, "temp.xyz"), self.objectName)
                cmd.show("sticks", self.objectName)
                self.exists = True
            except:
                print("simulation")
            
            self.frozen = set([]) 
            stateNo = cmd.get_state()
            model = cmd.get_model(self.objectName, stateNo)
            index2id = {}
            for atom in model.atom:
                index2id[atom.index] = atom.id
            
            for frozenInd in moleculeData["frozen"]:
                self.frozen.add( index2id[frozenInd] )
            
            self.scannedBonds = moleculeData["bondsScanned"]
            
            self.frozenBonds = set([])
            
            for fb in moleculeData["bondsFrozen"]:
                frozenbond = []
                for atomInd in fb:
                    frozenbond.append( index2id[atomInd] )
                    
                self.frozenBonds.add(frozenset(frozenbond))
            
            self.sourceType = "g16Inp"
            self.printScannedBonds()
            self.routeSectionG16.delete(1.0, "end")
            self.routeSectionG16.insert("end", moleculeData["routeSection"])
            
    def loadG16Log(self):
        pass
        
    def _saveAsG16(self):
        inpName = tkFileDialog.asksaveasfilename(defaultextension = ".inp", filetypes = (("Inp files","*.inp") , ("Com files", "*.com")) )
        if inpName == () or inpName == "":
            return
        self._writeG16(inpName)
        
    def _writeG16(self, inpName):
        inputFile = open(inpName, 'w')
        inpNameBase = basename(inpName)
        
        routeSection = self.routeSectionG16.get("1.0", "end")
        if not "%CHK" in routeSection.upper():
            inputFile.write("%Chk="+inpNameBase[:-3]+"chk\n")
        
        inputFile.write(routeSection)
        lastXyz = self.xyz
 
        atomId2atomIndex = {}
        sortedAtomsId = sorted( list( lastXyz.keys() ))
        for atomIndex , atomId in enumerate(  sortedAtomsId, 1):
            xyzStr = [ str(xyz) for xyz in lastXyz[atomId]]

            fragmentId = self._findFragmentId(atomId)
            if atomId in self.frozen:
                inputFile.write(self.elements[atomId]+fragmentId+" -1 " + " ".join(xyzStr)+"\n")
            else:
                inputFile.write(self.elements[atomId]+fragmentId+" 0 " + " ".join(xyzStr)+"\n")
                
            atomId2atomIndex[atomId] = atomIndex
                
        if self.scannedBonds or self.frozenBonds:
            inputFile.write("\n")
            if self.scannedBonds:
                for bond in self.scannedBonds:
                    inputFile.write(bond.toG16(atomId2atomIndex))
            if self.frozenBonds:
                for bond in self.frozenBonds:
                    bondList = list(bond)
                    inputFile.write("B "+str(atomId2atomIndex[bondList[0]])+" "+str(atomId2atomIndex[bondList[1]])+" F\n")
            
                
        inputFile.write("\n\n")
        inputFile.close()
        
        slurmName = inpName[:-3]+"slurm"
        slurmFile = open(slurmName, 'w')
        
        slurmHead = self.slurmTextG16.get("1.0", "end")
        
        slurmFile.write(slurmHead)
        slurmFile.write("\nmodule add plgrid/apps/gaussian/g16.A.03\n\n")
        
        slurmFile.write("g16 "+inpNameBase+ "\n")
        
        slurmFile.close()
        
    def saveAllFrames(self):
        inpName = tkFileDialog.asksaveasfilename(defaultextension = ".inp", filetypes = (("Inp files","*.inp") , ("Com files", "*.com")) )
        if inpName == () or inpName == "":
            return
        
        inpBasename = inpName.split(".")[-1]
        framesNo = cmd.count_frames()
        
        for i in range( 1, framesNo+1 ):
            cmd.frame(i)
            newInputName = inpBasename+str(i)+".inp"
            dirname = inpBasename+str(i)
            fullPath = join( dirname,  newInputName )
            
            if not isdir(dirname):
                mkdir(dirname)
            self.updateModel()
            self._writeG16(fullPath)
        