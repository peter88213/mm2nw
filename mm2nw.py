#!/usr/bin/python3
"""Convert FreeMind to novelWriter

Version 0.1.2
Requires Python 3.6+
Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/mm2nw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import argparse
import os
import sys
import gettext
import locale

__all__ = ['Error',
           '_',
           'LOCALE_PATH',
           'CURRENT_LANGUAGE',
           'norm_path',
           'string_to_list',
           'list_to_string',
           ]


class Error(Exception):
    pass


LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('pywriter', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message


def norm_path(path):
    if path is None:
        path = ''
    return os.path.normpath(path)


def string_to_list(text, divider=';'):
    elements = []
    try:
        tempList = text.split(divider)
        for element in tempList:
            element = element.strip()
            if element and not element in elements:
                elements.append(element)
        return elements

    except:
        return []


def list_to_string(elements, divider=';'):
    try:
        text = divider.join(elements)
        return text

    except:
        return ''


class Ui:

    def __init__(self, title):
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        return True

    def set_info_how(self, message):
        if message.startswith('!'):
            message = f'FAIL: {message.split("!", maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def set_info_what(self, message):
        self.infoWhatText = message

    def show_warning(self, message):
        pass

    def start(self):
        pass


class UiCmd(Ui):

    def __init__(self, title):
        super().__init__(title)
        print(title)

    def ask_yes_no(self, text):
        result = input(f'{_("WARNING")}: {text} (y/n)')
        if result.lower() == 'y':
            return True
        else:
            return False

    def set_info_how(self, message):
        if message.startswith('!'):
            message = f'FAIL: {message.split("!", maxsplit=1)[1].strip()}'
        self.infoHowText = message
        print(message)

    def set_info_what(self, message):
        print(message)

    def show_warning(self, message):
        print(f'\nWARNING: {message}\n')


def open_document(document):
    try:
        os.startfile(norm_path(document))
    except:
        try:
            os.system('xdg-open "%s"' % norm_path(document))
        except:
            try:
                os.system('open "%s"' % norm_path(document))
            except:
                pass


import re
from typing import Iterator, Pattern


class BasicElement:

    def __init__(self):
        self.title: str = None

        self.desc: str = None

        self.kwVar: dict[str, str] = {}


class Chapter(BasicElement):

    def __init__(self):
        super().__init__()

        self.chLevel: int = None

        self.chType: int = None

        self.suppressChapterTitle: bool = None

        self.isTrash: bool = None

        self.suppressChapterBreak: bool = None

        self.srtScenes: list[str] = []


from typing import Pattern

ADDITIONAL_WORD_LIMITS: Pattern = re.compile('--|—|–')

NO_WORD_LIMITS: Pattern = re.compile('\[.+?\]|\/\*.+?\*\/|-|^\>', re.MULTILINE)

NON_LETTERS: Pattern = re.compile('\[.+?\]|\/\*.+?\*\/|\n|\r')


class Scene(BasicElement):
    STATUS: set = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')

    ACTION_MARKER: str = 'A'
    REACTION_MARKER: str = 'R'
    NULL_DATE: str = '0001-01-01'
    NULL_TIME: str = '00:00:00'

    def __init__(self):
        super().__init__()

        self._sceneContent: str = None

        self.wordCount: int = 0

        self.letterCount: int = 0

        self.scType: int = None

        self.doNotExport: bool = None

        self.status: int = None

        self.notes: str = None

        self.tags: list[str] = None

        self.field1: str = None

        self.field2: str = None

        self.field3: str = None

        self.field4: str = None

        self.appendToPrev: bool = None

        self.isReactionScene: bool = None

        self.isSubPlot: bool = None

        self.goal: str = None

        self.conflict: str = None

        self.outcome: str = None

        self.characters: list[str] = None

        self.locations: list[str] = None

        self.items: list[str] = None

        self.date: str = None

        self.time: str = None

        self.day: str = None

        self.lastsMinutes: str = None

        self.lastsHours: str = None

        self.lastsDays: str = None

        self.image: str = None

        self.scnArcs: str = None

        self.scnStyle: str = None

    @property
    def sceneContent(self) -> str:
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text: str):
        self._sceneContent = text
        text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
        text = NO_WORD_LIMITS.sub('', text)
        wordList = text.split()
        self.wordCount = len(wordList)
        text = NON_LETTERS.sub('', self._sceneContent)
        self.letterCount = len(text)


class WorldElement(BasicElement):

    def __init__(self):
        super().__init__()

        self.image: str = None

        self.tags: list[str] = None

        self.aka: str = None


class Character(WorldElement):
    MAJOR_MARKER: str = 'Major'
    MINOR_MARKER: str = 'Minor'

    def __init__(self):
        super().__init__()

        self.notes: str = None

        self.bio: str = None

        self.goals: str = None

        self.fullName: str = None

        self.isMajor: bool = None


LANGUAGE_TAG: Pattern = re.compile('\[lang=(.*?)\]')


class Novel(BasicElement):

    def __init__(self):
        super().__init__()

        self.authorName: str = None

        self.authorBio: str = None

        self.fieldTitle1: str = None

        self.fieldTitle2: str = None

        self.fieldTitle3: str = None

        self.fieldTitle4: str = None

        self.wordTarget: int = None

        self.wordCountStart: int = None

        self.wordTarget: int = None

        self.chapters: dict[str, Chapter] = {}

        self.scenes: dict[str, Scene] = {}

        self.languages: list[str] = None

        self.srtChapters: list[str] = []

        self.locations: dict[str, WorldElement] = {}

        self.srtLocations: list[str] = []

        self.items: dict[str, WorldElement] = {}

        self.srtItems: list[str] = []

        self.characters: dict[str, Character] = {}

        self.srtCharacters: list[str] = []

        self.projectNotes: dict[str, BasicElement] = {}

        self.srtPrjNotes: list[str] = []

        self.languageCode: str = None

        self.countryCode: str = None

    def get_languages(self):

        def languages(text: str) -> Iterator[str]:
            if text:
                m = LANGUAGE_TAG.search(text)
                while m:
                    text = text[m.span()[1]:]
                    yield m.group(1)
                    m = LANGUAGE_TAG.search(text)

        self.languages = []
        for scId in self.scenes:
            text = self.scenes[scId].sceneContent
            if text:
                for language in languages(text):
                    if not language in self.languages:
                        self.languages.append(language)

    def check_locale(self):
        if not self.languageCode:
            try:
                sysLng, sysCtr = locale.getlocale()[0].split('_')
            except:
                sysLng, sysCtr = locale.getdefaultlocale()[0].split('_')
            self.languageCode = sysLng
            self.countryCode = sysCtr
            return

        try:
            if len(self.languageCode) == 2:
                if len(self.countryCode) == 2:
                    return
        except:
            pass
        self.languageCode = 'zxx'
        self.countryCode = 'none'


class YwCnvUi:

    def __init__(self):
        self.ui = Ui('')
        self.newFile = None

    def export_from_yw(self, source, target):
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, norm_path(source.filePath), target.DESCRIPTION, norm_path(target.filePath)))
        try:
            self.check(source, target)
            source.novel = Novel()
            source.read()
            target.novel = source.novel
            target.write()
        except Exception as ex:
            message = f'!{str(ex)}'
            self.newFile = None
        else:
            message = f'{_("File written")}: "{norm_path(target.filePath)}".'
            self.newFile = target.filePath
        finally:
            self.ui.set_info_how(message)

    def create_yw7(self, source, target):
        self.ui.set_info_what(
            _('Create a yWriter project file from {0}\nNew project: "{1}"').format(source.DESCRIPTION, norm_path(target.filePath)))
        if os.path.isfile(target.filePath):
            self.ui.set_info_how(f'!{_("File already exists")}: "{norm_path(target.filePath)}".')
        else:
            try:
                self.check(source, target)
                source.novel = Novel()
                source.read()
                target.novel = source.novel
                target.write()
            except Exception as ex:
                message = f'!{str(ex)}'
                self.newFile = None
            else:
                message = f'{_("File written")}: "{norm_path(target.filePath)}".'
                self.newFile = target.filePath
            finally:
                self.ui.set_info_how(message)

    def import_to_yw(self, source, target):
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, norm_path(source.filePath), target.DESCRIPTION, norm_path(target.filePath)))
        self.newFile = None
        try:
            self.check(source, target)
            target.novel = Novel()
            target.read()
            source.novel = target.novel
            source.read()
            target.novel = source.novel
            target.write()
        except Exception as ex:
            message = f'!{str(ex)}'
        else:
            message = f'{_("File written")}: "{norm_path(target.filePath)}".'
            self.newFile = target.filePath
            if source.scenesSplit:
                self.ui.show_warning(_('New scenes created during conversion.'))
        finally:
            self.ui.set_info_how(message)

    def _confirm_overwrite(self, filePath):
        return self.ui.ask_yes_no(_('Overwrite existing file "{}"?').format(norm_path(filePath)))

    def _open_newFile(self):
        open_document(self.newFile)
        sys.exit(0)

    def check(self, source, target):
        if source.filePath is None:
            raise Error(f'{_("File type is not supported")}.')

        if not os.path.isfile(source.filePath):
            raise Error(f'{_("File not found")}: "{norm_path(source.filePath)}".')

        if target.filePath is None:
            raise Error(f'{_("File type is not supported")}.')

        if os.path.isfile(target.filePath) and not self._confirm_overwrite(target.filePath):
            raise Error(f'{_("Action canceled by user")}.')


import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote


class File:
    DESCRIPTION = _('File')
    EXTENSION = None
    SUFFIX = None

    PRJ_KWVAR = []
    CHP_KWVAR = []
    SCN_KWVAR = []
    CRT_KWVAR = []
    LOC_KWVAR = []
    ITM_KWVAR = []
    PNT_KWVAR = []

    def __init__(self, filePath, **kwargs):
        super().__init__()
        self.novel = None

        self._filePath = None

        self.projectName = None

        self.projectPath = None

        self.scenesSplit = False
        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            try:
                head, tail = os.path.split(os.path.realpath(filePath))
            except:
                head, tail = os.path.split(filePath)
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        raise NotImplementedError

    def write(self):
        raise NotImplementedError

    def _convert_from_yw(self, text, quick=False):
        return text.rstrip()

    def _convert_to_yw(self, text):
        return text.rstrip()


def indent(elem, level=0):
    i = f'\n{level * "  "}'
    if elem:
        if not elem.text or not elem.text.strip():
            elem.text = f'{i}  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


from hashlib import pbkdf2_hmac


class Handles:
    HANDLE_CHARS = list('abcdef0123456789')
    SIZE = 13

    def __init__(self):
        self._handles = []

    def has_member(self, handle):
        return handle in self._handles

    def add_member(self, handle):
        if self.has_member(handle):
            return False

        if len(handle) != self.SIZE:
            return False

        for c in handle:
            if not c in self.HANDLE_CHARS:
                return False

        self._handles.append(handle)
        return True

    def create_member(self, text):

        def create_handle(text, salt):
            text = text.encode('utf-8')
            key = pbkdf2_hmac('sha1', text, bytes(salt), 1)
            keyInt = int.from_bytes(key, byteorder='big')
            handle = ''
            while len(handle) < self.SIZE and keyInt > 0:
                handle += self.HANDLE_CHARS[keyInt % len(self.HANDLE_CHARS)]
                keyInt //= len(self.HANDLE_CHARS)
            return handle

        i = 0
        handle = create_handle(text, i)
        while not self.add_member(handle):
            i += 1
            if i > 1000:
                raise ValueError('Unable to create a proper handle.')

            handle = create_handle(text, i)
        return(handle)


class NwItem:

    def __init__(self):
        self.nwName = None
        self.nwType = None
        self.nwClass = None
        self.nwStatus = None
        self.nwImportance = None
        self.nwActive = None
        self.nwLayout = None
        self.nwCharCount = None
        self.nwWordCount = None
        self.nwParaCount = None
        self.nwCursorPos = None
        self.nwHandle = None
        self.nwOrder = None
        self.nwParent = None


class NwItemV15(NwItem):

    def read(self, node, master):
        self.nwHandle = node.attrib.get('handle')
        self.nwOrder = int(node.attrib.get('order'))
        self.nwParent = node.attrib.get('parent')
        self.nwType = node.attrib.get('type')
        self.nwClass = node.attrib.get('class')
        self.nwLayout = node.attrib.get('layout')
        if node.find('name') is not None:
            nameNode = node.find('name')
            self.nwName = nameNode.text
            status = nameNode.attrib.get('status')
            if status is not None:
                self.nwStatus = master.statusLookup[status]
            importance = nameNode.attrib.get('import')
            if importance is not None:
                self.nwImportance = master.importanceLookup[importance]
            isActive = nameNode.attrib.get('active')
            if isActive in ('yes', 'true', 'on'):
                self.nwActive = True
            else:
                self.nwActive = False
        return self.nwHandle

    def write(self, parentNode, master):
        attrib = {
            'handle': self.nwHandle,
            'parent': self.nwParent,
            'order': str(self.nwOrder),
        }
        node = ET.SubElement(parentNode, 'item', attrib)
        nameNode = ET.SubElement(node, 'name')
        if self.nwName is not None:
            nameNode.text = self.nwName
        if self.nwStatus is not None:
            nameNode.set('status', master.STATUS_IDS[self.nwStatus])
        if self.nwImportance is not None:
            nameNode.set('import', master.IMPORTANCE_IDS[self.nwImportance])
        if self.nwActive is not None:
            if self.nwActive:
                nameNode.set('active', 'yes')
            else:
                nameNode.set('active', 'no')
        if self.nwType is not None:
            node.set('type', self.nwType)
        if self.nwClass is not None:
            node.set('class', self.nwClass)
        if self.nwLayout is not None:
            node.set('layout', self.nwLayout)
        nwMeta = ET.SubElement(node, 'meta')
        if self.nwCharCount is not None:
            nwMeta.set('charCount', self.nwCharCount)
        if self.nwWordCount is not None:
            nwMeta.set('wordCount', self.nwWordCount)
        if self.nwParaCount is not None:
            nwMeta.set('paraCount', self.nwParaCount)
        if self.nwCursorPos is not None:
            nwMeta.set('cursorPos', self.nwCursorPos)
        return node


class NwdFile:
    EXTENSION = '.nwd'

    def __init__(self, prj, nwItem):
        self._prj = prj
        self._nwItem = nwItem
        self._filePath = os.path.dirname(self._prj.filePath) + self._prj.CONTENT_DIR + nwItem.nwHandle + self.EXTENSION
        self._lines = []

    def read(self):
        try:
            with open(self._filePath, 'r', encoding='utf-8') as f:
                self._lines = f.read().split('\n')
                return 'Item data read in.'

        except:
            raise Error(f'Can not read "{norm_path(self._filePath)}".')

    def write(self):
        lines = [f'%%~name: {self._nwItem.nwName}',
                 f'%%~path: {self._nwItem.nwParent}/{self._nwItem.nwHandle}',
                 f'%%~kind: {self._nwItem.nwClass}/{self._nwItem.nwLayout}',
                 ]
        lines.extend(self._lines)
        text = '\n'.join(lines)
        try:
            with open(self._filePath, 'w', encoding='utf-8') as f:
                f.write(text)
                return 'nwd file saved.'

        except:
            raise Error(f'Can not write "{norm_path(self._filePath)}".')


class NwdCharacterFile(NwdFile):

    def __init__(self, prj, nwItem):
        super().__init__(prj, nwItem)

        self._majorImportance = prj.kwargs['major_character_status']

        self._characterNotesHeading = prj.kwargs['character_notes_heading']
        self._characterGoalsHeading = prj.kwargs['character_goals_heading']
        self._characterBioHeading = prj.kwargs['character_bio_heading']

        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        super().read()
        self._prj.crCount += 1
        crId = str(self._prj.crCount)
        self._prj.novel.characters[crId] = Character()
        self._prj.novel.characters[crId].fullName = self._nwItem.nwName
        self._prj.novel.characters[crId].title = self._nwItem.nwName
        desc = []
        bio = []
        goals = []
        notes = []
        section = 'desc'
        for line in self._lines:
            if not line:
                continue

            elif line.startswith('%%'):
                continue

            elif line.startswith('#'):
                section = 'desc'
                if line.startswith(self._characterBioHeading):
                    section = 'bio'
                elif line.startswith(self._characterGoalsHeading):
                    section = 'goals'
                elif line.startswith(self._characterNotesHeading):
                    section = 'notes'
            elif line.startswith('@'):
                if line.startswith('@tag'):
                    self._prj.novel.characters[crId].title = line.split(':')[1].strip().replace('_', ' ')
            elif line.startswith('%'):
                if line.startswith(self._ywAkaKeyword):
                    self._prj.novel.characters[crId].aka = line.split(':')[1].strip()
                elif line.startswith(self._ywTagKeyword):
                    if self._prj.novel.characters[crId].tags is None:
                        self._prj.novel.characters[crId].tags = []
                    self._prj.novel.characters[crId].tags.append(line.split(':')[1].strip())
            elif section == 'desc':
                desc.append(line)
            elif section == 'bio':
                bio.append(line)
            elif section == 'goals':
                goals.append(line)
            elif section == 'notes':
                notes.append(line)
        self._prj.novel.characters[crId].desc = '\n'.join(desc)
        self._prj.novel.characters[crId].bio = '\n'.join(bio)
        self._prj.novel.characters[crId].goals = '\n'.join(goals)
        self._prj.novel.characters[crId].notes = '\n'.join(notes)
        if self._nwItem.nwImportance in self._majorImportance:
            self._prj.novel.characters[crId].isMajor = True
        else:
            self._prj.novel.characters[crId].isMajor = False
        self._prj.novel.srtCharacters.append(crId)
        return 'Character data read in.'

    def add_character(self, crId):
        character = self._prj.novel.characters[crId]

        if character.fullName:
            title = character.fullName
        else:
            title = character.title
        self._lines.append(f'# {title}\n')

        self._lines.append(f'@tag: {character.title.replace(" ", "_")}')

        if character.aka:
            self._lines.append(self._ywAkaKeyword + character.aka)

        if character.tags is not None:
            for tag in character.tags:
                self._lines.append(self._ywTagKeyword + tag)

        if character.desc:
            self._lines.append(f'\n{character.desc}')

        if character.bio:
            self._lines.append(f'\n{self._characterBioHeading}')
            self._lines.append(character.bio)

        if character.goals:
            self._lines.append(f'\n{self._characterGoalsHeading}')
            self._lines.append(character.goals)

        if character.notes:
            self._lines.append(f'\n{self._characterNotesHeading}')
            self._lines.append(character.notes)


class NwdNovelFile(NwdFile):
    _POV_TAG = '@pov: '
    _CHARACTER_TAG = '@char: '
    _LOCATION_TAG = '@location: '
    _ITEM_TAG = '@object: '
    _SYNOPSIS_KEYWORD = 'synopsis:'

    def __init__(self, prj, nwItem):
        super().__init__(prj, nwItem)

        self.doubleLinebreaks = prj.kwargs['double_linebreaks']

        self._outlineStatus = prj.kwargs['outline_status']
        self._draftStatus = prj.kwargs['draft_status']
        self._firstEditStatus = prj.kwargs['first_edit_status']
        self._secondEditStatus = prj.kwargs['second_edit_status']
        self._doneStatus = prj.kwargs['done_status']

        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def _convert_from_yw(self, text, quick=False):
        if quick:
            if text is None:
                return ''
            else:
                return text

        MD_REPLACEMENTS = [
            ('[i] ', ' [i]'),
            ('[b] ', ' [b]'),
            ('[s] ', ' [s]'),
            (' [/i]', '[/i] '),
            (' [/b]', '[/b] '),
            (' [/s]', '[/s] '),
            ('[i]', '_'),
            ('[/i]', '_'),
            ('[b]', '**'),
            ('[/b]', '**'),
            ('[s]', '~~'),
            ('[/s]', '~~'),
            ('  ', ' '),
        ]
        if self.doubleLinebreaks:
            MD_REPLACEMENTS.insert(0, ['\n', '\n\n'])
        try:
            for yw, md in MD_REPLACEMENTS:
                text = text.replace(yw, md)
            text = re.sub('\[\/*[h|c|r|u]\d*\]', '', text)
        except AttributeError:
            text = ''
        return text

    def _convert_to_yw(self, text):

        text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
        text = re.sub('\_([^ ].+?[^ ])\_', '[i]\\1[/i]', text)
        text = re.sub('\~\~(.+?)\~\~', '[s]\\1[/s]', text)

        MD_REPLACEMENTS = []
        if self.doubleLinebreaks:
            MD_REPLACEMENTS.insert(0, ('\n\n', '\n'))
        try:
            for md, yw in MD_REPLACEMENTS:
                text = text.replace(md, yw)
        except AttributeError:
            text = ''
        return text

    def read(self):

        def set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags):
            if scId is not None:
                text = '\n'.join(contentLines)
                self._prj.novel.scenes[scId].sceneContent = self._convert_to_yw(text)
                self._prj.novel.scenes[scId].desc = '\n'.join(synopsis)
                self._prj.novel.scenes[scId].characters = characters
                self._prj.novel.scenes[scId].locations = locations
                self._prj.novel.scenes[scId].items = items
                self._prj.novel.scenes[scId].tags = tags

        scId = None
        super().read()

        elementType = None
        status = None
        if self._nwItem.nwLayout == 'DOCUMENT' and self._nwItem.nwActive:
            elementType = 0
        elif self._nwItem.nwLayout == 'NOTE':
            elementType = 1
        else:
            elementType = 3
        if self._nwItem.nwStatus in self._outlineStatus:
            status = 1
        elif self._nwItem.nwStatus in self._draftStatus:
            status = 2
        elif self._nwItem.nwStatus in self._firstEditStatus:
            status = 3
        elif self._nwItem.nwStatus in self._secondEditStatus:
            status = 4
        elif self._nwItem.nwStatus in self._doneStatus:
            status = 5
        else:
            status = 1
        characters = []
        locations = []
        items = []
        synopsis = []
        contentLines = []
        tags = []
        inScene = False
        sceneTitle = None
        appendToPrev = None
        for line in self._lines:
            if line.startswith('%%'):
                continue

            elif line.startswith(self._POV_TAG):
                characters.insert(0, line.replace(self._POV_TAG, '').strip().replace('_', ' '))
            elif line.startswith(self._CHARACTER_TAG):
                characters.append(line.replace(self._CHARACTER_TAG, '').strip().replace('_', ' '))
            elif line.startswith(self._LOCATION_TAG):
                locations.append(line.replace(self._LOCATION_TAG, '').strip().replace('_', ' '))
            elif line.startswith(self._ITEM_TAG):
                items.append(line.replace(self._ITEM_TAG, '').strip().replace('_', ' '))
            elif line.startswith('@'):
                continue

            elif line.startswith('%'):
                if line.startswith(self._ywTagKeyword):
                    tags.append(line.split(':', maxsplit=1)[1].strip())
                else:
                    line = line.lstrip('%').lstrip()
                    if line.lower().startswith(self._SYNOPSIS_KEYWORD):
                        synopsis.append(line.split(':', maxsplit=1)[1].strip())
                    pass
            elif line.startswith('###') and self._prj.chId:
                set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags)
                scId = None
                characters = []
                locations = []
                items = []
                synopsis = []
                tags = []
                sceneTitle = line.split(' ', maxsplit=1)[1]
                if line.startswith('####'):
                    appendToPrev = True
                else:
                    appendToPrev = None
                inScene = True
            elif line.startswith('#'):
                set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags)
                synopsis = []

                self._prj.chCount += 1
                self._prj.chId = str(self._prj.chCount)
                self._prj.novel.chapters[self._prj.chId] = Chapter()
                self._prj.novel.chapters[self._prj.chId].title = line.split(' ', maxsplit=1)[1]
                self._prj.novel.chapters[self._prj.chId].chType = elementType
                self._prj.novel.srtChapters.append(self._prj.chId)
                if line.startswith('##'):
                    self._prj.novel.chapters[self._prj.chId].chLevel = 0
                else:
                    self._prj.novel.chapters[self._prj.chId].chLevel = 1

                scId = None
                characters = []
                locations = []
                items = []
                tags = []
                sceneTitle = f'Scene {self._prj.scCount + 1}'
                inScene = False
            elif scId is None and not line:
                continue

            elif sceneTitle and scId is None:
                if synopsis and not inScene:
                    self._prj.novel.chapters[self._prj.chId].desc = '\n'.join(synopsis)
                    synopsis = []
                inScene = True

                self._prj.scCount += 1
                scId = str(self._prj.scCount)
                self._prj.novel.scenes[scId] = Scene()
                self._prj.novel.scenes[scId].status = status
                self._prj.novel.scenes[scId].title = sceneTitle
                self._prj.novel.scenes[scId].scType = elementType
                self._prj.novel.chapters[self._prj.chId].srtScenes.append(scId)
                self._prj.novel.scenes[scId].appendToPrev = appendToPrev
                contentLines = [line]
            elif scId is not None:
                contentLines.append(line)

        if scId is not None:
            set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags)
        elif synopsis:
            self._prj.novel.chapters[self._prj.chId].desc = '\n'.join(synopsis)
        return 'Chapters and scenes read in.'

    def add_scene(self, scId):
        scene = self._prj.novel.scenes[scId]
        if scene.appendToPrev:
            self._lines.append(f'#### {scene.title}\n')
        else:
            self._lines.append(f'### {scene.title}\n')

        if scene.characters is not None:
            isViewpoint = True
            for crId in scene.characters:
                if isViewpoint:
                    self._lines.append(self._POV_TAG + self._prj.novel.characters[crId].title.replace(' ', '_'))
                    isViewpoint = False
                else:
                    self._lines.append(self._CHARACTER_TAG + self._prj.novel.characters[crId].title.replace(' ', '_'))

        if scene.locations is not None:
            for lcId in scene.locations:
                self._lines.append(self._LOCATION_TAG + self._prj.novel.locations[lcId].title.replace(' ', '_'))

        if scene.items is not None:
            for itId in scene.items:
                self._lines.append(self._ITEM_TAG + self._prj.novel.items[itId].title.replace(' ', '_'))

        if scene.tags is not None:
            for tag in scene.tags:
                self._lines.append(self._ywTagKeyword + tag)

        if scene.desc:
            synopsis = scene.desc.replace('\n', '\t')
            self._lines.append(f'\n% {self._SYNOPSIS_KEYWORD} {synopsis}')

        self._lines.append('\n')

        text = self._convert_from_yw(scene.sceneContent)
        if text:
            self._lines.append(text)

    def add_chapter(self, chId):
        chapter = self._prj.novel.chapters[chId]
        if chapter.chLevel == 0:
            self._lines.append(f'## {chapter.title}\n')
        else:
            self._lines.append(f'# {chapter.title}\n')

        if chapter.desc:
            synopsis = chapter.desc.replace('\n', '\t')
            self._lines.append(f'\n% {self._SYNOPSIS_KEYWORD} {synopsis}\n')


class NwdWorldFile(NwdFile):

    def __init__(self, prj, nwItem):
        super().__init__(prj, nwItem)

        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        super().read()
        self._prj.lcCount += 1
        lcId = str(self._prj.lcCount)
        self._prj.novel.locations[lcId] = WorldElement()
        self._prj.novel.locations[lcId].title = self._nwItem.nwName
        desc = []
        for line in self._lines:
            if not line:
                continue

            elif line.startswith('%%'):
                continue

            elif line.startswith('#'):
                continue

            elif line.startswith('%'):
                if line.startswith(self._ywAkaKeyword):
                    self._prj.novel.locations[lcId].aka = line.split(':')[1].strip()
                elif line.startswith(self._ywTagKeyword):
                    if self._prj.novel.locations[lcId].tags is None:
                        self._prj.novel.locations[lcId].tags = []
                    self._prj.novel.locations[lcId].tags.append(line.split(':')[1].strip())
                else:
                    continue

            elif line.startswith('@'):
                if line.startswith('@tag'):
                    self._prj.novel.locations[lcId].title = line.split(':')[1].strip().replace('_', ' ')
                else:
                    continue

            else:
                desc.append(line)
        self._prj.novel.locations[lcId].desc = '\n'.join(desc)
        self._prj.novel.srtLocations.append(lcId)
        return 'Location data read in.'

    def add_element(self, lcId):
        location = self._prj.novel.locations[lcId]

        self._lines.append(f'# {location.title}\n')

        self._lines.append(f'@tag: {location.title.replace(" ", "_")}')

        if location.aka:
            self._lines.append(self._ywAkaKeyword + location.aka)

        if location.tags is not None:
            for tag in location.tags:
                self._lines.append(self._ywTagKeyword + tag)

        if location.desc:
            self._lines.append(f'\n{location.desc}')
        return super().write()


class NwdObjectFile(NwdFile):

    def __init__(self, prj, nwItem):
        super().__init__(prj, nwItem)

        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        super().read()
        self._prj.lcCount += 1
        itId = str(self._prj.lcCount)
        self._prj.novel.items[itId] = WorldElement()
        self._prj.novel.items[itId].title = self._nwItem.nwName
        desc = []
        for line in self._lines:
            if not line:
                continue

            elif line.startswith('%%'):
                continue

            elif line.startswith('#'):
                continue

            elif line.startswith('%'):
                if line.startswith(self._ywAkaKeyword):
                    self._prj.novel.items[itId].aka = line.split(':')[1].strip()
                elif line.startswith(self._ywTagKeyword):
                    if self._prj.novel.items[itId].tags is None:
                        self._prj.novel.items[itId].tags = []
                    self._prj.novel.items[itId].tags.append(line.split(':')[1].strip())
                else:
                    continue

            elif line.startswith('@'):
                if line.startswith('@tag'):
                    self._prj.novel.items[itId].title = line.split(':')[1].strip().replace('_', ' ')
                else:
                    continue

            else:
                desc.append(line)
        self._prj.novel.items[itId].desc = '\n'.join(desc)
        self._prj.novel.srtItems.append(itId)
        return 'Item data read in.'

    def add_element(self, itId):
        item = self._prj.novel.items[itId]

        self._lines.append(f'# {item.title}\n')

        self._lines.append(f'@tag: {item.title.replace(" ", "_")}')

        if item.aka:
            self._lines.append(self._ywAkaKeyword + item.aka)

        if item.tags is not None:
            for tag in item.tags:
                self._lines.append(self._ywTagKeyword + tag)

        if item.desc:
            self._lines.append(f'\n{item.desc}')
        return super().write()


WRITE_NEW_FORMAT = True


class NwxFile(File):
    EXTENSION = '.nwx'
    DESCRIPTION = 'novelWriter project'
    SUFFIX = ''
    CONTENT_DIR = '/content/'
    CONTENT_EXTENSION = '.nwd'
    _NWX_TAG = 'novelWriterXML'
    _NWX_ATTR_V1_5 = {
        'appVersion': '2.0.2',
        'hexVersion': '0x020002f0',
        'fileVersion': '1.5',
        'timeStamp': datetime.today().replace(microsecond=0).isoformat(sep=' '),
    }
    _NWD_CLASSES = {
        'CHARACTER':NwdCharacterFile,
        'WORLD':NwdWorldFile,
        'OBJECT':NwdObjectFile,
        'NOVEL':NwdNovelFile
        }
    _TRAILER = ('ARCHIVE', 'TRASH')
    STATUS_IDS = {
            'None': 's000001',
            'Outline': 's000002',
            'Draft': 's000003',
            '1st Edit': 's000004',
            '2nd Edit': 's000005',
            'Done': 's000006',
            }

    IMPORTANCE_IDS = {
            'None': 'i000001',
            'Minor': 'i000002',
            'Major': 'i000003',
            }

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath, **kwargs)
        self._tree = None
        self.kwargs = kwargs
        self.nwHandles = Handles()
        self.lcCount = 0
        self.crCount = 0
        self.itCount = 0
        self.scCount = 0
        self.chCount = 0
        self.chId = None
        self._sceneStatus = kwargs['scene_status']
        self.statusLookup = {}

    def read_xml_file(self):
        try:
            self._tree = ET.parse(self.filePath)
        except:
            raise Error(f'Can not process "{norm_path(self.filePath)}".')

    def read(self):

        if self._tree is None:
            self.read_xml_file()
        root = self._tree.getroot()

        if root.tag != self._NWX_TAG:
            raise Error(f'This seems not to bee a novelWriter project file.')

        if root.attrib.get('fileVersion') != self._NWX_ATTR_V1_5['fileVersion']:
            raise Error(f'Wrong file version (must be {self._NWX_ATTR_V1_5["fileVersion"]}).')

        NwItem = NwItemV15
        self.statusLookup = {}
        xmlStatus = root.find('settings').find('status')
        for xmlStatusEntry in xmlStatus.findall('entry'):
            self.statusLookup[xmlStatusEntry.attrib.get('key')] = xmlStatusEntry.text
        self.importanceLookup = {}
        xmlImportance = root.find('settings').find('importance')
        for xmlImportanceEntry in xmlImportance.findall('entry'):
            self.importanceLookup[xmlImportanceEntry.attrib.get('key')] = xmlImportanceEntry.text

        prj = root.find('project')
        if prj.find('title') is not None:
            self.novel.title = prj.find('title').text
        elif prj.find('name') is not None:
            self.novel.title = prj.find('name').text
        authors = []
        for author in prj.iter('author'):
            if author is not None:
                if author.text:
                    authors.append(author.text)
        self.novel.authorName = ', '.join(authors)

        content = root.find('content')
        for node in content.iter('item'):
            nwItem = NwItem()
            handle = nwItem.read(node, self)
            if not self.nwHandles.add_member(handle):
                raise Error(f'Invalid handle: {handle}')

            if nwItem.nwClass in self._TRAILER:
                break

            if nwItem.nwType != 'FILE':
                continue

            nwdFile = self._NWD_CLASSES[nwItem.nwClass](self, nwItem)
            nwdFile.read()

        crIdsByTitle = {}
        for crId in self.novel.characters:
            crIdsByTitle[self.novel.characters[crId].title] = crId
        lcIdsByTitle = {}
        for lcId in self.novel.locations:
            lcIdsByTitle[self.novel.locations[lcId].title] = lcId
        itIdsByTitle = {}
        for itId in self.novel.items:
            itIdsByTitle[self.novel.items[itId].title] = itId

        for scId in self.novel.scenes:
            characters = []
            for crId in self.novel.scenes[scId].characters:
                characters.append(crIdsByTitle[crId])
            self.novel.scenes[scId].characters = characters
            locations = []
            for lcId in self.novel.scenes[scId].locations:
                locations.append(lcIdsByTitle[lcId])
            self.novel.scenes[scId].locations = locations
            items = []
            for itId in self.novel.scenes[scId].items:
                items.append(itIdsByTitle[itId])
            self.novel.scenes[scId].items = items

        return 'novelWriter data converted to novel structure.'

    def write(self):

        def write_entry(parent, entry, red, green, blue, map):
            attrib = {}
            attrib['key'] = map[entry]
            attrib['count'] = '0'
            attrib['blue'] = str(blue)
            attrib['green'] = str(green)
            attrib['red'] = str(red)
            ET.SubElement(parent, 'entry', attrib).text = entry

        root = ET.Element(self._NWX_TAG, self._NWX_ATTR_V1_5)
        NwItem = NwItemV15

        xmlPrj = ET.SubElement(root, 'project')
        if self.novel.title:
            title = self.novel.title
        else:
            title = 'New project'
        ET.SubElement(xmlPrj, 'name').text = title
        ET.SubElement(xmlPrj, 'title').text = title
        if self.novel.authorName:
            authors = self.novel.authorName.split(',')
        else:
            authors = ['']
        for author in authors:
            ET.SubElement(xmlPrj, 'author').text = author.strip()

        settings = ET.SubElement(root, 'settings')
        status = ET.SubElement(settings, 'status')
        try:
            write_entry(status, self._sceneStatus[0], 230, 230, 230, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[1], 0, 0, 0, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[2], 170, 40, 0, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[3], 240, 140, 0, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[4], 250, 190, 90, self.STATUS_IDS)
            write_entry(status, self._sceneStatus[5], 58, 180, 58, self.STATUS_IDS)
        except IndexError:
            pass
        importance = ET.SubElement(settings, 'importance')
        write_entry(importance, 'None', 220, 220, 220, self.IMPORTANCE_IDS)
        write_entry(importance, 'Minor', 0, 122, 188, self.IMPORTANCE_IDS)
        write_entry(importance, 'Major', 21, 0, 180, self.IMPORTANCE_IDS)

        content = ET.SubElement(root, 'content')
        attrCount = 0
        order = [0]

        novelFolderHandle = self.nwHandles.create_member('novelFolderHandle')
        novelFolder = NwItem()
        novelFolder.nwHandle = novelFolderHandle
        novelFolder.nwOrder = order[-1]
        novelFolder.nwParent = 'None'
        novelFolder.nwName = 'Novel'
        novelFolder.nwType = 'ROOT'
        novelFolder.nwClass = 'NOVEL'
        novelFolder.nwExpanded = 'True'
        novelFolder.write(content, self)
        attrCount += 1
        order[-1] += 1
        hasPartLevel = False
        isInChapter = False

        order.append(0)
        for chId in self.novel.srtChapters:
            if self.novel.chapters[chId].chLevel == 1:
                hasPartLevel = True
                isInChapter = False

                partFolderHandle = self.nwHandles.create_member(f'{chId + self.novel.chapters[chId].title}Folder')
                partFolder = NwItem()
                partFolder.nwHandle = partFolderHandle
                partFolder.nwOrder = order[-1]
                partFolder.nwParent = novelFolderHandle
                partFolder.nwName = self.novel.chapters[chId].title
                partFolder.nwType = 'FOLDER'
                partFolder.nwClass = 'NOVEL'
                partFolder.expanded = 'True'
                partFolder.write(content, self)
                attrCount += 1
                order[-1] += 1
                order.append(0)

                partHeadingHandle = self.nwHandles.create_member(f'{chId + self.novel.chapters[chId].title}')
                partHeading = NwItem()
                partHeading.nwHandle = partHeadingHandle
                partHeading.nwOrder = order[-1]
                partHeading.nwParent = partFolderHandle
                partHeading.nwName = self.novel.chapters[chId].title
                partHeading.nwType = 'FILE'
                partHeading.nwClass = 'NOVEL'
                partHeading.nwLayout = 'DOCUMENT'
                partHeading.nwActive = True
                if self.novel.chapters[chId].chType == 3:
                    partHeading.nwActive = False
                elif self.novel.chapters[chId].chType in (1, 2):
                    partHeading.nwLayout = 'NOTE'
                partHeading.nwStatus = 'None'
                partHeading.nwImportance = 'None'
                partHeading.write(content, self)

                nwdFile = NwdNovelFile(self, partHeading)
                nwdFile.add_chapter(chId)
                nwdFile.write()
                attrCount += 1
                order[-1] += 1

                order.append(0)
            else:
                isInChapter = True

                chapterFolderHandle = self.nwHandles.create_member(f'{chId}{self.novel.chapters[chId].title}Folder')
                chapterFolder = NwItem()
                chapterFolder.nwHandle = chapterFolderHandle
                chapterFolder.nwOrder = order[-1]
                if hasPartLevel:
                    chapterFolder.nwParent = partFolderHandle
                else:
                    chapterFolder.nwParent = novelFolderHandle
                chapterFolder.nwName = self.novel.chapters[chId].title
                chapterFolder.nwType = 'FOLDER'
                chapterFolder.expanded = 'True'
                chapterFolder.write(content, self)
                attrCount += 1
                order[-1] += 1
                order.append(0)

                chapterHeadingHandle = self.nwHandles.create_member(f'{chId}{self.novel.chapters[chId].title}')
                chapterHeading = NwItem()
                chapterHeading.nwHandle = chapterHeadingHandle
                chapterHeading.nwOrder = order[-1]
                chapterHeading.nwParent = chapterFolderHandle
                chapterHeading.nwName = self.novel.chapters[chId].title
                chapterHeading.nwType = 'FILE'
                chapterHeading.nwClass = 'NOVEL'
                chapterHeading.nwLayout = 'DOCUMENT'
                chapterHeading.nwActive = True
                if self.novel.chapters[chId].chType == 3:
                    chapterHeading.nwActive = False
                elif self.novel.chapters[chId].chType in (1, 2):
                    chapterHeading.nwLayout = 'NOTE'
                chapterHeading.nwStatus = 'None'
                chapterHeading.nwImportance = 'None'
                chapterHeading.write(content, self)

                nwdFile = NwdNovelFile(self, chapterHeading)
                nwdFile.add_chapter(chId)
                nwdFile.write()
                attrCount += 1
                order[-1] += 1
            for scId in self.novel.chapters[chId].srtScenes:
                sceneHandle = self.nwHandles.create_member(f'{scId}{self.novel.scenes[scId].title}')
                scene = NwItem()
                scene.nwHandle = sceneHandle
                scene.nwOrder = order[-1]
                if isInChapter:
                    scene.nwParent = chapterFolderHandle
                else:
                    scene.nwParent = partFolderHandle
                if self.novel.scenes[scId].title:
                    title = self.novel.scenes[scId].title
                else:
                    title = f'Scene {order[-1] + 1}'
                scene.nwName = title
                scene.nwType = 'FILE'
                scene.nwClass = 'NOVEL'
                if self.novel.scenes[scId].status is not None:
                    try:
                        scene.nwStatus = self._sceneStatus[self.novel.scenes[scId].status]
                    except IndexError:
                        scene.nwStatus = self._sceneStatus[-1]
                scene.nwImportance = 'None'
                scene.nwLayout = 'DOCUMENT'
                scene.nwActive = True
                if self.novel.scenes[scId].scType == 3:
                    scene.nwActive = False
                elif self.novel.scenes[scId].scType in (1, 2):
                    scene.nwLayout = 'NOTE'
                if self.novel.scenes[scId].wordCount:
                    scene.nwWordCount = str(self.novel.scenes[scId].wordCount)
                if self.novel.scenes[scId].letterCount:
                    scene.nwCharCount = str(self.novel.scenes[scId].letterCount)
                scene.write(content, self)

                nwdFile = NwdNovelFile(self, scene)
                nwdFile.add_scene(scId)
                nwdFile.write()
                attrCount += 1
                order[-1] += 1
            order.pop()
        order.pop()

        characterFolderHandle = self.nwHandles.create_member('characterFolderHandle')
        characterFolder = NwItem()
        characterFolder.nwHandle = characterFolderHandle
        characterFolder.nwOrder = order[-1]
        characterFolder.nwParent = 'None'
        characterFolder.nwName = 'Characters'
        characterFolder.nwType = 'ROOT'
        characterFolder.nwClass = 'CHARACTER'
        characterFolder.nwStatus = 'None'
        characterFolder.nwImportance = 'None'
        characterFolder.nwExpanded = 'True'
        characterFolder.write(content, self)
        attrCount += 1
        order[-1] += 1

        order.append(0)
        for crId in self.novel.srtCharacters:
            characterHandle = self.nwHandles.create_member(f'{crId}{self.novel.characters[crId].title}')
            character = NwItem()
            character.nwHandle = characterHandle
            character.nwOrder = order[-1]
            character.nwParent = characterFolderHandle
            if self.novel.characters[crId].fullName:
                character.nwName = self.novel.characters[crId].fullName
            elif self.novel.characters[crId].title:
                character.nwName = self.novel.characters[crId].title
            else:
                character.nwName = f'Character {order[-1] + 1}'
            character.nwType = 'FILE'
            character.nwClass = 'CHARACTER'
            character.nwStatus = 'None'
            if self.novel.characters[crId].isMajor:
                character.nwImportance = 'Major'
            else:
                character.nwImportance = 'Minor'
            character.nwActive = True
            character.nwLayout = 'NOTE'
            character.write(content, self)

            nwdFile = NwdCharacterFile(self, character)
            nwdFile.add_character(crId)
            nwdFile.write()

            attrCount += 1
            order[-1] += 1
        order.pop()

        worldFolderHandle = self.nwHandles.create_member('worldFolderHandle')
        worldFolder = NwItem()
        worldFolder.nwHandle = worldFolderHandle
        worldFolder.nwOrder = order[-1]
        worldFolder.nwParent = 'None'
        worldFolder.nwName = 'Locations'
        worldFolder.nwType = 'ROOT'
        worldFolder.nwClass = 'WORLD'
        worldFolder.nwStatus = 'None'
        worldFolder.nwImportance = 'None'
        worldFolder.nwExpanded = 'True'
        worldFolder.write(content, self)
        attrCount += 1
        order[-1] += 1

        order.append(0)
        for lcId in self.novel.srtLocations:
            locationHandle = self.nwHandles.create_member(f'{lcId}{self.novel.locations[lcId].title}')
            location = NwItem()
            location.nwHandle = locationHandle
            location.nwOrder = order[-1]
            location.nwParent = worldFolderHandle
            if self.novel.locations[lcId].title:
                title = self.novel.locations[lcId].title
            else:
                title = f'Place {order[-1] + 1}'
            location.nwName = title
            location.nwType = 'FILE'
            location.nwClass = 'WORLD'
            location.nwActive = True
            location.nwLayout = 'NOTE'
            location.nwStatus = 'None'
            location.nwImportance = 'None'
            location.write(content, self)

            nwdFile = NwdWorldFile(self, location)
            nwdFile.add_element(lcId)
            nwdFile.write()
            attrCount += 1
            order[-1] += 1
        order.pop()

        objectFolderHandle = self.nwHandles.create_member('objectFolderHandle')
        objectFolder = NwItem()
        objectFolder.nwHandle = objectFolderHandle
        objectFolder.nwOrder = order[-1]
        objectFolder.nwParent = 'None'
        objectFolder.nwName = 'Items'
        objectFolder.nwType = 'ROOT'
        objectFolder.nwClass = 'OBJECT'
        objectFolder.nwStatus = 'None'
        objectFolder.nwImportance = 'None'
        objectFolder.nwExpanded = 'True'
        objectFolder.write(content, self)
        attrCount += 1
        order[-1] += 1

        order.append(0)
        for itId in self.novel.srtItems:
            itemHandle = self.nwHandles.create_member(f'{itId}{self.novel.items[itId].title}')
            item = NwItem()
            item.nwHandle = itemHandle
            item.nwOrder = order[-1]
            item.nwParent = objectFolderHandle
            if self.novel.items[itId].title:
                title = self.novel.items[itId].title
            else:
                title = f'Object {order[-1] + 1}'
            item.nwName = title
            item.nwType = 'FILE'
            item.nwClass = 'OBJECT'
            item.nwActive = True
            item.nwLayout = 'NOTE'
            item.nwStatus = 'None'
            item.nwImportance = 'None'
            item.write(content, self)

            nwdFile = NwdObjectFile(self, item)
            nwdFile.add_element(itId)
            nwdFile.write()
            attrCount += 1
            order[-1] += 1
        order.pop()

        content.set('count', str(attrCount))

        indent(root)
        self._tree = ET.ElementTree(root)
        self._tree.write(self.filePath, xml_declaration=True, encoding='utf-8')
        return f'"{norm_path(self.filePath)}" written.'


from typing import Iterable


def create_id(elements: Iterable) -> str:
    i = 1
    while str(i) in elements:
        i += 1
    return str(i)


class MmFile(File):
    EXTENSION = '.mm'
    DESCRIPTION = 'Mindmap'
    SUFFIX = ''

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath, **kwargs)
        self._locationsIcon = kwargs['locations_icon']
        self._itemsIcon = kwargs['items_icon']
        self._mainCharactersIcon = kwargs['main_characters_icon']
        self._minorCharactersIcon = kwargs['minor_characters_icon']
        self._notesIcon = kwargs['notes_icon']
        self._todoIcon = kwargs['todo_icon']
        self._exportScenes = kwargs['export_scenes']
        self._exportCharacters = kwargs['export_characters']
        self._exportLocations = kwargs['export_locations']
        self._exportItems = kwargs['export_items']
        self._hasNormalParts = kwargs['has_normal_parts']

    def read(self):
        try:
            self._tree = ET.parse(self.filePath)
        except:
            return f'!Can not process "{norm_path(self.filePath)}".'

        root = self._tree.getroot()
        xmlNovel = root.find('node')
        self.novel.title = self._get_title(xmlNovel)
        self.novel.desc = self._get_desc(xmlNovel)
        for xmlNode in xmlNovel.findall('node'):
            isMainCharactersNode = False
            isMinorCharactersNode = False
            isLocationsNode = False
            isItemsNode = False
            for xmlIcon in xmlNode.findall('icon'):
                if xmlIcon.attrib.get('BUILTIN', '') == self._mainCharactersIcon:
                    isMainCharactersNode = True
                    break

                if xmlIcon.attrib.get('BUILTIN', '') == self._minorCharactersIcon:
                    isMinorCharactersNode = True
                    break

                elif xmlIcon.attrib.get('BUILTIN', '') == self._locationsIcon:
                    isLocationsNode = True
                    break

                elif xmlIcon.attrib.get('BUILTIN', '') == self._itemsIcon:
                    isItemsNode = True
                    break

            if isMainCharactersNode:
                if self._exportCharacters:
                    self._get_characters(xmlNode, True)
            elif isMinorCharactersNode:
                if self._exportCharacters:
                    self._get_characters(xmlNode, False)
            elif isLocationsNode:
                if self._exportLocations:
                    self._get_locations(xmlNode)
            elif isItemsNode:
                if self._exportItems:
                    self._get_items(xmlNode)
            elif self._exportScenes:
                self._get_part(xmlNode)

    def _get_characters(self, xmlNode, isMajor):
        for xmlCharacter in xmlNode.findall('node'):
            crId = create_id(self.novel.characters)
            self.novel.characters[crId] = Character()
            self.novel.srtCharacters.append(crId)
            self.novel.characters[crId].title = self._get_title(xmlCharacter)
            self.novel.characters[crId].desc = self._get_desc(xmlCharacter)
            self.novel.characters[crId].isMajor = isMajor

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
        partType = self._get_type(xmlNode)
        if self._hasNormalParts or partType != 0:
            inPart = True
            paId = create_id(self.novel.chapters)
            self.novel.chapters[paId] = Chapter()
            self.novel.srtChapters.append(paId)
            self.novel.chapters[paId].chLevel = 1
            self.novel.chapters[paId].title = self._get_title(xmlNode)
            self.novel.chapters[paId].desc = self._get_desc(xmlNode)
            self.novel.chapters[paId].chType = partType
        else:
            partType = 0
        for xmlChapter in xmlNode.findall('node'):
            chId = create_id(self.novel.chapters)
            self.novel.chapters[chId] = Chapter()
            self.novel.srtChapters.append(chId)
            self.novel.chapters[chId].chLevel = 0
            self.novel.chapters[chId].title = self._get_title(xmlChapter)
            self.novel.chapters[chId].desc = self._get_desc(xmlChapter)
            if partType == 0:
                self.novel.chapters[chId].chType = self._get_type(xmlChapter)
            else:
                self.novel.chapters[chId].chType = partType
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
            for xmlRichContent in xmlNode.findall('richcontent'):
                if xmlRichContent.attrib.get('TYPE', '') == 'NODE':
                    htmlTitle = []
                    for htmlText in xmlRichContent.itertext():
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


class MmNwConverter(YwCnvUi):

    def run(self, sourcePath, **kwargs):
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!File "{norm_path(sourcePath)}" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath.replace('\\', '/'))
        srcDir = os.path.dirname(sourcePath).replace('\\', '/')
        if not srcDir:
            srcDir = '.'
        srcDir = f'{srcDir}/'
        if fileExtension == MmFile.EXTENSION:
            sourceFile = MmFile(sourcePath, **kwargs)
            title = fileName.replace(srcDir, '')
            prjDir = f'{srcDir}{title}.nw'
            if os.path.isfile('{prjDir}/nwProject.lock'):
                self.ui.set_info_how(f'!Please exit novelWriter.')
                return

            try:
                os.makedirs(f'{prjDir}{NwxFile.CONTENT_DIR}')
            except FileExistsError:
                extension = '.bak'
                i = 0
                while os.path.isdir(f'{prjDir}{extension}'):
                    extension = f'.bk{i:03}'
                    i += 1
                    if i > 999:
                        self.ui.set_info_how(f'!Unable to back up the project.')
                        return

                os.replace(prjDir, f'{prjDir}{extension}')
                self.ui.set_info_what(f'Backup folder "{norm_path(prjDir)}{extension}" saved.')
                os.makedirs(f'{prjDir}{NwxFile.CONTENT_DIR}')
            targetFile = NwxFile(f'{prjDir}/nwProject.nwx', **kwargs)
            self.ui.set_info_what(
                _('Create a novelWriter project from {0}\nNew project: "{1}"').format(sourceFile.DESCRIPTION, norm_path(targetFile.filePath)))
            try:
                self.check(sourceFile, targetFile)
                sourceFile.novel = Novel()
                sourceFile.read()
                targetFile.novel = sourceFile.novel
                targetFile.write()
            except Exception as ex:
                message = f'!{str(ex)}'
                self.newFile = None
            else:
                message = f'{_("File written")}: "{norm_path(targetFile.filePath)}".'
                self.newFile = targetFile.filePath
            finally:
                self.ui.set_info_how(message)
        else:
            self.ui.set_info_how(f'!File type of "{norm_path(sourcePath)}" not supported.')


SUFFIX = ''
APPNAME = 'mm2nw'
SETTINGS = dict(
    outline_status=('Outline', 'New', 'Notes'),
    draft_status=('Draft', 'Started', '1st Draft'),
    first_edit_status=('1st Edit', '2nd Draft'),
    second_edit_status=('2nd Edit', '3rd Draft'),
    done_status=('Done', 'Finished'),
    scene_status=('None', 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done'),
    major_character_status=('Major', 'Main'),
    character_notes_heading='## Notes',
    character_goals_heading='## Goals',
    character_bio_heading='## Bio',
    ywriter_aka_keyword='aka',
    ywriter_tag_keyword='tag',
    locations_icon='gohome',
    items_icon='password',
    main_characters_icon='full-1',
    minor_characters_icon='full-2',
    notes_icon='info',
    todo_icon='list',
)
OPTIONS = dict(
    export_scenes=True,
    export_characters=True,
    export_locations=True,
    export_items=True,
    has_normal_parts=True,
    double_linebreaks=True,
)


def main(sourcePath, silentMode=True):
    if silentMode:
        ui = Ui('')
    else:
        ui = UiCmd('Converter between FreeMind and novelWriter 0.1.1')

    kwargs = {'suffix': SUFFIX}
    kwargs.update(SETTINGS)
    kwargs.update(OPTIONS)
    converter = MmNwConverter()
    converter.ui = ui
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Converter between FreeMind and novelWriter',
        epilog='')
    parser.add_argument('sourcePath',
                        metavar='Sourcefile',
                        help='The path of the .mm file.')
    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()
    main(args.sourcePath, args.silent)
