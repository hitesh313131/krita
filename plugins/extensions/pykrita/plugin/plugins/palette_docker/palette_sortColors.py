'''
A script that sorts the colors in the group.
By Wolthera.
'''


# Importing the relevant dependancies:
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math
from krita import *


class sortColors:
    def __init__(self, name):
        # We want people to select a palette...
        allPalettes = Application.resources("palette")
        self.paletteName = name
        self.currentPalette = Palette(allPalettes[self.paletteName])
        self.sort_all_groups()

    def sort_all_groups(self):
        self.sort_color_by_name(str())
        groupNames = self.currentPalette.groupNames()
        for groupName in groupNames:
            self.sort_color_by_name(groupName)

    def sort_color_by_name(self, groupName):
        l={}
        colorCount = self.currentPalette.colorsCountGroup(groupName)
        for i in range(colorCount-1, -1, -1):
            entry = self.currentPalette.colorSetEntryFromGroup((i), groupName)
            l[entry.name+str(i)] = entry
            self.currentPalette.removeEntry((i), groupName)
            
        for s in sorted(l):
            self.currentPalette.addEntry(l[s], groupName)

    def sort_color_by_id(self, groupName):
        l={}
        colorCount = self.currentPalette.colorsCountGroup(groupName)
        for i in range(colorCount-1, -1, -1):
            entry = self.currentPalette.colorSetEntryFromGroup((i), groupName)
            l[entry.id+" "+str(i)] = entry
            self.currentPalette.removeEntry((i), groupName)
            
        for s in sorted(l):
            self.currentPalette.addEntry(l[s], groupName)
    
    def sort_by_value(self, groupName):
        l={}
        colorCount = self.currentPalette.colorsCountGroup(groupName)
        for i in range(colorCount-1, -1, -1):
            entry = self.currentPalette.colorSetEntryFromGroup((i), groupName)
            color = self.currentPalette.colorForEntry(entry)
            color.setColorSpace("RGBA", "U8", "sRGB built-in")
            l[color.components()[0]+color.components()[1]+color.components()[2]] = entry
            self.currentPalette.removeEntry((i), groupName)
            
        for s in sorted(l):
            self.currentPalette.addEntry(l[s], groupName)
    
    def sort_by_hue(self, stepsize, groupName):
        pass

    def palette(self):
        return self.currentPalette
