#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:47:04 2018

@author: michal
"""
import sys
from model import Model
from glob import glob
if sys.version_info[0] < 3:
    import Tkinter
    from pymol import  plugins
    import ttk
else:
    import tkinter as Tkinter
    import tkinter.ttk as ttk


def fetchdialog(simulation = False):
    if simulation:
        root = Tkinter.Tk()
    else:
        app = plugins.get_pmgapp()
        root = plugins.get_tk_root()
        
    
    self = Tkinter.Toplevel(root)
    self.title('QM assistant')
    self.minsize(700, 500)
    self.resizable(0,0)
    
    self.model = Model()
    
    nb = ttk.Notebook(self, height = 500, width = 700)
    
    pageMain = ttk.Frame(nb)
    pageTerachem = ttk.Frame(nb)
    pageGaussian = ttk.Frame(nb)
    pageFreqs = ttk.Frame(nb)
    
    nb.add(pageMain, text = "Main")
    nb.add(pageTerachem, text = "Terachem")
    nb.add(pageGaussian, text = "Gaussian" )
    nb.add(pageFreqs, text = "Frequencies")
    nb.grid(row = 0, column = 0)
    
    #MAIN
    
    but_showFrozen = Tkinter.Button(pageMain, text = "Show frozen atoms", command = self.model.showFrozen, width = 15)
    but_showFrozen.grid(row = 0, column = 0, columnspan = 2)
    
    but_hideFrozen = Tkinter.Button(pageMain, text = "Hide frozen atoms", command = self.model.hideFrozen, width = 15)
    but_hideFrozen.grid(row = 0, column = 2, columnspan = 2)
    
    but_addSel2Frozen = Tkinter.Button(pageMain, text = "Add sel to frozen", width = 15, command = self.model.addSelection2Frozen)
    but_addSel2Frozen.grid(row = 0, column = 4, columnspan = 2)
    
    but_removeSelFromFrozen = Tkinter.Button(pageMain, text = "Remove sel", width = 15, command = self.model.removeSelectionFromFrozen)
    but_removeSelFromFrozen.grid(row = 0, column = 6, columnspan = 2)
    
    but_showFrozenBonds = Tkinter.Button(pageMain, text = "Show frozen bonds", width = 15, command = self.model.showFrozenBonds)
    but_showFrozenBonds.grid(row = 1, column = 0, columnspan = 2)
    
    but_hideFrozenBonds = Tkinter.Button(pageMain, text = "Hide frozen bonds", width = 15, command = self.model.hideFrozenBonds)
    but_hideFrozenBonds.grid(row= 1, column = 2, columnspan = 2)
    
    but_addSel2FrozenBonds = Tkinter.Button(pageMain, text = "Add sel to frozen bonds", width = 15, command = self.model.addSelection2FrozenBonds)
    but_addSel2FrozenBonds.grid(row = 1, column = 4, columnspan = 2)
    
    but_removeSelFromFrozenBonds = Tkinter.Button(pageMain, text = "Remove sel", width = 15, command = self.model.removeSelectionFromFrozenBonds)
    but_removeSelFromFrozenBonds.grid(row = 1, column = 6, columnspan = 2)
    
    but_showScannedBonds = Tkinter.Button(pageMain, text = "Show Scanned bonds", width = 15, command = self.model.showScannedBonds)
    but_showScannedBonds.grid(row = 2, column = 0, columnspan = 2)
    
    but_hideScannedBonds = Tkinter.Button(pageMain, text = "Hide Scanned bonds", width = 15, command = self.model.hideScannedBonds)
    but_hideScannedBonds.grid(row = 2, column = 2, columnspan = 2)
    
    scannedBondsHeaders = [ "Atom 1", "Atom 2", "Start", "Stop", "Step", "Points"  ]
    self.model.tree_scannedBonds = ttk.Treeview(pageMain, columns = scannedBondsHeaders , show = "headings", heigh = 5 )
    for header in scannedBondsHeaders:
            self.model.tree_scannedBonds.heading(header, text = header)
            self.model.tree_scannedBonds.column(header, width = 70)
    self.model.tree_scannedBonds.grid(row = 30, column = 0, columnspan = 6, rowspan = 5)
    self.model.tree_scannedBonds.bind("<Double-1>", self.model.showSelectedScannedBond )
    
    but_removeScannedBond = Tkinter.Button(pageMain, text = "Remove", width = 10, command = self.model.removeSelectedScannedBond)
    but_removeScannedBond.grid(row = 30, column = 6, columnspan = 2)
    
    but_modifyScannedBond = Tkinter.Button(pageMain, text = "Modify", width = 10, command = self.model.modifySelectedScannedBond)
    but_modifyScannedBond.grid(row = 31, column = 6, columnspan = 2)
    
    but_scannedBondFromSelection = Tkinter.Button(pageMain, text = "From sele", width = 10, command = self.model.scannedBondFromSelection)
    but_scannedBondFromSelection.grid(row = 32, column = 6, columnspan = 2)
    
    but_scannedBondShow = Tkinter.Button(pageMain, text = "Show", width = 10, command = self.model.showSelectedScannedBond)
    but_scannedBondShow.grid(row = 33, column = 6, columnspan = 2)
    
    entryWidth = 7
    
    self.model.ent_atom1 = Tkinter.Entry(pageMain, width = entryWidth)
    self.model.ent_atom1.grid(row = 40, column = 0)
    
    self.model.ent_atom2 = Tkinter.Entry(pageMain, width = entryWidth)
    self.model.ent_atom2.grid(row = 40, column = 1)
    
    self.model.ent_start = Tkinter.Entry(pageMain, width = entryWidth)
    self.model.ent_start.grid(row = 40, column =2 )
    
    self.model.ent_stop = Tkinter.Entry(pageMain, width = entryWidth)
    self.model.ent_stop.grid(row = 40, column = 3)
    
    self.model.ent_step = Tkinter.Entry(pageMain, width =entryWidth)
    self.model.ent_step.grid(row = 40, column = 4)
    
    self.model.ent_points = Tkinter.Entry(pageMain, width = entryWidth)
    self.model.ent_points.grid(row = 40, column = 5)
    
    but_saveScannedBond = Tkinter.Button(pageMain, text = "Save scanned bond", width = 15, command = self.model.addScannedBond)
    but_saveScannedBond.grid(row = 41, column = 0, columnspan = 2)
    
    but_plot = Tkinter.Button(pageMain, text = "Plot energies" , width = 15, command = self.model.plot)
    but_plot.grid(row = 42, column = 0, columnspan = 2)
    #TERACHEM
    
    def refreshTerachemLists():
        xyzFiles = glob("*.xyz")
        inpFiles = glob("*.in")+glob("*.com")+glob("*.inp")
        
        self.model.xyzList.delete(0, "end")
        self.model.inpList.delete(0, "end")
        
        for xyz in xyzFiles :
            self.model.xyzList.insert("end", xyz)
            
        for inpF in inpFiles:
            self.model.inpList.insert("end", inpF)
    
    self.model.xyzList = Tkinter.Listbox(pageTerachem,  height = 10, exportselection = False)
    self.model.xyzList.grid(row = 0, column =0, rowspan = 10)

    self.model.inpList = Tkinter.Listbox(pageTerachem, height = 10, exportselection = False)
    self.model.inpList.grid(row = 0, column = 1, rowspan = 10)
    
    but_readTer = Tkinter.Button(pageTerachem, text = "Read", command = self.model.loadTerachemFiles)
    but_readTer.grid(row = 0, column = 3)
    
    but_refresh = Tkinter.Button(pageTerachem, text = "Refresh dir", command = refreshTerachemLists)
    but_refresh.grid(row = 1, column = 3)
        
    but_saveCurrentViewAsTerachem = Tkinter.Button(pageTerachem, text = "Save current geometry as Terachem", width = 30, command = self.model.saveCurrentViewAsTerachemInp)
    but_saveCurrentViewAsTerachem.grid( row = 20, column = 0, columnspan = 3 )
    
    self.model.routeSectionTerachem =Tkinter.Text(pageTerachem, width =50, height = 10 )
    self.model.routeSectionTerachem.grid(row = 30, column = 0, columnspan = 5)
    self.model.routeSectionTerachem.insert("end", "# basis set\nbasis 6-31g**\n# molecular charge\ncharge -1\n# optimize geometry\nrun minimize\nmethod b3lyp\nnew_minimizer yes\n")
    
    self.model.slurmTextTerachem = Tkinter.Text(pageTerachem, width = 50, height = 10)
    self.model.slurmTextTerachem.grid(row = 40, column = 0 , columnspan = 5)
    self.model.slurmTextTerachem.insert("end" , "#!/bin/bash\n## Number of nodes\n#SBATCH -N 1\n#SBATCH --ntasks-per-node=2\n## Number of GPU cards per node\n#SBATCH --gres=gpu:2\n## Max time of job (d-h)\n#SBATCH --time=3-0\n## Partition/queue\n#SBATCH -p plgrid-gpu\n" )
     
    refreshTerachemLists()
    #GAUSSIAN
    
    but_g16log = Tkinter.Button(pageGaussian, text = "Load g16 log", command = self.model.loadG16Log, width = 10)
    but_g16log.grid(row = 0, column = 0)
    
    but_g16inp = Tkinter.Button(pageGaussian, text = "Load g16 inp", command = self.model.loadG16Inp, width = 10)
    but_g16inp.grid(row = 0, column = 1)
    
#    but_saveLastAsG16 = Tkinter.Button(pageGaussian, text = "Save last geometry as G16 inp", width =30, command = self.model.saveLastGeomAsG16Inp)
#    but_saveLastAsG16.grid(row = 1, column = 0 , columnspan =3 )
    
    but_loadXYZInto = Tkinter.Button(pageGaussian, text = "Load xyz into model", width = 30, command = self.model.loadXYZ )
    but_loadXYZInto.grid(row = 1, column = 0, columnspan = 3)
    
    but_saveCurrentViewAsG16 = Tkinter.Button(pageGaussian, text = "Save current geometry as G16", width = 30, command = self.model.saveCurrentViewAsG16Inp)
    but_saveCurrentViewAsG16.grid( row = 2, column = 0, columnspan = 3 )
    
    self.model.routeSectionG16 =Tkinter.Text(pageGaussian, width =50, height = 10 )
    self.model.routeSectionG16.grid(row = 3, column = 0, columnspan = 5)
    self.model.routeSectionG16.insert("end", "%Mem=8GB\n#P HF/6-31G(d,p)\n# Freq\n# Gfinput IOP(6/7=3)  Pop=full  Density  Test \n# Units(Ang,Deg)\n\nComment\n\n0 1")
    
    self.model.slurmTextG16 = Tkinter.Text(pageGaussian, width = 50, height = 10)
    self.model.slurmTextG16.grid(row = 4, column = 0 , columnspan = 5)
    self.model.slurmTextG16.insert("end" , "#!/bin/env bash\n#SBATCH --nodes=1\n#SBATCH --cpus-per-task=24\n#SBATCH --time=70:00:00\n##### Nazwa kolejki\n#SBATCH -p plgrid\n" )
              
    lab_fragments = Tkinter.Label(pageGaussian, text = "Fragments")
    lab_fragments.grid(row = 1, column = 10)
    
    self.model.fragmentsList = Tkinter.Listbox(pageGaussian, height = 20, exportselection = False)
    self.model.fragmentsList.grid(row = 2, column = 10, rowspan = 10)
    
    self.model.ent_fragment = Tkinter.Entry(pageGaussian)
    self.model.ent_fragment.grid(row=6, column =10)
    
    but_removeFragment = Tkinter.Button(pageGaussian, text = "Remove", width = 10 , command = self.model.removeSelectedFragment)
    but_removeFragment.grid(row = 3, column = 15)
    
    but_modifyFragment = Tkinter.Button(pageGaussian, text = "Modify", width = 10 , command = self.model.modifySelectedFragment)
    but_modifyFragment.grid(row = 4, column = 15)
    
    but_fragmentFromSelection = Tkinter.Button(pageGaussian, text = "From sele" , width = 10, command = self.model.fragmentFromSelection)
    but_fragmentFromSelection.grid(row = 5, column = 15)
    
    but_fragmentShow = Tkinter.Button(pageGaussian, text = "Show", width = 10 , command = self.model.showFragment)
    but_fragmentShow.grid(row = 6, column = 15)
    
    #Frequencies
   
    but_readFreqs = Tkinter.Button(pageFreqs, text = "Load Freqs from json", command = self.model.loadFreqsFromJson)
    but_readFreqs.grid(row = 0, column = 0)
    
    but_showFreq = Tkinter.Button(pageFreqs, text = "Show freq", command = self.model.showFreq)
    but_showFreq.grid(row = 0, column = 1)
    
    frequencyHeaders = [ "Freq", "Intens"  ]
    self.model.tree_frequencies = ttk.Treeview(pageFreqs, columns = frequencyHeaders , show = "headings", heigh = 20 )
    for header in frequencyHeaders:
            self.model.tree_frequencies.heading(header, text = header)
            self.model.tree_frequencies.column(header, width = 70)
            
    self.model.tree_frequencies.grid(row = 1, column = 0)
    
    #PAGES END
    
    if simulation:
        self.mainloop()