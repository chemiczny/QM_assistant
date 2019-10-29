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
            
            self.xyz = [ moleculeData["xyz"] ]
            self.elements = moleculeData["elements"]
            self.frozen = moleculeData["frozen"]
            self.atomIds = list(range(len(self.elements)))
            self.scannedBonds = moleculeData["bondsScanned"]
            self.frozenBonds = moleculeData["bondsFrozen"]
            
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
        lastXyz = self.xyz[-1]
 
        for i in range( len( lastXyz )):
            xyzStr = [ str(xyz) for xyz in lastXyz[i]]

            fragmentId = self._findFragmentId(i)
            if self.atomIds[i] in self.frozen:
                inputFile.write(self.elements[i]+fragmentId+" -1 " + " ".join(xyzStr)+"\n")
            else:
                inputFile.write(self.elements[i]+fragmentId+" 0 " + " ".join(xyzStr)+"\n")
                
        if self.scannedBonds or self.frozenBonds:
            inputFile.write("\n")
            if self.scannedBonds:
                for bond in self.scannedBonds:
                    inputFile.write(bond.toG16())
            if self.frozenBonds:
                for bond in self.frozenBonds:
                    inputFile.write("B "+str(bond[0]+1)+" "+str(bond[1]+1)+" F\n")
            
                
        inputFile.write("\n\n")
        inputFile.close()
        
        slurmName = inpName[:-3]+"slurm"
        slurmFile = open(slurmName, 'w')
        
        slurmHead = self.slurmTextG16.get("1.0", "end")
        
        slurmFile.write(slurmHead)
        slurmFile.write("\nmodule add plgrid/apps/gaussian/g16.A.03\n\n")
        
#        slurmFile.write("inputDir=`pwd`\n")
#        slurmFile.write("cp *  $SCRATCHDIR\n")
#        slurmFile.write("cd $SCRATCHDIR\n")
        
        slurmFile.write("g16 "+inpNameBase+ "\n")
        slurmFile.write("python ~/g16Log2xyz.py "+inpNameBase[:-3]+"log \n")
#        slurmFile.write("cp *.log $inputDir 2>/dev/null\n")
#        slurmFile.write("cp *.xyz $inputDir 2>/dev/null\n")
        
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
        