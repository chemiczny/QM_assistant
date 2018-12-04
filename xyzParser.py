#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:27:51 2018

@author: michal
"""
from energyPlot import EnergyPlot
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
from os.path import join, basename
from math import sqrt, sin, pi

class XYZParser:
    def __init__(self):
        pass
    
    def loadXYZ(self):
         xyz = tkFileDialog.askopenfilename(title = "Select file", filetypes = (("XYZ files","*.xyz"), ("all files","*.*") ) )
         
         if xyz != ():
             self._loadXYZ(xyz)
             
             try:
                if self.exists:
                    cmd.delete(self.objectName)
                cmd.load(xyz, self.objectName)
                cmd.show("sticks", self.objectName)
                self.exists = True
             except:
                print("simulation")
    
    def _energyFromComment(self, comment):
        if "scf done" in comment:
            return float(comment.split()[-1])
        elif "Energy" in comment:
            commentS = comment.split()
            return float( commentS[ commentS.index("Energy") + 1 ] )
        else:
            try:
                energy = float( comment.split()[0] )
                return energy
            except:
                return None
        
    def _loadXYZ(self, xyzSource):
        xyz = open(xyzSource, 'r')
        self.xyz = []
        self.elements = []
        
        line = xyz.readline()
        atomsNo = int(line)
        
        energies = []
        while True:
            commentLine = xyz.readline()
            energy = self._energyFromComment(commentLine)
            if energy != None:
                energies.append(energy)
            self._loadXYZFrame(xyz, atomsNo)
            
            nextLine = xyz.readline()
            if not nextLine:
                break
            else:
                newAtomsNo = int(nextLine)
                if newAtomsNo != atomsNo:
                    print("WTF!?")
                    break
        if len(self.xyz) ==len(energies):
            self.energyPlot = EnergyPlot(energies, self.xyz, self.scannedBonds, self.elements)
        
        xyz.close()
        
    def _loadXYZFrame(self, file, atomNo):
        newXyz = []
        newElements = []
        for i in range(atomNo):
            line = file.readline()
            lineS = line.split()
            
            newCoords = [ float(i) for i in lineS[1:]]
            newXyz.append(newCoords)
            newElements.append(lineS[0])
            
        self.xyz.append(newXyz)
        self.elements = newElements
        self.atomIds = list(range(len(newElements)))
        
    def writeFreqAsXyz(self, freq):
        framesNo = 100
        freqFile = join(self.scrDir, "freq.xyz")
        
        vector = freq["vector"]
        index2atom = {}
        for index, element in enumerate(vector):
            index2atom[int(element["atomInd"])] = int(index)
        
        freqF = open(freqFile, 'w')
        for i in range(framesNo):
            scale = sin( i * 2 * pi / framesNo )
            self.writeFreqAsXYZframe(vector, scale, freqF, index2atom)
        
        
        freqF.close()
        
    def writeFreqAsXYZframe(self, freqVector, scale, freqFile, ind2atom):
        currentXyz = self.xyz[-1]
        
        freqFile.write( str(len(self.elements)) + "\n\n" )
        coords = []
        
        for i in range(len(currentXyz)):
            currentCoords = currentXyz[i]
            currentElement = self.elements[i]
            
            if i in ind2atom:
                xmove = freqVector[ ind2atom[i]  ]["x"]
                ymove = freqVector[ ind2atom[i]  ]["y"]
                zmove = freqVector[ ind2atom[i]  ]["z"]
                
                xmove = scale * float(xmove)
                ymove = scale * float(ymove)
                zmove = scale * float(zmove)
                
                coords = [ currentCoords[0] + xmove,
                          currentCoords[1] + ymove,
                          currentCoords[2] + zmove ]
                
                coords = [ str(c) for c in coords]
            else:
                coords = [ str(c) for c in currentCoords]
            freqFile.write(currentElement+" "+" ".join(coords) + "\n")