#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 16:05:03 2019

@author: michal
"""

import sys
import json
from os.path import expanduser, join, isdir, isfile, normpath
from os import mkdir
import json
try:
    from pymol import cmd
except:
    pass

try:
    import paramiko
except:
    pass

if sys.version_info[0] < 3:
    import Tkinter
    import tkMessageBox, tkFileDialog
    import tkSimpleDialog as simpledialog
    import ttk
    
else:
    import tkinter as Tkinter
    import tkinter.ttk as ttk
    from tkinter import simpledialog
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
    
class CommandDialog(simpledialog.Dialog):
    
    def __init__(self, parent, initialName, initialCommand):
        self.initialName = initialName
        self.initialCommand = initialCommand
        self.results = ( initialName , initialCommand )
        simpledialog.Dialog.__init__(self, parent)
        
    def buttonbox(self):
#        super().buttonbox()
        simpledialog.Dialog.buttonbox(self)
        self.unbind("<Return>")
    
    def body(self, master):

        Tkinter.Label(master, text="Name:").grid(row=0, column=0)
        Tkinter.Label(master, text="Command:").grid(row=1, column =0 ,columnspan =2)

        self.e1 = Tkinter.Entry(master, width = 50)
        self.e2 = Tkinter.Text(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=2, column=0, columnspan = 2)
        
        self.e1.insert("end", self.initialName)
        self.e2.insert("end", self.initialCommand)
        
        return self.e1 # initial focus
    

    def apply(self):
        name = self.e1.get()
        command = self.e2.get("1.0", "end")
        
        self.results = ( name, command )

    
class JobStatusGUI:
    def __init__(self, page):
        self.page = page
        
        self.ntbk = ttk.Notebook(self.page, height = 700, width = 1320)
        
        self.jobMonitor = ttk.Frame(self.ntbk)
        self.loginData = ttk.Frame(self.ntbk)
        
        self.ntbk.add( self.jobMonitor, text = "Job status" )
        self.ntbk.add( self.loginData, text = "Login data")
        
        self.ntbk.grid(column = 0, row = 0, columnspan = 20)
        
        self.treeHeaders = ["ID", "Path", "Script", "Status", "Time", "Comment"]
        self.treeHeaders2width = {"ID" : 90, "Path" : 500, "Script" : 140, "Status" : 80, "Time" : 100, "Comment" : 200 }
        
        self.client = paramiko.client.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.RejectPolicy)
        
        self.connected = False
        self.currentSelectionTree = None
        
        self.customButtonsNo = 18
        self.customButtonsPerRow = 6
        self.customButtons = []
        self.customButtonsData = []
        
        self.customButtonsLocalNo = 17
        self.customButtonsLocal = []
        self.customButtonsLocalData = []
        
        self.actualStatus = {}
        self.currentDir = ""
        
        self.grid()
        
        self.scrDir = expanduser("~/.jobStatusPro")
        self.configFile = join(self.scrDir, "config.json")
        
        if not isdir(self.scrDir):
            mkdir(self.scrDir)
        
        if isfile(self.configFile):
            with open(self.configFile, 'r') as fp:
                state = json.load(fp)
                self.loadState( state )
            
        
    def gridJobMonitor(self):
        self.tree_data = ttk.Treeview(self.jobMonitor, columns = self.treeHeaders , show = "headings", heigh = 15 )
        for header in self.treeHeaders:
            self.tree_data.heading(header, text = header)
            self.tree_data.column(header, width = self.treeHeaders2width[header])
        self.tree_data.grid(row = 0, column = 0, columnspan = 20, rowspan = 11)
        self.tree_data.bind("<Button-1>", self.setDir)
        
        columnNo = 21
        getStatusButton = Tkinter.Button(self.jobMonitor, text = "Get status", width = 15, command = self.getStatus)
        getStatusButton.grid(row=0, column = columnNo, columnspan = 2)
        
        cancelJobButton = Tkinter.Button(self.jobMonitor, text = "Cancel job", width = 15, command = self.scancel)
        cancelJobButton.grid(row=1, column = columnNo, columnspan = 2)
        
        forgetButton = Tkinter.Button(self.jobMonitor, text = "Forget", width = 15, command = self.sremovePy)
        forgetButton.grid(row=2, column = columnNo, columnspan = 2)
        
        self.filterEntry = Tkinter.Entry(self.jobMonitor, width = 7)
        self.filterEntry.grid(row= 3, column = columnNo)
        
        filterButton = Tkinter.Button(self.jobMonitor, width = 5, text = "*", command = self.filterJobs)
        filterButton.grid(row = 3, column = columnNo + 1)
        
        directoryViewLabel = Tkinter.Label(self.jobMonitor, text = "Directory contains:")
        directoryViewLabel.grid( row = 11, column = 0 , columnspan = 2)
        
        self.directoryViewList = Tkinter.Listbox(self.jobMonitor, width = 40, height = 15 )
        self.directoryViewList.grid(row = 12, column = 0, columnspan = 2, rowspan = 8)
        self.directoryViewList.bind('<Double-Button-1>', self.enterAndSetDir)
        
        refreshButton = Tkinter.Button(self.jobMonitor, text = "Refresh", width = 20, command = self.refreshDirectoryView )
        refreshButton.grid(row= 12, column =2)
        
        downloadButton = Tkinter.Button(self.jobMonitor, text = "Download", width = 20, command = self.downloadFile)
        downloadButton.grid(row=13, column = 2)
        
        toPymolButton = Tkinter.Button(self.jobMonitor, text = "to Pymol", width = 20, command = self.downloadAndLoadToPymol )
        toPymolButton.grid(row = 14, column = 2)
        
        outputLabel = Tkinter.Label(self.jobMonitor, text = "Command output")
        outputLabel.grid(row = 11, column = 3, columnspan = 4)
        
        self.outputText = Tkinter.Text(self.jobMonitor, width = 80, height =  16)
        self.outputText.grid(row = 12, column = 3, columnspan = 4, rowspan = 8)
        
        rowActual = 20
        colActual = 0
        
        for i in range( self.customButtonsNo):
            newButton = Tkinter.Button( self.jobMonitor, width = 20, command = lambda arg = i : self.customButtonCommand(arg) )
            newButton.grid(row = rowActual, column = colActual)
            newButton.bind("<Button-3>", lambda e, arg = i:self.customButtonSet(e, arg))
            self.customButtons.append(newButton)
            self.customButtonsData.append({})
            colActual += 1
            if colActual >= self.customButtonsPerRow:
                colActual = 0
                rowActual += 1
                
        rowActual += 1
        currentDirLabel = Tkinter.Label(self.jobMonitor, text = "Current dir:")
        currentDirLabel.grid( row = rowActual, column = 0 )
        
        self.currentDirEntry = Tkinter.Entry(self.jobMonitor, width = 110)
        self.currentDirEntry.grid(row = rowActual, column = 1, columnspan = 5)
        
        self.currentDirEntry.configure(state = "readonly")
                
        colActual = 21
#        rowActual = 21
        rowActual = 4
        
        directoryViewLabel = Tkinter.Label(self.jobMonitor, text = "Local commands:")
        directoryViewLabel.grid( row = rowActual, column = 21 , columnspan = 2)
        
        rowActual += 1
        
        for i in range( self.customButtonsLocalNo):
            if rowActual == 11:
                rowActual += 1
            newButton = Tkinter.Button( self.jobMonitor, width = 15, height = 1 ,command = lambda arg = i : self.customButtonCommandLocal(arg), bg = "green" )
            newButton.grid(row = rowActual, column = colActual, columnspan =2)
            newButton.bind("<Button-3>", lambda e, arg = i:self.customButtonLocalSet(e, arg))
            self.customButtonsLocal.append(newButton)
            self.customButtonsLocalData.append({})
            rowActual += 1
            
        
        
    def customButtonCommand(self, buttonInd):
        if not self.connected:
            tkMessageBox.showwarning(title = "Cannot execute", message = "You have to connect to host before command execution")
            return
        
        if not "command" in self.customButtonsData[buttonInd]:
            tkMessageBox.showwarning(title = "Cannot execute", message = "No command for this button")
            return
        
        if not self.customButtonsData[buttonInd]["command"]:
            tkMessageBox.showwarning(title = "Cannot execute", message = "No command for this button")
            return
        
        command2execute = self.customButtonsData[buttonInd]["command"]

        if self.currentDir == "" :
            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select directory")
            return
        
        dir2go = self.currentDir
        
        fileSelection = self.directoryViewList.curselection()
        
        if not fileSelection:
            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select file to execute")
            return
        
        fileSelection = self.directoryViewList.get(fileSelection)
        command2execute = command2execute.replace( "$1", fileSelection )
        stdin, stdout, stderr = self.client.exec_command("cd "+dir2go + " ; " + command2execute )
        
        output = "".join(list(stdout.readlines()))
        
        self.outputText.delete("1.0", "end")
        self.outputText.insert("end", output)
        
    def customButtonCommandLocal(self, buttonInd):
        if not "command" in self.customButtonsLocalData[buttonInd]:
            tkMessageBox.showwarning(title = "Cannot execute", message = "No command for this button")
            return
        
        if not self.customButtonsLocalData[buttonInd]["command"]:
            tkMessageBox.showwarning(title = "Cannot execute", message = "No command for this button")
            return
        
        command2execute = self.customButtonsLocalData[buttonInd]["command"]
        exec(command2execute)
        
        
    def customButtonSet(self, event, buttonInd):
        initialName = ""
        initialCommand = ""
        
        if "text" in self.customButtonsData[buttonInd]:
            initialName =  self.customButtonsData[buttonInd]["text"]
        
        if "command" in self.customButtonsData[buttonInd]:
            initialCommand  = self.customButtonsData[buttonInd]["command"]
        
        commDial = CommandDialog(self.jobMonitor, initialName, initialCommand)
        newButtonName, newButtonCommand = commDial.results
        
        self.customButtons[buttonInd].config(text = newButtonName)
        self.customButtonsData[buttonInd]["text"] = newButtonName
    
        self.customButtonsData[buttonInd]["command"] = newButtonCommand
        
        state = self.getState()
        with open(self.configFile, 'w') as fp:
            json.dump(state, fp)
            
    def customButtonLocalSet(self, event, buttonInd):
        initialName = ""
        initialCommand = ""
        
        if "text" in self.customButtonsLocalData[buttonInd]:
            initialName = self.customButtonsLocalData[buttonInd]["text"]
 
        
        if "command" in self.customButtonsLocalData[buttonInd]:
            initialCommand = self.customButtonsLocalData[buttonInd]["command"]

        
        commDial = CommandDialog(self.jobMonitor, initialName, initialCommand)
        newButtonName, newButtonCommand = commDial.results
        
        self.customButtonsLocal[buttonInd].config(text = newButtonName)
        self.customButtonsLocalData[buttonInd]["text"] = newButtonName
        
        self.customButtonsLocalData[buttonInd]["command"] = newButtonCommand
        
        state = self.getState()
        with open(self.configFile, 'w') as fp:
            json.dump(state, fp)
        
    def setDir(self, event):
        item = self.tree_data.identify_row(event.y)
        
        if item:
            info = self.tree_data.item(item, 'values')
            self.currentSelectionTree = info
            
            if self.connected:
                dir2print = info[1]
                self.currentDir = dir2print
                
                self.currentDirEntry.configure(state = "normal")
                self.currentDirEntry.delete(0, "end")
                self.currentDirEntry.insert(0, self.currentDir)
                self.currentDirEntry.configure(state = "readonly")
                
                stdin, stdout, stderr = self.client.exec_command("ls -p "+dir2print)
                filesList = list(stdout.readlines())
                
                self.directoryViewList.delete(0, "end")
                for filename in filesList:
                    self.directoryViewList.insert("end", filename.strip())
                    
                self.directoryViewList.insert("end", "../")
                    
                self.outputText.delete("1.0", "end")
                
    def enterAndSetDir(self, event):
        dirSelection = self.directoryViewList.curselection()
        
        if not dirSelection:
            tkMessageBox.showwarning(title = "Cannot enter directory!", message = "There is no directory selected")
            return
        
        dirSelection = self.directoryViewList.get(dirSelection)
        if dirSelection[-1] != "/":
            tkMessageBox.showwarning(title = "Cannot enter directory!", message = "This is not a directory")
            return
        
        self.currentDir = normpath( join(self.currentDir, dirSelection))
        self.currentDirEntry.configure(state = "normal")
        self.currentDirEntry.delete(0, "end")
        self.currentDirEntry.insert(0, self.currentDir)
        self.currentDirEntry.configure(state = "readonly")
        self.refreshDirectoryView()
        
    def getStatus(self):
        if not self.connected:
            tkMessageBox.showwarning(title = "Cannot get status!", message = "You have to be connected with host to get actual status")
            
        jobManagerDir = self.jobManagerDirEntry.get()
        if jobManagerDir[-1] != "/":
            jobManagerDir += "/"
        
        command = " python " + jobManagerDir + "squeuePy.py -json"
        
        stdin, stdout, stderr = self.client.exec_command(command)
        
        result = list(stdout.readlines())
        result = " ".join(result)
        result = result.replace("'", '"')
        status = json.loads( result )
        
        self.actualStatus = status
        
        self.tree_data.delete(*self.tree_data.get_children())
        self.directoryViewList.delete(0, "end")
        self.outputText.delete("1.0", "end")
        
        for mainKey in status:
            resultList = status[mainKey]
            for row in resultList:
                tableRow = ( row["jobID"] , row["RunningDir"], row["Script file"], row["Status"], row["Time"], row["Comment"] )
                self.tree_data.insert('', "end" , values = tableRow  )
                
    def filterJobs(self):
        filterKey = self.filterEntry.get()
        
        self.tree_data.delete(*self.tree_data.get_children())
        self.directoryViewList.delete(0, "end")
        self.outputText.delete("1.0", "end")
        
        for mainKey in self.actualStatus:
            resultList = self.actualStatus[mainKey]
            for row in resultList:
                stringRow = row["jobID"] + row["RunningDir"] + row["Script file"] + row["Comment"]
                if filterKey in stringRow:
                    tableRow = ( row["jobID"] , row["RunningDir"], row["Script file"], row["Status"], row["Time"], row["Comment"] )
                    self.tree_data.insert('', "end" , values = tableRow  )
                
    def scancel(self):
        if not self.connected:
            tkMessageBox.showwarning(title = "Cannot scancel!", message = "You have to be connected with host to cancel job")
            
        currentSel = self.tree_data.focus()
        if currentSel == "" :
            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select job")
            return
        
        jobID = self.tree_data.item(currentSel)["values"][0]
            
        jobManagerDir = self.jobManagerDirEntry.get()
        if jobManagerDir[-1] != "/":
            jobManagerDir += "/"
        
        command = "scancel " + str(jobID)
        
        stdin, stdout, stderr = self.client.exec_command(command)
    
    def sremovePy(self):
        if not self.connected:
            tkMessageBox.showwarning(title = "Cannot forget!", message = "You have to be connected with host to forget job")
            
        currentSel = self.tree_data.focus()
        if currentSel == "" :
            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select job")
            return
        
        jobID = self.tree_data.item(currentSel)["values"][0]
            
        jobManagerDir = self.jobManagerDirEntry.get()
        if jobManagerDir[-1] != "/":
            jobManagerDir += "/"
        
        command =  " python " + jobManagerDir + "sremove.py " + str(jobID)
        
        stdin, stdout, stderr = self.client.exec_command(command)
        
        item2forget = self.tree_data.selection()[0]
        self.tree_data.delete(item2forget)
    
    def refreshDirectoryView(self):
        if not self.connected:
            tkMessageBox.showwarning(title = "Cannot execute!", message = "You have to be connected with host")
            
#        currentSel = self.tree_data.focus()
#        if currentSel == "" :
#            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select row")
#            return
#        
#        item = self.tree_data.focus()
#        info = self.tree_data.item(item, 'values')
#        self.currentSelectionTree = info
        
#        if self.connected:
        if self.currentDir:
            dir2print = self.currentDir
            
            stdin, stdout, stderr = self.client.exec_command("ls -p "+dir2print)
            filesList = list(stdout.readlines())
            
            self.directoryViewList.delete(0, "end")
            
            for filename in filesList:
                self.directoryViewList.insert("end", filename.strip())
            self.directoryViewList.insert("end", "../")
                
            self.outputText.delete("1.0", "end")
    
    def downloadFile(self):
        if not self.connected:
            tkMessageBox.showwarning(title = "Cannot execute", message = "You have to connect to host before command execution")
            return
        
        if self.currentDir == "" :
            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select directory")
            return
        
        dir2go = self.currentDir
        
        fileSelection = self.directoryViewList.curselection()
        
        if not fileSelection:
            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select file to execute")
            return
        
        fileSelection = self.directoryViewList.get(fileSelection)
        
        fullPath = join(dir2go, fileSelection)
        
        sftp = self.client.open_sftp()
        
        sftp.get(fullPath, fileSelection)
        
        sftp.close()
    
    def downloadAndLoadToPymol(self):
        if not self.connected:
            tkMessageBox.showwarning(title = "Cannot execute", message = "You have to connect to host before command execution")
            return
        
        if self.currentDir == "" :
            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select directory")
            return
        
        dir2go = self.currentDir
        
        fileSelection = self.directoryViewList.curselection()
        
        if not fileSelection:
            tkMessageBox.showwarning(title = "Cannot execute", message = "Please select file to execute")
            return
        
        fileSelection = self.directoryViewList.get(fileSelection)
        
        fullPath = join(dir2go, fileSelection)
        
        sftp = self.client.open_sftp()
        
        sftp.get(fullPath, fileSelection)
        
        sftp.close()
        cmd.load(fileSelection)
    
    def gridLoginData(self):
        loginLabel = Tkinter.Label(self.loginData, text = "login")
        loginLabel.grid(row = 0, column = 0)
        
        self.loginEntry = Tkinter.Entry(self.loginData, width = 20)
        self.loginEntry.grid(row = 0, column = 1)
        
        hostLabel = Tkinter.Label(self.loginData, text = "host")
        hostLabel.grid(row= 1, column = 0)
        
        self.hostEntry = Tkinter.Entry(self.loginData, width = 20)
        self.hostEntry.grid(row = 1, column = 1)
        
        portLabel = Tkinter.Label(self.loginData, text = "port")
        portLabel.grid(row = 2, column = 0)
        
        self.portEntry = Tkinter.Entry(self.loginData, width = 20)
        self.portEntry.grid(row = 2, column = 1)
        self.portEntry.insert(0, "22")
        
        passwordLabel = Tkinter.Label(self.loginData, text = "password")
        passwordLabel.grid(row = 3, column =0)
        
        self.passwordEntry = Tkinter.Entry(self.loginData, width = 20)
        self.passwordEntry.grid(row = 3, column = 1)
        
        jobManagerDirLabel = Tkinter.Label(self.loginData, text = "JobManagerPro dir")
        jobManagerDirLabel.grid(row = 4, column  = 0)
        
        self.jobManagerDirEntry = Tkinter.Entry(self.loginData, width = 20)
        self.jobManagerDirEntry.grid( row = 4, column = 1 )
        
        connectButton = Tkinter.Button(self.loginData, width = 20, text = "Connect", command = self.connect)
        connectButton.grid(row = 5, column = 0)
        
        disconnectButton = Tkinter.Button(self.loginData, width = 20, text = "Disconnect", command = self.disconnect)
        disconnectButton.grid(row = 5, column = 1)
        
        statusLabel = Tkinter.Label(self.loginData, text = "Status")
        statusLabel.grid(row = 6, column = 0)
        
        self.statusEntry = Tkinter.Entry(self.loginData, width = 20)
        self.statusEntry.grid(row = 6, column = 1)
        
        self.statusEntry.insert(0, "Disconnected")
        self.statusEntry.configure(state = "readonly")
        
        downloadLabel = Tkinter.Label(self.loginData, text = "Download dir")
        downloadLabel.grid(row = 7, column = 0)
        
        downloadDirButton = Tkinter.Button(self.loginData, text = "Change", width = 20, command = self.changeDownloadDir)
        downloadDirButton.grid(row = 7, column = 1)
        
        self.downloadEntry = Tkinter.Entry(self.loginData, width = 60)
        self.downloadEntry.grid(row = 8, column = 0, columnspan = 3)
        self.downloadEntry.configure(state = "readonly")
        
    def changeDownloadDir(self):
        newDir =  tkFileDialog.askdirectory()
        if not newDir:
            return
        
        self.downloadEntry.configure(state = "normal")
        self.downloadEntry.delete(0, "end")
        self.downloadEntry.insert("end", newDir)
        self.downloadEntry.configure(state = "readonly")
    
    def connect(self):
        host = self.hostEntry.get()
        login = self.loginEntry.get()
        port =  int(self.portEntry.get())
        password = self.passwordEntry.get()
        
        try:
            self.client.connect(host, port=port , username=login, password=password)
            
            self.statusEntry.configure(state = "normal")
            self.statusEntry.delete(0, "end")
            self.statusEntry.insert(0, "Connected")
            self.statusEntry.configure(state = "readonly")
            self.connected = True
        except:
            tkMessageBox.showwarning(title = "Connection error!", message = "Cannot connect to host! Please check login, password and internet connection")
    
    def disconnect(self):
        if self.connected:
            self.client.close()
            
            self.statusEntry.configure(state = "normal")
            self.statusEntry.delete(0, "end")
            self.statusEntry.insert(0, "Disconnected")
            self.statusEntry.configure(state = "readonly")
            self.connected = False
    
    def getState(self):
        state = {}
        
        state["login"] = self.loginEntry.get()
        state["host"] = self.hostEntry.get()
        state["port"] = self.portEntry.get()
        state["jobManagerDir"] = self.jobManagerDirEntry.get()
        state["password"] = self.passwordEntry.get()
        state["customButtons"] = self.customButtonsData
        state["customButtonsLocal"] = self.customButtonsLocalData
        state["downloadDir"] = self.downloadEntry.get()
        
        return state
    
    def loadState(self, state):
        self.loginEntry.delete(0, "end")
        self.loginEntry.insert(0, state["login"])
        
        self.hostEntry.delete(0, "end")
        self.hostEntry.insert(0, state["host"])
        
        self.portEntry.delete(0, "end")
        self.portEntry.insert(0, state["port"])
        
        self.passwordEntry.delete(0, "end")
        self.passwordEntry.insert(0, state["password"])
        
        self.jobManagerDirEntry.delete(0, "end")
        self.jobManagerDirEntry.insert(0, state["jobManagerDir"])
        
        if "customButtons" in state:
            self.customButtonsData = state["customButtons"]
            self.refreshCustomButtons()
            
        if "customButtonsLocal" in state:
            self.customButtonsLocalData = state["customButtonsLocal"]
            self.refreshCustomButtonsLocal() 
            
        if "downloadDir" in state:
            self.downloadEntry.configure(state = "normal")
            self.downloadEntry.delete(0, "end")
            self.downloadEntry.insert("end", state["downloadDir"])
            self.downloadEntry.configure(state = "readonly")

    def refreshCustomButtons(self):
        for i, data in enumerate(self.customButtonsData):
            if "text" in data:
                self.customButtons[i].config(text = data["text"])
                
        lenDiff = len(self.customButtons) - len(self.customButtonsData)
        if lenDiff > 0:
            for i in range(lenDiff):
                self.customButtonsData.append({})
                
    def refreshCustomButtonsLocal(self):
        for i, data in enumerate(self.customButtonsLocalData):
            if "text" in data:
                self.customButtonsLocal[i].config(text = data["text"])
                
        lenDiff = len(self.customButtonsLocal) - len(self.customButtonsLocalData)
        if lenDiff > 0:
            for i in range(lenDiff):
                self.customButtonsLocalData.append({})

    def grid(self):
        self.gridJobMonitor()
        self.gridLoginData()