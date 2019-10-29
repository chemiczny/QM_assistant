#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:51:07 2018

@author: michal
"""
from math import sqrt
from scannedBond import ScannedBond

def rewriteG16Inp2xyz( gInput, xyz ):
    gInp = open(gInput, 'r')
    xyzF = open(xyz, 'w')
    
    line = gInp.readline()
    beginning = ""
    while "%" in line or "#" in line:
        line = gInp.readline()
        if "#" in line:
            beginning += line
        
    beginning += line
    while len(line.split()) != 2:
        line = gInp.readline()
        beginning += line
        
    beginning = beginning[:-1]
    line = gInp.readline().split()
    atomNo = 0
    coords = ""
    symbols = []
    xyz = []
    frozen = []
    while len(line) >=4:
        newCoords = line[-3:]
        symbol = line[0]
        coords += symbol+" "+" ".join(newCoords)+"\n"
        xyz.append( [ float(c) for c in newCoords ] )
        symbols.append( symbol )
        if len(line) == 5 and int(line[1]) == -1:
            frozen.append(atomNo)
            
        atomNo +=1
        line = gInp.readline().split()
        
    xyzF.write(str(atomNo)+"\n")
    xyzF.write("\n")
    xyzF.write(coords)
    xyzF.close()

    bondsScanned = []
    line = gInp.readline()
    while line:
        lineS = line.split()
        
        if len(lineS) == 6:
        
            if lineS[0] == "B":
                dataDict = {}
                dataDict["atom1"] = int(lineS[1])-1
                dataDict["atom2"] = int(lineS[2])-1
                dataDict["step" ] = float(lineS[5])
                dataDict["points"] = int(lineS[4])
                
                coord1 = xyz[ dataDict["atom1"] ]
                coord2 = xyz[ dataDict["atom2"] ]
                
                dist = 0
                for c1, c2 in zip(coord1, coord2):
                    dist += (c1-c2)*(c1-c2)
                    
                dist = sqrt(dist)
                dataDict["start"] = dist

                bondsScanned.append( ScannedBond( dataDict ) )
        
        line = gInp.readline()
    gInp.close()
    moleculeData = { "xyz" : xyz, "elements" : symbols, "frozen" : frozen, "bondsScanned" : bondsScanned, "routeSection" : beginning }
    return moleculeData