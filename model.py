#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:48:12 2018

@author: michal
"""

import sys
from os.path import join, basename
from math import sqrt
from rewriteG16Inp2xyz import rewriteG16Inp2xyz
from scannedBond import ScannedBond
from energyPlot import EnergyPlot
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

class Model:
    def __init__(self):
        self.scrDir = "/home/michal/scr"
        self.xyz = []
        self.elements = []
        self.frozen = []
        self.frozenBonds = []
        self.scannedBonds = []
        self.atomIds = []
        self.sourceType = None
        self.sourceFile = None
        self.energyPlot = None
        
        self.exists = False
        self.objectName = "MortalKombat"
        self.frozenBondsNames = []
        self.scannedBondsNames = []
        self.modifyScannedBond = -1
        
    def resetAtributes(self):
        self.xyz = []
        self.elements = []
        self.frozen = []
        self.frozenBonds = []
        self.scannedBonds = []
        self.atomIds = []
        self.sourceType = None
        self.sourceFile = None
        self.energyPlot = None
        
        self.exists = False
        self.objectName = "MortalKombat"
        self.frozenBondsNames = []
        self.scannedBondsNames = []
        self.modifyScannedBond = -1
        
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
            
            self.sourceType = "g16Inp"
            self.printScannedBonds()
            self.routeSectionG16.delete(1.0, "end")
            self.routeSectionG16.insert("end", moleculeData["routeSection"])
    
    def printScannedBonds(self):
        self.tree_scannedBonds.delete(*self.tree_scannedBonds.get_children())
        
        for scannedBond in self.scannedBonds:
            self.tree_scannedBonds.insert('', "end" , values = [  str(scannedBond.atom1), str(scannedBond.atom2),
                                                                str(scannedBond.start), str(scannedBond.stop), str(scannedBond.step), str(scannedBond.points)]  )
    
    def loadG16Log(self):
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
            
            line = terachemF.readline()
        
        self.frozen = [ int(fA) - 1 for fA in frozenAtoms ]
        self.frozenBonds = []
        for bond in frozenBonds:
            [a, b] = bond.split("_")
            self.frozenBonds.append( [ int(a)-1, int(b)-1 ]  )
        
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
        
    def plot(self):
        if self.energyPlot != None:
            self.energyPlot.plot()
            
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
            
            if len(atoms.atom) != 2:
                return
            
            for at in atoms.atom:       
                id2remove = at.index-1
                if id2remove in self.frozen:
                    self.frozen.remove(id2remove)
            
        except:
            print("lo kurla")
            
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
        
    def updateModel(self):
        try:
            stateNo = cmd.get_state()
            atoms = cmd.get_model(self.objectName, stateNo)
            newXYZ = []
            newElements = []
            newAtomsId = cmd.identify(self.objectName, 0)
            newAtomsIdDecr = [ atId -1 for atId in newAtomsId ]
            
            for at in atoms.atom:
                newXYZ.append(at.coord)
                newElements.append(at.name)
             
            self.xyz = [newXYZ]
            self.elements = newElements
            self.atomIds = newAtomsIdDecr
        except:
            print("simulation")
        
    def saveLastGeomAsG16Inp(self):
        if not self.xyz and not self.sourceFile:
            return
        
        self._saveAsG16()
                
    def saveCurrentViewAsG16Inp(self):
        self.updateModel()
        self._saveAsG16()
    
    def _saveAsG16(self):
        inpName = tkFileDialog.asksaveasfilename(defaultextension = ".inp", filetypes = (("Inp files","*.inp") , ("Com files", "*.com")) )
        if inpName == () or inpName == "":
            return
        
        inputFile = open(inpName, 'w')
        inpNameBase = basename(inpName)
        
        inputFile.write("%Chk="+inpNameBase[:-3]+"chk\n")
        routeSection = self.routeSectionG16.get("1.0", "end")
        
        inputFile.write(routeSection)
        lastXyz = self.xyz[-1]
 
        for i in range( len( lastXyz )):
            xyzStr = [ str(xyz) for xyz in lastXyz[i]]

            if self.atomIds[i] in self.frozen:
                inputFile.write(self.elements[i]+" -1 " + " ".join(xyzStr)+"\n")
            else:
                inputFile.write(self.elements[i]+" 0 " + " ".join(xyzStr)+"\n")
                
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
        
        slurmFile.write("inputDir=`pwd`\n")
        slurmFile.write("cp *  $SCRATCHDIR\n")
        slurmFile.write("cd $SCRATCHDIR\n")
        
        slurmFile.write("g16 "+inpNameBase+ "\n")
        slurmFile.write("python ~/g16Log2xyz.py "+inpNameBase[:-3]+"log \n")
        slurmFile.write("cp *.log $inputDir 2>/dev/null\n")
        slurmFile.write("cp *.xyz $inputDir 2>/dev/null\n")
        
        slurmFile.close()
    
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
        