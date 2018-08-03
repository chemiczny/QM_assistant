#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:49:22 2018

@author: michal
"""

class ScannedBond:
    def __init__(self,  dataDict ):
        if "atom1" in dataDict:
            try:
                self.atom1 =  int(dataDict["atom1"] )
            except:
                self.atom1 = None
        else:
            self.atom1 = None
            
        if "atom2" in dataDict:
            try:
                self.atom2 = int(dataDict["atom2"])
            except:
                self.atom2 = None
        else:
            self.atom2 = None
            
        if "step" in dataDict:
            try:
                self.step = float(dataDict["step" ] )
            except:
                self.step = None
        else:
            self.step = None
            
        if "points" in dataDict:
            try:
                self.points = int(dataDict["points"] )
            except:
                self.points = None
        else:
            self.points = None
            
        if "start" in dataDict:
            try:
                self.start = float(dataDict["start"])
            except:
                self.start = None
        else:
            self.start = None
            
        if "stop" in dataDict:
            try:
                self.stop = float(dataDict["stop"])
            except:
                self.stop = None
        else:
            self.stop = None
            
        self._check()
    
    def _check(self):
        noneVal = []
        for key in self.__dict__:
            if self.__dict__[key] == None:
                noneVal.append(key)
                
        if len(noneVal) == 1:
            if noneVal[0] == "step":
                self.step = (self.stop - self.start)/self.points
            elif noneVal[0] == "stop":
                self.stop = self.start + self.points * self.step
            elif noneVal[0] == "points":
                self.points = int( (self.stop - self.start)/self.step )
            elif noneVal[0] == "step":
                self.step =  (self.stop - self.start)/self.points 
            else:
                return False
            
        if len(noneVal) > 1 :
            return False
        
        return True
                
    def bondOk(self):
        return self._check()
    
    def toG16(self):
        return "B "+str(self.atom1+1)+" "+str(self.atom2+1)+" S "+str(self.points)+" "+str(self.step)+"\n"
    
    def toTerachem(self):
        return "bond "+str(self.start)+" "+str(self.stop)+ " "+str(self.points)+" "+str(self.atom1+1)+"_"+str(self.atom2+1)+"\n"
    