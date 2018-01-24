# import the necessary packages
import numpy as np
import pygame
import os
import label_image
import re
import csv
import cv2
import argparse
import sys
from tkinter import *
import tkinter.messagebox
import tkinter.colorchooser
from tkinter.filedialog import askdirectory
import time, threading

from PIL import ImageTk, Image


def main(folderPath):
    myFolder = folderPath

    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", help="folder to be processed")

    args = parser.parse_args()

    if args.folder:
        myFolder = args.folder

    #Variables
    currentX = 0
    currentY = 0

    maxWidth = 0
    maxHeight = 0
    minWidth = 0
    minHeight = 0

    #Aux Functions
    class Point:
        def __init__(self,x,y,label,imgName,radius):
            self.x = x
            self.y = y
            self.label = label
            self.imgName = imgName
            self.clicked = False
            self.radius = radius

        def show(self):
            print("Circle :)")


    resultInfo = []
    try:
        resultFile = open(os.path.join(myFolder, "results.txt"), "r")
        reader = csv.reader(resultFile, skipinitialspace=True)
        for r in reader:
            resultInfo.append(r)

    finally:
        resultFile.close()

    global drawnList
    global pointList

    pointList = []
    for record in resultInfo:
        currentX = int(record[3])
        currentY = int(record[2])
        if currentX > maxWidth:
            maxWidth = currentX

        if currentX < minWidth:
            minWidth = currentX

        if currentY > maxHeight:
            maxHeight = currentY

        if currentY < minHeight:
            minHeight = currentY

        pointList.append(Point(currentX, currentY, record[1], record[0], 1))

    #Make the labels set
    labelSet = set()
    for point in pointList:
        labelSet.add(point.label)
    #Make the labels list
    labelsList = []
    for element in labelSet:
        labelsList.append(element)

    global labelsAndColors
    labelsAndColors = {key: "gray" for key in labelsList}


    #Spacing phase
    for point in pointList:
        point.x *= 4
        point.y *= 4


    globRadius = 20
    #Translation phase
    for point in pointList:
        point.x += abs(minWidth) + 4
        point.y += abs(minHeight) + 4

    #Scaling phase
    for point in pointList:
        point.x *= globRadius
        point.y *= globRadius
        point.radius = globRadius

    def closeAll():
        root.destroy()
        exit()



    #Starting GUI interface
    root = Tk()
    windowName = "GraffX -- " + myFolder
    root.winfo_toplevel().title(windowName)
    root.geometry("700x600")
    root.configure(background="#404040")
    root.protocol('WM_DELETE_WINDOW', closeAll)

    selectedObject = None

    #Function Definitions
    def doNothing():
        print("lul")

    def doSomething(x):
        print(x)

    def getColor(event):
        global labelsAndColors
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        #print(value)
        color = tkinter.colorchooser.askcolor()
        #print(color[1])
        labelsAndColors[value] = color[1]


    def colorDialog():
        popup = Tk()
        popup.geometry("400x300")

        def leaveWindow():
            #print(labelsAndColors)
            #canv.delete("all")
            #drawPoints(drawnList)
            #displayText()
            popup.destroy()

        popup.wm_title("Label colors")
        labelList = Label(popup, text="Choose color for label:")
        labelList.pack(side=TOP, fill=X, anchor="w")

        selectColorList = Listbox(popup, fg="#cdcdcd", bg="#333333",  bd=3, highlightcolor="#404040", relief=SUNKEN, selectbackground="#404040", selectmode="SINGLE")
        lList = [x[0] for x in resultInfo]
        colList = [x[1] for x in resultInfo]
        for label in labelsList:
            selectColorList.insert(END, label)

        selectColorList.pack(side=TOP, fill=BOTH)
        selectColorList.bind('<<ListboxSelect>>', getColor)

        b1 = Button(popup, text="OK", anchor="w", command=leaveWindow)
        b1.pack(side=BOTTOM, fill=X, anchor="e")
        popup.mainloop()


    def popupRight(event):
        try:
            popup_menu.tk_popup(event.x_root+3*globRadius, event.y_root+globRadius, 0)
        finally:
            popup_menu.grab_release()

    def delete_selected():
        print("deleted")

    def getLabel(event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        global selectedObject
        try:
            selectedObject
        except NameError:
            print("chill")
        else:
            item = selectedObject
            tagList = canv.gettags(item)
            for pic in resultInfo:
                if pic[0] == tagList[0]:
                    pic[1] = value
                    break
            newTags = (tagList[0], value)
            fillCol = labelsAndColors[value]
            canv.itemconfig(item, activeoutline="#dddddd", width = 2, tags=newTags, fill=fillCol)
            leftList.delete(0, END) #clear leftList
            nameList = [x[0] for x in resultInfo]
            lList = [x[1] for x in resultInfo]
            cnt = 0
            for x in nameList:
                listedName = []
                if x.endswith('.jpg'):
                    listedName = x[:-4]
                elif x.endswith('.jpeg'):
                    listedName = x[:-5]
                    #print(cnt)
                listedName = listedName + " - " + lList[cnt]
                leftList.insert(END, listedName)
                cnt += 1


    def changeLabel():
        popup = Tk()
        popup.geometry("400x300")

        def leaveWindow():
            #print(labelsAndColors)
            #canv.delete("all")
            #drawPoints(drawnList)
            #displayText()
            popup.destroy()

        popup.wm_title("Change label")
        labelList = Label(popup, text="Select the new label")
        labelList.pack(side=TOP, fill=X, anchor="w")

        changeLabelList = Listbox(popup, fg="#cdcdcd", bg="#333333",  bd=3, highlightcolor="#404040", relief=SUNKEN, selectbackground="#404040", selectmode="SINGLE")
        lList = [x[0] for x in resultInfo]
        colList = [x[1] for x in resultInfo]
        for label in labelsList:
            changeLabelList.insert(END, label)

        changeLabelList.pack(side=TOP, fill=BOTH)
        changeLabelList.bind('<<ListboxSelect>>', getLabel)

        b1 = Button(popup, text="OK", anchor="w", command=leaveWindow)
        b1.pack(side=BOTTOM, fill=X, anchor="e")

        popup.mainloop()



    def inspectPoint():
        global selectedObject
        try:
            selectedObject
        except NameError:
            print("chill")
        else:
            item = selectedObject
            tagList = canv.gettags(item)
            image = cv2.imread(os.path.join(myFolder, tagList[0]))
            cv2.imshow(tagList[0]+" - "+tagList[1], image)

    def rightClick(event):
        global selectedObject
        newx = canv.canvasx(event.x)
        newy = canv.canvasy(event.y)
        item = canv.find_closest(newx, newy)
        tags = canv.itemcget(item, "tags")
        item_type = canv.type(item)
        if item_type == "oval":
            if 'current' in tags:
                global selectedObject
                selectedObject = item
                tagList = canv.gettags(item)
                popupRight(event)

    def mouseMotion(event):
        newx = canv.canvasx(event.x)
        newy = canv.canvasy(event.y)
        item = canv.find_closest(newx, newy)
        tags = canv.itemcget(item, "tags")
        item_type = canv.type(item)
        statusText = ""

        if item_type == "oval":
            if 'current' in tags:
                tagList = canv.gettags(item)
                statusText = tagList[0]
        else:
            statusText = "Canvas"

        status.config(text=statusText)

    def periodicRefresh():
        cnt = 0
        for pic in resultInfo:
            global drawnList

            tags = canv.itemcget(drawnList[cnt], "tags")
            #print(tags)
            token = tags.split(' ')
            #print(token[1])
            #fillCol = labelsAndColors[tags[1]]
            fillCol = labelsAndColors[token[1]]
            if "current" in tags:
                pass
            else:
                if cv2.getWindowProperty(pic[0] + " - " + pic[1], 0) >= 0:
                    canv.itemconfig(drawnList[cnt], activeoutline="#dddddd", width = 6, tags=(pic[0], pic[1]), fill=fillCol)
                    #print("changed")
                    #print(pic[0]+" open")
                else:
                    canv.itemconfig(drawnList[cnt], activeoutline="#dddddd", width = 2, tags=(pic[0], pic[1]), fill=fillCol)
            cnt += 1
        #print("refresh")
        root.after(500, periodicRefresh)

    def refreshCanvas():
        #Update points
        cnt = 0
        for pic in resultInfo:
            global drawnList
            tags = canv.itemcget(drawnList[cnt], "tags")
            #print(tags)
            token = tags.split(' ')
            fillCol = labelsAndColors[token[1]]
            if cv2.getWindowProperty(pic[0] + " - " + pic[1], 0) >= 0:
                canv.itemconfig(drawnList[cnt], activeoutline="#dddddd", width = 6, tags=(pic[0], pic[1]), fill=fillCol)
                #print(pic[0]+" open")
            else:
                canv.itemconfig(drawnList[cnt], activeoutline="#dddddd", width = 2, tags=(pic[0], pic[1]), fill=fillCol)
            cnt += 1


    def doubleClick(event):

        newx = canv.canvasx(event.x)
        newy = canv.canvasy(event.y)
        item = canv.find_closest(newx, newy)
        tags = canv.itemcget(item, "tags")
        item_type = canv.type(item)

        if item_type == "oval":
            if 'current' in tags:
                global selectedObject
                selectedObject = item

                tagList = canv.gettags(item)
                #print("ja?")
                image = cv2.imread(os.path.join(myFolder, tagList[0]))
                cv2.imshow(tagList[0]+" - "+tagList[1], image)

        refreshCanvas()



    def loadOtherFolder():
        folder = askdirectory(initialdir='D:')

    def drawPoints(drawnList):
        #print(labelsAndColors)
        drawnList = []
        labelsAndColors
        myCol = ''
        for point in pointList:
            fillCol = labelsAndColors[point.label]
            #print(fillCol)
            circle = canv.create_oval(point.x, point.y, 2*globRadius+point.x, 2*globRadius+point.y, activeoutline="#dddddd", width = 2, tags=(point.imgName, point.label), fill=fillCol)
            drawnList.append(circle)
        return drawnList

    def displayText():
        for point in pointList:
            drawnText = point.imgName
            if drawnText.endswith('.jpg'):
                drawnText = drawnText[:-4]
            elif drawnText.endswith('.jpeg'):
                drawnText = drawnText[:-5]
            canv.create_text(point.x+globRadius, point.y+globRadius*2.5, text=drawnText, fill="#cdcdcd")

    def listSelect(event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        token = value.split(' ')
        image = cv2.imread(os.path.join(myFolder, token[0]+".jpeg"))
        cv2.imshow(token[0]+".jpeg"+" - "+token[1], image)

    def scroll_start(event):
        canv.scan_mark(event.x, event.y)

    def scroll_move(event):
        canv.scan_dragto(event.x, event.y, gain=1)

    #Dropdown Menu
    menu = Menu(root)
    root.config(menu=menu)

    #File menu
    subMenu = Menu(menu)
    subMenu = Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=subMenu)

    subMenu.add_command(label="Open Another Folder", command=loadOtherFolder)
    subMenu.add_command(label="Save", command=doNothing)
    subMenu.add_separator()
    subMenu.add_command(label="Exit", command=root.destroy)

    #Edit menu
    editMenu = Menu(menu)
    editMenu = Menu(menu, tearoff=0)
    menu.add_cascade(label="Edit", menu=editMenu)

    editMenu.add_command(label="Undo", command=doNothing, accelerator='Ctrl+Z')
    editMenu.add_command(label="Redo", command=doNothing, accelerator='Ctrl+Y')
    editMenu.add_separator()
    editMenu.add_command(label="Reset", command=doNothing)

    #Binding keyboard shortcut
    root.bind_all('<Control-Key-z>', doSomething)
    root.bind_all('<Control-Key-y>', doSomething)

    #Labels menu
    labelMenu = Menu(menu)
    labelMenu = Menu(menu, tearoff=0)
    menu.add_cascade(label="Labels", menu=labelMenu)

    labelMenu.add_command(label="Label colors", command=colorDialog)


    #Toolbar
    # toolbar = Frame(root, bg="#606060")
    #
    # viewButton1 = Button(toolbar, text="View pictures", command=doNothing)
    # viewButton1.pack(side=LEFT, padx=2, pady=2)
    # viewButton2 = Button(toolbar, text="View labels", command=doNothing)
    # viewButton2.pack(side=LEFT, padx=2, pady=2)
    #
    # toolbar.pack(side=TOP, fill=X)

    #StatusBar
    status = Label(root, text = "Waiting", fg="#cdcdcd", bg="#333333", bd=3, relief=SUNKEN, anchor=W)
    status.pack(side=BOTTOM, fill=X)

    #Left List
    leftList = Listbox(root, width=20, fg="#cdcdcd", bg="#333333", bd=3, highlightcolor="#404040", relief=SUNKEN, selectbackground="#404040", selectmode="SINGLE")
    nameList = [x[0] for x in resultInfo]
    lList = [x[1] for x in resultInfo]
    cnt = 0
    for x in nameList:
        listedName = []
        if x.endswith('.jpg'):
            listedName = x[:-4]
        elif x.endswith('.jpeg'):
            listedName = x[:-5]
            #print(cnt)
        listedName = listedName + " - " + lList[cnt]
        leftList.insert(END, listedName)
        cnt += 1
    leftList.pack(side=LEFT, fill=Y)
    leftList.bind('<<ListboxSelect>>', listSelect)

    #Canvas Frame
    canvasFrame = Frame(root)
    canvasFrame.pack(side=LEFT, expand=True, fill=BOTH)

    #Canvas
    canv = Canvas(canvasFrame, bg="#404040")
    canv.bind("<ButtonPress-1>", scroll_start)
    canv.bind("<B1-Motion>", scroll_move)
    ##Setup scrollBars
    # hbar = Scrollbar(canvasFrame,orient=HORIZONTAL)
    # hbar.pack(side=BOTTOM,fill=X)
    # hbar.config(command=canv.xview)
    # vbar = Scrollbar(canvasFrame,orient=VERTICAL)
    # vbar.pack(side=RIGHT,fill=Y)
    # vbar.config(command=canv.yview)
    # canv.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

    drawnList = []
    drawnList = drawPoints(drawnList)
    displayText()


    canv.pack(side=LEFT, expand=True, fill=BOTH)
    canv.bind('<Button-3>', rightClick)
    #canv.bind('<Double-1>', doubleClick)
    canv.bind('<Double-Button-1>', doubleClick)
    canv.bind('<Motion>', mouseMotion)

    popup_menu = Menu(tearoff=0)
    popup_menu.add_command(label="Inspect",
                            command=inspectPoint)
    popup_menu.add_command(label="Change label",
                            command=changeLabel)

    root.after(500, periodicRefresh)
    root.mainloop()




if __name__ == "__main__":
    main(sys.argv)
