"""Provide a class for FreeMind file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET
from pywriter.pywriter_globals import *
from pywriter.yw.yw7_file import Yw7File
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene
from pywriter.model.character import Character
from pywriter.model.world_element import WorldElement
from mm2yw7lib.mm_node import MmNode


class MmFile(Yw7File):
    """File representation of a Freemind mindmap. 

    Represents a mm file containing an outline according to the conventions.
    """
    EXTENSION = '.mm'
    DESCRIPTION = 'Mindmap'
    SUFFIX = ''

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables and MmNode class variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            locations_icon -- str: Icon that marks the locations in FreeMind.
            items_icon -- str: Icon that marks the items in FreeMind.
            characters_icon -- str: Icon that marks the major racters in FreeMind.
            export_scenes -- bool: if True, create scenes from FreeMind notes.
            export_characters -- bool: if True, create characters from FreeMind notes.
            export_locations -- bool: if True, create location from FreeMind notes. 
            export_items -- bool: if True, create items from FreeMind notes. 
        
        Extends the superclass constructor.
        """
        MmNode.locationIcon = kwargs['locations_icon']
        MmNode.itemIcon = kwargs['items_icon']
        MmNode.characterIcon = kwargs['characters_icon']
        super().__init__(filePath, **kwargs)
        self._exportScenes = kwargs['export_scenes']
        self._exportCharacters = kwargs['export_characters']
        self._exportLocations = kwargs['export_locations']
        self._exportItems = kwargs['export_items']

    def read(self):
        """Parse the FreeMind xml file, fetching the Novel attributes.
        
        Create an object structure of FreeMind notes.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        try:
            self._tree = ET.parse(self.filePath)
        except:
            return f'{ERROR}Can not process "{os.path.normpath(self.filePath)}".'
        root = self._tree.getroot()

        #--- Create a single chapter and assign all scenes to it.
        chId = '1'
        self.chapters[chId] = Chapter()
        self.chapters[chId].title = 'Chapter 1'
        self.srtChapters = [chId]

        #--- Parse FreeMind notes.
        mmNodes = {}
        uidByPos = {}
        for xmlNode in root.iter('node'):
            node = MmNode()
            node.parse_xml(xmlNode)
            mmNodes[node.uid] = node
            uidByPos[node.position] = node.uid

            # Create Novel elements.
            if node.isScene:
                if self._exportScenes:
                    scene = Scene()
                    scene.title = node.text
                    scene.isNotesScene = node.isNotesScene
                    scene.status = 1
                    # Status = Outline
                    self.scenes[node.uid] = scene
            elif node.isCharacter:
                if self._exportCharacters:
                    character = Character()
                    character.title = node.text
                    character.fullName = node.text
                    character.isMajor = True
                    self.characters[node.uid] = character
                    self.srtCharacters.append(node.uid)
            elif node.isLocation:
                if self._exportLocations:
                    location = WorldElement()
                    location.title = node.text
                    self.locations[node.uid] = location
                    self.srtLocations.append(node.uid)
            elif node.isItem:
                if self._exportItems:
                    item = WorldElement()
                    item.title = node.text
                    self.items[node.uid] = item
                    self.srtItems.append(node.uid)

        #--- Sort notes by position.
        srtNotes = sorted(uidByPos.items())
        for srtNote in srtNotes:
            if srtNote[1] in self.scenes:
                self.chapters[chId].srtScenes.append(srtNote[1])

        #--- Assign characters/locations/items/tags/notes to the scenes.
        for scId in self.scenes:
            self.scenes[scId].characters = []
            self.scenes[scId].locations = []
            self.scenes[scId].items = []
            self.scenes[scId].tags = []
            self.scenes[scId].sceneNotes = ''
            for uid in mmNodes[scId].connections:
                if uid in self.characters:
                    if scId in mmNodes[uid].pointTo:
                        self.scenes[scId].characters.insert(0, uid)
                    else:
                        self.scenes[scId].characters.append(uid)
                elif uid in self.locations:
                    self.scenes[scId].locations.append(uid)
                elif uid in self.items:
                    self.scenes[scId].items.append(uid)
                elif mmNodes[uid].isTag:
                    self.scenes[scId].tags.append(mmNodes[uid].text)
                elif mmNodes[uid].isNote:
                    self.scenes[scId].sceneNotes = f'{self.scenes[scId].sceneNotes}{mmNodes[uid].text}'

        #--- Assign tags/notes to the characters.
        for crId in self.characters:
            self.characters[crId].tags = []
            self.characters[crId].notes = ''
            for uid in mmNodes[crId].connections:
                if mmNodes[uid].isTag:
                    self.characters[crId].tags.append(mmNodes[uid].text)
                elif mmNodes[uid].isNote:
                    self.characters[crId].notes = f'{self.characters[crId].notes}{mmNodes[uid].text}'

        #--- Assign tags to the locations.
        for lcId in self.locations:
            self.locations[lcId].tags = []
            for uid in mmNodes[lcId].connections:
                if mmNodes[uid].isTag:
                    self.locations[lcId].tags.append(mmNodes[uid].text)

        #--- Assign tags to the items.
        for itId in self.items:
            self.items[itId].tags = []
            for uid in mmNodes[itId].connections:
                if mmNodes[uid].isTag:
                    self.items[itId].tags.append(mmNodes[uid].text)
        return 'Mindmap converted to novel structure.'
