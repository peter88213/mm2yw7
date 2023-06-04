"""Provide a class for FreeMind file representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import xml.etree.ElementTree as ET
from pywriter.pywriter_globals import *
from pywriter.file.file import File
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene
from pywriter.model.character import Character
from pywriter.model.world_element import WorldElement
from pywriter.model.id_generator import create_id


class MmFile(File):
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
        super().__init__(filePath, **kwargs)
        self._locationIcon = kwargs['locations_icon']
        self._itemIcon = kwargs['items_icon']
        self._characterIcon = kwargs['characters_icon']
        self._notesIcon = kwargs['notes_icon']
        self._todoIcon = kwargs['todo_icon']
        self._exportScenes = kwargs['export_scenes']
        self._exportCharacters = kwargs['export_characters']
        self._exportLocations = kwargs['export_locations']
        self._exportItems = kwargs['export_items']

    def read(self):
        """Parse the FreeMind xml file, fetching the Novel attributes.
        
        Overrides the superclass method.
        """
        try:
            self._tree = ET.parse(self.filePath)
        except:
            return f'{ERROR}Can not process "{os.path.normpath(self.filePath)}".'

        root = self._tree.getroot()
        xmlNovel = root.find('node')
        self.novel.title = self._get_title(xmlNovel)
        self.novel.desc = self._get_desc(xmlNovel)
        for xmlNode in xmlNovel.findall('node'):
            isCharactersNode = False
            isLocationsNode = False
            isItemsNode = False
            for xmlIcon in xmlNode.findall('icon'):
                if xmlIcon.attrib.get('BUILTIN', '') == self._characterIcon:
                    isCharactersNode = True
                    break

                elif xmlIcon.attrib.get('BUILTIN', '') == self._locationIcon:
                    isLocationsNode = True
                    break

                elif xmlIcon.attrib.get('BUILTIN', '') == self._itemIcon:
                    isItemsNode = True
                    break

            if isCharactersNode:
                if self._exportCharacters:
                    self._get_characters(xmlNode)
            elif isLocationsNode:
                if self._exportLocations:
                    self._get_locations(xmlNode)
            elif isItemsNode:
                if self._exportItems:
                    self._get_items(xmlNode)
            elif self._exportScenes:
                self._get_part(xmlNode)

    def _get_characters(self, xmlNode):
        for xmlCharacter in xmlNode.findall('node'):
            crId = create_id(self.novel.characters)
            self.novel.characters[crId] = Character()
            self.novel.srtCharacters.append(crId)
            self.novel.characters[crId].title = self._get_title(xmlCharacter)
            self.novel.characters[crId].desc = self._get_desc(xmlCharacter)

    def _get_desc(self, xmlNode):
        desc = None
        for xmlRichcontent in xmlNode.findall('richcontent'):
            if xmlRichcontent.attrib.get('TYPE', '') == 'NOTE':
                htmlDesc = []
                for htmlText in xmlRichcontent.itertext():
                    htmlDesc.append(htmlText)
                desc = ''.join(htmlDesc).strip()
                break
        return desc

    def _get_items(self, xmlNode):
        for xmlItem in xmlNode.findall('node'):
            itId = create_id(self.novel.items)
            self.novel.items[itId] = WorldElement()
            self.novel.srtItems.append(itId)
            self.novel.items[itId].title = self._get_title(xmlItem)
            self.novel.items[itId].desc = self._get_desc(xmlItem)

    def _get_locations(self, xmlNode):
        for xmlLocation in xmlNode.findall('node'):
            lcId = create_id(self.novel.locations)
            self.novel.locations[lcId] = WorldElement()
            self.novel.srtLocations.append(lcId)
            self.novel.locations[lcId].title = self._get_title(xmlLocation)
            self.novel.locations[lcId].desc = self._get_desc(xmlLocation)

    def _get_part(self, xmlNode):
        paId = create_id(self.novel.chapters)
        self.novel.chapters[paId] = Chapter()
        self.novel.srtChapters.append(paId)
        self.novel.chapters[paId].chLevel = 1
        self.novel.chapters[paId].title = self._get_title(xmlNode)
        self.novel.chapters[paId].desc = self._get_desc(xmlNode)
        self.novel.chapters[paId].chType = self._get_type(xmlNode)
        for xmlChapter in xmlNode.findall('node'):
            chId = create_id(self.novel.chapters)
            self.novel.chapters[chId] = Chapter()
            self.novel.srtChapters.append(chId)
            self.novel.chapters[chId].chLevel = 0
            self.novel.chapters[chId].title = self._get_title(xmlChapter)
            self.novel.chapters[chId].desc = self._get_desc(xmlChapter)
            if self.novel.chapters[paId].chType != 0:
                self.novel.chapters[chId].chType = self.novel.chapters[paId].chType
            else:
                self.novel.chapters[chId].chType = self._get_type(xmlChapter)
            for xmlScene in xmlChapter.findall('node'):
                scId = create_id(self.novel.scenes)
                self.novel.scenes[scId] = Scene()
                self.novel.chapters[chId].srtScenes.append(scId)
                self.novel.scenes[scId].title = self._get_title(xmlScene)
                self.novel.scenes[scId].desc = self._get_desc(xmlScene)
                self.novel.scenes[scId].status = 1
                if self.novel.chapters[chId].chType != 0:
                    self.novel.scenes[scId].scType = self.novel.chapters[chId].chType
                else:
                    self.novel.scenes[scId].scType = self._get_type(xmlScene)

    def _get_title(self, xmlNode):
        title = xmlNode.attrib.get('TEXT', None)
        if title is None:
            for xmlRichcontent in xmlNode.findall('richcontent'):
                if xmlRichcontent.attrib.get('TYPE', '') == 'NODE':
                    htmlTitle = []
                    for htmlText in xmlRichcontent.itertext():
                        htmlTitle.append(htmlText)
                    title = ''.join(htmlTitle).strip()
                    break
        return title

    def _get_type(self, xmlNode):
        type = 0
        for xmlIcon in xmlNode.findall('icon'):
            if xmlIcon.attrib.get('BUILTIN', '') == self._notesIcon:
                type = 1
                break

            elif xmlIcon.attrib.get('BUILTIN', '') == self._todoIcon:
                type = 2
                break

        return type
