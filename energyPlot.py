#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:49:50 2018

@author: michal
"""
import sys
from math import sqrt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
if sys.version_info[0] < 3:
    import Tkinter
    from Tkinter import LEFT, RIGHT
    import tkMessageBox, tkFileDialog
    from pymol import cmd, plugins, CmdException, cgo
    import ttk
else:
    import tkinter as Tkinter
    from tkinter import LEFT, RIGHT
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
    import tkinter.ttk as ttk
class EnergyPlot:
    def __init__(self, energies, xyz, scannedBonds, elements):
        self.fullEnergies = energies
        if len(scannedBonds) == 0:
            self.axis = [ list(range(0, len(self.fullEnergies ))) ]
            self.axisTitle = "Optimization step"
            self.energies2plot = self.fullEnergies
        elif len(scannedBonds) == 1:
            distances = self.getDistance(xyz, scannedBonds[0])
            self.getDataPlot1D(energies, distances)
            self.axisTitle = [ self.prettyScanTitle(scannedBonds[0], elements) ]
        elif len(scannedBonds) == 2:
            distances1 = self.getDistance(xyz, scannedBonds[0])
            distances2 = self.getDistance(xyz, scannedBonds[1])

            self.getDataPlot2D(energies, distances1, distances2)
            self.axisTitle = [ self.prettyScanTitle(scannedBonds[0], elements),
                              self.prettyScanTitle(scannedBonds[1], elements)]
            
        self.scaleEnergy()
            
    def prettyScanTitle(self, scannedBond, elements):
        label = elements[scannedBond.atom1] + str(scannedBond.atom1) + "-"
        label += elements[scannedBond.atom2] + str(scannedBond.atom2) 
        label += " bond length"
        return label
    
    def scaleEnergy(self):
        minimalEnergy = min(self.energies2plot)
        self.energies2plot = [ (e - minimalEnergy)*627.509 for e in self.energies2plot ]
            
    def plot(self):
        figure = plt.figure()
        
        if len(self.axis) == 1:
            plt.plot( self.axis[0], self.energies2plot )
            plt.xlabel( self.axisTitle )
        else:
            ax = figure.gca(projection = '3d')
            ax.plot_trisurf(self.axis[0], self.axis[1], self.energies2plot)
            ax.set_xlabel(self.axisTitle[0])
            ax.set_ylabel(self.axisTitle[1])
            
        plt.show()
        
    def getDistance( self, xyz, scannedBond):
        atom1Ind = scannedBond.atom1
        atom2Ind = scannedBond.atom2
        
        distances = []
        for frame in xyz:
            coord1 = frame[atom1Ind]
            coord2 = frame[atom2Ind]
            newDist = 0
            
            for c1, c2 in zip(coord1, coord2):
                newDist += (c1-c2)*(c1-c2)
                
            distances.append(sqrt(newDist))
            
        return distances
    
    def getDataPlot1D(self, energies, distances ):
        energies.reverse()
        distances.reverse()
        
        lastDistance = 666
        energies2plot = []
        distances2axis = []
        
        for d, e in zip(distances, energies):
            if abs(d-lastDistance) > 0.001:
                energies2plot.append(e)
                distances2axis.append(d)
                lastDistance = d
                
        self.energies2plot = energies2plot
        self.axis = [ distances2axis ]
        
    
        
    def getDataPlot2D(self, energies, distances1, distances2):
        energies.reverse()
        distances1.reverse()
        distances2.reverse()
        
        lastDistance1 = 666
        lastDistance2 = 666
        energies2plot = []
        distances2axis1 = []
        distances2axis2 = []
        
        for d1, d2, e in zip(distances1, distances2, energies):
            if abs(d1-lastDistance1) > 0.001 or abs(d2 - lastDistance2) > 0.001:
                energies2plot.append(e)
                distances2axis1.append(d1)
                distances2axis2.append(d2)
                lastDistance1 = d1
                lastDistance2 = d2
                
        self.energies2plot = energies2plot
        self.axis = [ distances2axis1,distances2axis2 ]