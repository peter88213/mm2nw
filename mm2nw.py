#!/usr/bin/python3
"""Convert FreeMind to novelWriter

Version 0.1.0
Requires Python 3.6+
Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2nw
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
    """Base class for exceptions."""
    pass


#--- Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    # Fallback for old Windows versions.
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
    """Convert a string into a list with unique elements.
    
    Positional arguments:
        text -- string containing divider-separated substrings.
        
    Optional arguments:
        divider -- string that divides the substrings.
    
    Split a string into a list of strings. Retain the order, but discard duplicates.
    Remove leading and trailing spaces, if any.
    Return a list of strings.
    If an error occurs, return an empty list.
    """
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
    """Join strings from a list.
    
    Positional arguments:
        elements -- list of elements to be concatenated.
        
    Optional arguments:
        divider -- string that divides the substrings.
    
    Return a string which is the concatenation of the 
    members of the list of strings "elements", separated by 
    a comma plus a space. The space allows word wrap in 
    spreadsheet cells.
    If an error occurs, return an empty string.
    """
    try:
        text = divider.join(elements)
        return text

    except:
        return ''


class Ui:
    """Base class for UI facades, implementing a 'silent mode'.
    
    Public methods:
        ask_yes_no(text) -- return True or False.
        set_info_how(message) -- show how the converter is doing.
        set_info_what(message) -- show what the converter is going to do.
        show_warning(message) -- Stub for displaying a warning message.
        start() -- launch the GUI, if any.
        
    Public instance variables:
        infoWhatText -- buffer for general messages.
        infoHowText -- buffer for error/success messages.
    """

    def __init__(self, title):
        """Initialize text buffers for messaging.
        
        Positional arguments:
            title -- application title.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """Return True or False.
        
        Positional arguments:
            text -- question to be asked. 
            
        This is a stub used for "silent mode".
        The application may use a subclass for confirmation requests.    
        """
        return True

    def set_info_how(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be buffered.
            
        Print the message to stderr, replacing the error marker, if any.
        """
        if message.startswith('!'):
            message = f'FAIL: {message.split("!", maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be buffered. 
        """
        self.infoWhatText = message

    def show_warning(self, message):
        """Stub for displaying a warning message.

        Positional arguments:
            message -- message to be displayed. 
        """
        pass

    def start(self):
        """Launch the GUI, if any.
        
        To be overridden by subclasses requiring
        special action to launch the user interaction.
        """
        pass


class UiCmd(Ui):
    """Ui subclass implementing a console interface.
    
    Public methods:
        ask_yes_no(text) -- query yes or no at the console.
        set_info_how(message) -- show how the converter is doing.
        set_info_what(message) -- show what the converter is going to do.
        show_warning(message) -- Display a warning message.
    """

    def __init__(self, title):
        """Print the title.
        
        Positional arguments:
            title -- application title to be displayed at the console.
        
        Extends the superclass constructor.
        """
        super().__init__(title)
        print(title)

    def ask_yes_no(self, text):
        """Query yes or no at the console.
        
        Positional arguments:
            text -- question to be asked at the console. 
            
        Overrides the superclass method.       
        """
        result = input(f'{_("WARNING")}: {text} (y/n)')
        if result.lower() == 'y':
            return True
        else:
            return False

    def set_info_how(self, message):
        """Show how the converter is doing.

        Positional arguments:
            message -- message to be printed at the console. 
            
        Print the message, replacing the error marker, if any.
        Overrides the superclass method.
        """
        if message.startswith('!'):
            message = f'FAIL: {message.split("!", maxsplit=1)[1].strip()}'
        self.infoHowText = message
        print(message)

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be printed at the console. 
            
        Print the message.
        Overrides the superclass method.
        """
        print(message)

    def show_warning(self, message):
        """Display a warning message."""
        print(f'\nWARNING: {message}\n')


def open_document(document):
    """Open a document with the operating system's standard application."""
    try:
        os.startfile(norm_path(document))
        # Windows
    except:
        try:
            os.system('xdg-open "%s"' % norm_path(document))
            # Linux
        except:
            try:
                os.system('open "%s"' % norm_path(document))
                # Mac
            except:
                pass


import re
from typing import Iterator, Pattern


class BasicElement:
    """Basic element representation (may be a project note).
    
    Public instance variables:
        title: str -- title (name).
        desc: str -- description.
        kwVar: dict -- custom keyword variables.
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title: str = None
        # xml: <Title>

        self.desc: str = None
        # xml: <Desc>

        self.kwVar: dict[str, str] = {}
        # Optional key/value instance variables for customization.


class Chapter(BasicElement):
    """yWriter chapter representation.
    
    Public instance variables:
        chLevel: int -- chapter level (part/chapter).
        chType: int -- chapter type (Normal/Notes/Todo/Unused).
        suppressChapterTitle: bool -- uppress chapter title when exporting.
        isTrash: bool -- True, if the chapter is the project's trash bin.
        suppressChapterBreak: bool -- Suppress chapter break when exporting.
        srtScenes: list of str -- the chapter's sorted scene IDs.        
    """

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self.chLevel: int = None
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.chType: int = None
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo
        # 3= Unused
        # Applies to projects created by yWriter version 7.0.7.2+.
        #
        # xml: <ChapterType>
        # xml: <Type>
        # xml: <Unused>
        #
        # This is how yWriter 7.1.3.0 reads the chapter type:
        #
        # Type   |<Unused>|<Type>|<ChapterType>|chType
        # -------+--------+------+--------------------
        # Normal | N/A    | N/A  | N/A         | 0
        # Normal | N/A    | 0    | N/A         | 0
        # Notes  | x      | 1    | N/A         | 1
        # Unused | -1     | 0    | N/A         | 3
        # Normal | N/A    | x    | 0           | 0
        # Notes  | x      | x    | 1           | 1
        # Todo   | x      | x    | 2           | 2
        # Unused | -1     | x    | x           | 3
        #
        # This is how yWriter 7.1.3.0 writes the chapter type:
        #
        # Type   |<Unused>|<Type>|<ChapterType>|chType
        #--------+--------+------+-------------+------
        # Normal | N/A    | 0    | 0           | 0
        # Notes  | -1     | 1    | 1           | 1
        # Todo   | -1     | 1    | 2           | 2
        # Unused | -1     | 1    | 0           | 3

        self.suppressChapterTitle: bool = None
        # xml: <Fields><Field_SuppressChapterTitle> 1
        # True: Chapter heading not to be displayed in written document.
        # False: Chapter heading to be displayed in written document.

        self.isTrash: bool = None
        # xml: <Fields><Field_IsTrash> 1
        # True: This chapter is the yw7 project's "trash bin".
        # False: This chapter is not a "trash bin".

        self.suppressChapterBreak: bool = None
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes: list[str] = []


        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.
from typing import Pattern

#--- Regular expressions for counting words and characters like in LibreOffice.
# See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html

ADDITIONAL_WORD_LIMITS: Pattern = re.compile('--|—|–')
# this is to be replaced by spaces, thus making dashes and dash replacements word limits

NO_WORD_LIMITS: Pattern = re.compile('\[.+?\]|\/\*.+?\*\/|-|^\>', re.MULTILINE)
# this is to be replaced by empty strings, thus excluding markup and comments from
# word counting, and making hyphens join words

NON_LETTERS: Pattern = re.compile('\[.+?\]|\/\*.+?\*\/|\n|\r')
# this is to be replaced by empty strings, thus excluding markup, comments, and linefeeds
# from letter counting


class Scene(BasicElement):
    """yWriter scene representation.
    
    Public instance variables:
        sceneContent: str -- scene content (property with getter and setter).
        wordCount: int -- word count (derived; updated by the sceneContent setter).
        letterCount: int -- letter count (derived; updated by the sceneContent setter).
        scType: int -- Scene type (Normal/Notes/Todo/Unused).
        doNotExport: bool -- True if the scene is not to be exported to RTF.
        status: int -- scene status (Outline/Draft/1st Edit/2nd Edit/Done).
        notes: str -- scene notes in a single string.
        tags -- list of scene tags. 
        field1: int -- scene ratings field 1.
        field2: int -- scene ratings field 2.
        field3: int -- scene ratings field 3.
        field4: int -- scene ratings field 4.
        appendToPrev: bool -- if True, append the scene without a divider to the previous scene.
        isReactionScene: bool -- if True, the scene is "reaction". Otherwise, it's "action". 
        isSubPlot: bool -- if True, the scene belongs to a sub-plot. Otherwise it's main plot.  
        goal: str -- the main actor's scene goal. 
        conflict: str -- what hinders the main actor to achieve his goal.
        outcome: str -- what comes out at the end of the scene.
        characters -- list of character IDs related to this scene.
        locations -- list of location IDs related to this scene. 
        items -- list of item IDs related to this scene.
        date: str -- specific start date in ISO format (yyyy-mm-dd).
        time: str -- specific start time in ISO format (hh:mm).
        minute: str -- unspecific start time: minutes.
        hour: str -- unspecific start time: hour.
        day: str -- unspecific start time: day.
        lastsMinutes: str -- scene duration: minutes.
        lastsHours: str -- scene duration: hours.
        lastsDays: str -- scene duration: days. 
        image: str --  path to an image related to the scene. 
    """
    STATUS: set = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')
    # Emulate an enumeration for the scene status
    # Since the items are used to replace text,
    # they may contain spaces. This is why Enum cannot be used here.

    ACTION_MARKER: str = 'A'
    REACTION_MARKER: str = 'R'
    NULL_DATE: str = '0001-01-01'
    NULL_TIME: str = '00:00:00'

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self._sceneContent: str = None
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.wordCount: int = 0
        # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount: int = 0
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.scType: int = None
        # Scene type (Normal/Notes/Todo/Unused).
        #
        # xml: <Unused>
        # xml: <Fields><Field_SceneType>
        #
        # This is how yWriter 7.1.3.0 reads the scene type:
        #
        # Type   |<Unused>|Field_SceneType>|scType
        #--------+--------+----------------+------
        # Notes  | x      | 1              | 1
        # Todo   | x      | 2              | 2
        # Unused | -1     | N/A            | 3
        # Unused | -1     | 0              | 3
        # Normal | N/A    | N/A            | 0
        # Normal | N/A    | 0              | 0
        #
        # This is how yWriter 7.1.3.0 writes the scene type:
        #
        # Type   |<Unused>|Field_SceneType>|scType
        #--------+--------+----------------+------
        # Normal | N/A    | N/A            | 0
        # Notes  | -1     | 1              | 1
        # Todo   | -1     | 2              | 2
        # Unused | -1     | 0              | 3

        self.doNotExport: bool = None
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status: int = None
        # xml: <Status>
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        # See also the STATUS list for conversion.

        self.notes: str = None
        # xml: <Notes>

        self.tags: list[str] = None
        # xml: <Tags>

        self.field1: str = None
        # xml: <Field1>

        self.field2: str = None
        # xml: <Field2>

        self.field3: str = None
        # xml: <Field3>

        self.field4: str = None
        # xml: <Field4>

        self.appendToPrev: bool = None
        # xml: <AppendToPrev> -1

        self.isReactionScene: bool = None
        # xml: <ReactionScene> -1

        self.isSubPlot: bool = None
        # xml: <SubPlot> -1

        self.goal: str = None
        # xml: <Goal>

        self.conflict: str = None
        # xml: <Conflict>

        self.outcome: str = None
        # xml: <Outcome>

        self.characters: list[str] = None
        # xml: <Characters><CharID>

        self.locations: list[str] = None
        # xml: <Locations><LocID>

        self.items: list[str] = None
        # xml: <Items><ItemID>

        self.date: str = None
        # yyyy-mm-dd
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time: str = None
        # hh:mm:ss
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.day: str = None
        # xml: <Day>

        self.lastsMinutes: str = None
        # xml: <LastsMinutes>

        self.lastsHours: str = None
        # xml: <LastsHours>

        self.lastsDays: str = None
        # xml: <LastsDays>

        self.image: str = None
        # xml: <ImageFile>

        self.scnArcs: str = None
        # xml: <Field_SceneArcs>
        # Semicolon-separated arc titles.
        # Example: 'A' for 'A-Storyline'.
        # If the scene is "Todo" type, an assigned single arc
        # should be defined by it.

        self.scnStyle: str = None
        # xml: <Field_SceneStyle>
        # Mode of discourse. May be 'explaining', 'descriptive', or 'summarizing'.
        # None is the default, meaning 'staged'.
        # TODO: Change the wording and use "Mode" instead of "Style".

    @property
    def sceneContent(self) -> str:
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text: str):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
        text = NO_WORD_LIMITS.sub('', text)
        wordList = text.split()
        self.wordCount = len(wordList)
        text = NON_LETTERS.sub('', self._sceneContent)
        self.letterCount = len(text)


class WorldElement(BasicElement):
    """Story world element representation (may be location or item).
    
    Public instance variables:
        image: str -- image file path.
        tags -- list of tags.
        aka: str -- alternate name.
    """

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self.image: str = None
        # xml: <ImageFile>

        self.tags: list[str] = None
        # xml: <Tags>

        self.aka: str = None
        # xml: <AKA>


class Character(WorldElement):
    """yWriter character representation.

    Public instance variables:
        notes: str -- character notes.
        bio: str -- character biography.
        goals: str -- character's goals in the story.
        fullName: str -- full name (the title inherited may be a short name).
        isMajor: bool -- True, if it's a major character.
    """
    MAJOR_MARKER: str = 'Major'
    MINOR_MARKER: str = 'Minor'

    def __init__(self):
        """Extends the superclass constructor by adding instance variables."""
        super().__init__()

        self.notes: str = None
        # xml: <Notes>

        self.bio: str = None
        # xml: <Bio>

        self.goals: str = None
        # xml: <Goals>

        self.fullName: str = None
        # xml: <FullName>

        self.isMajor: bool = None
        # xml: <Major>


LANGUAGE_TAG: Pattern = re.compile('\[lang=(.*?)\]')


class Novel(BasicElement):
    """Novel representation.

    This class represents a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        get_languages() -- Determine the languages used in the document.
        check_locale() -- Check the document's locale (language code and country code).

    Public instance variables:
        authorName: str -- author's name.
        author bio: str -- information about the author.
        fieldTitle1: str -- scene rating field title 1.
        fieldTitle2: str -- scene rating field title 2.
        fieldTitle3: str -- scene rating field title 3.
        fieldTitle4: str -- scene rating field title 4.
        chapters: dict -- (key: ID; value: chapter instance).
        scenes: dict -- (key: ID, value: scene instance).
        srtChapters: list -- the novel's sorted chapter IDs.
        locations: dict -- (key: ID, value: WorldElement instance).
        srtLocations: list -- the novel's sorted location IDs.
        items: dict -- (key: ID, value: WorldElement instance).
        srtItems: list -- the novel's sorted item IDs.
        characters: dict -- (key: ID, value: character instance).
        srtCharacters: list -- the novel's sorted character IDs.
        projectNotes: dict --  (key: ID, value: projectNote instance).
        srtPrjNotes: list -- the novel's sorted project notes.
    """

    def __init__(self):
        """Initialize instance variables.
            
        Extends the superclass constructor.          
        """
        super().__init__()

        self.authorName: str = None
        # xml: <PROJECT><AuthorName>

        self.authorBio: str = None
        # xml: <PROJECT><Bio>

        self.fieldTitle1: str = None
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2: str = None
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3: str = None
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4: str = None
        # xml: <PROJECT><FieldTitle4>

        self.wordTarget: int = None
        # xml: <PROJECT><wordTarget>

        self.wordCountStart: int = None
        # xml: <PROJECT><wordCountStart>

        self.wordTarget: int = None
        # xml: <PROJECT><wordCountStart>

        self.chapters: dict[str, Chapter] = {}
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter instance.
        # The order of the elements does not matter (the novel's order of the chapters is defined by srtChapters)

        self.scenes: dict[str, Scene] = {}
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's order of the scenes is defined by
        # the order of the chapters and the order of the scenes within the chapters)

        self.languages: list[str] = None
        # List of non-document languages occurring as scene markup.
        # Format: ll-CC, where ll is the language code, and CC is the country code.

        self.srtChapters: list[str] = []
        # The novel's chapter IDs. The order of its elements corresponds to the novel's order of the chapters.

        self.locations: dict[str, WorldElement] = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtLocations: list[str] = []
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items: dict[str, WorldElement] = {}
        # xml: <ITEMS>
        # key = item ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtItems: list[str] = []
        # The novel's item IDs. The order of its elements corresponds to the XML project file.

        self.characters: dict[str, Character] = {}
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters: list[str] = []
        # The novel's character IDs. The order of its elements corresponds to the XML project file.

        self.projectNotes: dict[str, BasicElement] = {}
        # xml: <PROJECTNOTES>
        # key = note ID, value = note instance.
        # The order of the elements does not matter.

        self.srtPrjNotes: list[str] = []
        # The novel's projectNote IDs. The order of its elements corresponds to the XML project file.

        self.languageCode: str = None
        # Language code acc. to ISO 639-1.

        self.countryCode: str = None
        # Country code acc. to ISO 3166-2.

    def get_languages(self):
        """Determine the languages used in the document.
        
        Populate the self.languages list with all language codes found in the scene contents.        
        Example:
        - language markup: 'Standard text [lang=en-AU]Australian text[/lang=en-AU].'
        - language code: 'en-AU'
        """

        def languages(text: str) -> Iterator[str]:
            """Return the language codes appearing in text.
            
            Example:
            - language markup: 'Standard text [lang=en-AU]Australian text[/lang=en-AU].'
            - language code: 'en-AU'
            """
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
        """Check the document's locale (language code and country code).
        
        If the locale is missing, set the system locale.  
        If the locale doesn't look plausible, set "no language".        
        """
        if not self.languageCode:
            # Language isn't set.
            try:
                sysLng, sysCtr = locale.getlocale()[0].split('_')
            except:
                # Fallback for old Windows versions.
                sysLng, sysCtr = locale.getdefaultlocale()[0].split('_')
            self.languageCode = sysLng
            self.countryCode = sysCtr
            return

        try:
            # Plausibility check: code must have two characters.
            if len(self.languageCode) == 2:
                if len(self.countryCode) == 2:
                    return
                    # keep the setting
        except:
            # code isn't a string
            pass
        # Existing language or country field looks not plausible
        self.languageCode = 'zxx'
        self.countryCode = 'none'


class YwCnvUi:
    """Base class for Novel file conversion with user interface.

    Public methods:
        export_from_yw(sourceFile, targetFile) -- Convert from yWriter project to other file format.
        create_yw(sourceFile, targetFile) -- Create target from source.
        import_to_yw(sourceFile, targetFile) -- Convert from any file format to yWriter project.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        newFile: str -- path to the target file in case of success.   
    """

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.
        self.newFile = None
        # Also indicates successful conversion.

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
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
        """Create target from source.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf target already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """
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
        """Convert from any file format to yWriter project.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
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
        """Return boolean permission to overwrite the target file.
        
        Positional arguments:
            fileName -- path to the target file.
        
        Overrides the superclass method.
        """
        return self.ui.ask_yes_no(_('Overwrite existing file "{}"?').format(norm_path(filePath)))

    def _open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        open_document(self.newFile)
        sys.exit(0)

    def check(self, source, target):
        """Error handling:
        
        - Check if source and target are correctly initialized.
        - Ask for permission to overwrite target.
        - Raise the "Error" exception in case of error. 
        """
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
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        read() -- Parse the file and get the instance variables.
        write() -- Write instance variables to the file.

    Public instance variables:
        projectName: str -- URL-coded file name without suffix and extension. 
        projectPath: str -- URL-coded path to the project directory. 
        scenesSplit: bool -- True, if a scene or chapter is split during merging.
        filePath: str -- path to the file (property with getter and setter). 

    Public class constants:
        PRJ_KWVAR -- List of the names of the project keyword variables.
        CHP_KWVAR -- List of the names of the chapter keyword variables.
        SCN_KWVAR -- List of the names of the scene keyword variables.
        CRT_KWVAR -- List of the names of the character keyword variables.
        LOC_KWVAR -- List of the names of the location keyword variables.
        ITM_KWVAR -- List of the names of the item keyword variables.
        PNT_KWVAR -- List of the names of the project note keyword variables.
    """
    DESCRIPTION = _('File')
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    PRJ_KWVAR = []
    CHP_KWVAR = []
    SCN_KWVAR = []
    CRT_KWVAR = []
    LOC_KWVAR = []
    ITM_KWVAR = []
    PNT_KWVAR = []
    # Keyword variables for custom fields in the .yw7 XML file.

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath: str -- path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.  
            
        Extends the superclass constructor.          
        """
        super().__init__()
        self.novel = None

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a supported type as specified by EXTENSION.

        self.projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self.projectPath = None
        # str
        # URL-coded path to the project directory.

        self.scenesSplit = False
        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.
                
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            try:
                head, tail = os.path.split(os.path.realpath(filePath))
                # realpath() completes relative paths, but may not work on virtual file systems.
            except:
                head, tail = os.path.split(filePath)
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        """Parse the file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        This is a stub to be overridden by subclass methods.
        """
        raise NotImplementedError

    def write(self):
        """Write instance variables to the file.
        
        Raise the "Error" exception in case of error. 
        This is a stub to be overridden by subclass methods.
        """
        raise NotImplementedError

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick: bool -- if True, apply a conversion mode for one-liners without formatting.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()

    def _convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()


def indent(elem, level=0):
    """xml pretty printer

    Kudos to to Fredrik Lundh. 
    Source: http://effbot.org/zone/element-lib.htm#prettyprint
    """
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
    """Hold a list of novelWriter compatible handles.
    
    The only purpose of this list is to use unique handles.
    Therefore, it is not intended to delete members.
    """
    HANDLE_CHARS = list('abcdef0123456789')
    SIZE = 13

    def __init__(self):
        """Initialize the list of handles."""
        self._handles = []

    def has_member(self, handle):
        """Return True if handle is in the list of handles."""
        return handle in self._handles

    def add_member(self, handle):
        """Add handle to the list, if unique and compliant.
        
        Return True on success.
        Return False if handle is not accepted for any reason.
        """
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
        """Create a handle derived from text and add it to the list of handles.

        Positional arguments:
            text -- string from which the handle is derived.
        
        Return the handle.
        Use a non-random algorithm in order to faciliate testing.
        If text is not unique, a "salt" is varied until a unique handle is achieved. 
        """

        def create_handle(text, salt):
            """Return a handle for novelWriter.
            
            Positional arguments:
                text -- string from which the handle is derived.
                salt -- additional string to make the handle unique. 
            """
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
    """Abstract novelWriter item representation.
    
    Public instance variables:
        nwName -- str: name or title.
        nwType -- str: type (ROOT/FOLDER/FILE).
        nwClass -- str: class (NOVEL/CHARACTER/WORLD/OBJECT).
        nwStatus -- str: Scene editing status.
        nwImportance -- str: Character importance (major/minor).
        nwActive -- bool: if True, the item is exported by the application.
        nwLayout -- str: layout (DOCUMENT/NOTE).
        nwCharCount -- int: character count.
        nwWordCount -- int: word count.
        nwParaCount -- (not used for conversion).
        nwCursorPos -- (not used for conversion).
        nwHandle -- str: this item's handle.
        nwOrder -- int: sort order.
        nwParent -- str: the parent item's handle.
    
    File format specific classes inherit from this.
    """

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
    """novelWriter item representation.
    
    Strategy class for file format version 1.5.
    """

    def read(self, node, master):
        """Read a novelWriter node entry from the XML project tree. 
        
        Positional arguments: 
            node -- ElementTree element instance
        
        Return the handle.
        """
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
        """Write a novelWriter item entry to the XML project tree.
        
        Positional arguments: 
            parentNode -- ElementTree element instance: the new element's parent.

        Return a new ElementTree element instance.
        """
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
    """abstract novelWriter item file representation.
    
    Public methods:
        read() -- read a content file.
        write() -- write a content file.
    """
    EXTENSION = '.nwd'

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        
        """
        self._prj = prj
        self._nwItem = nwItem
        self._filePath = os.path.dirname(self._prj.filePath) + self._prj.CONTENT_DIR + nwItem.nwHandle + self.EXTENSION
        self._lines = []

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        try:
            with open(self._filePath, 'r', encoding='utf-8') as f:
                self._lines = f.read().split('\n')
                return 'Item data read in.'

        except:
            raise Error(f'Can not read "{norm_path(self._filePath)}".')

    def write(self):
        """Write a content file. 
        
        Return a message beginning with the ERROR constant in case of error.
        """
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
    """novelWriter character file representation.
    
    Public methods:
        read() -- read a content file.
        add_element(crId) -- add a character to the file content.
    """

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        
        
        Required keyword arguments from prj:
            major_character_status -- tuple of str: novelWriter status meaning "Major" character importance in yWriter.
            character_notes_heading -- str: heading for novelWriter text that is converted to yWriter character notes.
            character_goals_heading -- str: heading for novelWriter text that is converted to yWriter character goals.
            character_bio_heading -- str: heading for novelWriter text that is converted to yWriter character bio.
            ywriter_aka_keyword -- str: keyword for 'aka' pseudo tag in novelWriter, signifying an alternative name.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.
            Extends the superclass constructor.
        """
        super().__init__(prj, nwItem)

        # Customizable Character importance.
        self._majorImportance = prj.kwargs['major_character_status']

        # Headings that divide the character sheet into sections.
        self._characterNotesHeading = prj.kwargs['character_notes_heading']
        self._characterGoalsHeading = prj.kwargs['character_goals_heading']
        self._characterBioHeading = prj.kwargs['character_bio_heading']

        # Customizable tags for characters and locations.
        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        Extends the superclass method.
        """
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
        """Add a character to the file content.
        
        Positional arguments:
            crId -- str: character ID.
        """
        character = self._prj.novel.characters[crId]

        # Set Heading.
        if character.fullName:
            title = character.fullName
        else:
            title = character.title
        self._lines.append(f'# {title}\n')

        # Set tag.
        self._lines.append(f'@tag: {character.title.replace(" ", "_")}')

        # Set yWriter AKA.
        if character.aka:
            self._lines.append(self._ywAkaKeyword + character.aka)

        # Set yWriter tags.
        if character.tags is not None:
            for tag in character.tags:
                self._lines.append(self._ywTagKeyword + tag)

        # Set yWriter description.
        if character.desc:
            self._lines.append(f'\n{character.desc}')

        # Set yWriter bio.
        if character.bio:
            self._lines.append(f'\n{self._characterBioHeading}')
            self._lines.append(character.bio)

        # Set yWriter goals.
        if character.goals:
            self._lines.append(f'\n{self._characterGoalsHeading}')
            self._lines.append(character.goals)

        # Set yWriter notes.
        if character.notes:
            self._lines.append(f'\n{self._characterNotesHeading}')
            self._lines.append(character.notes)


class NwdNovelFile(NwdFile):
    """novelWriter novel file representation.
    
    Public methods:
        read() -- read a content file.
        add_scene(scId) -- add a scene to the file content.
        add_chapter(chId) -- add a chapter to the file content.
    """
    _POV_TAG = '@pov: '
    _CHARACTER_TAG = '@char: '
    _LOCATION_TAG = '@location: '
    _ITEM_TAG = '@object: '
    _SYNOPSIS_KEYWORD = 'synopsis:'

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        

        Required keyword arguments from prj:
            outline_status -- tuple of str: novelWriter status to be converted to yWriter "Outline" scene status.
            draft_status -- tuple of str: novelWriter status to be converted to yWriter "Draft" scene status.
            first_edit_status -- tuple of str: novelWriter status to be converted to yWriter "1st Edit" scene status.
            second_edit_status -- tuple of str: novelWriter status to be converted to yWriter "2nd Edit" scene status.
            done_status -- tuple of str: novelWriter status to be converted to yWriter "Done" scene status.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.     

        Extends the superclass constructor.
        """
        super().__init__(prj, nwItem)

        # Conversion options.
        self.doubleLinebreaks = prj.kwargs['double_linebreaks']

        # Scene status mapping.
        self._outlineStatus = prj.kwargs['outline_status']
        self._draftStatus = prj.kwargs['draft_status']
        self._firstEditStatus = prj.kwargs['first_edit_status']
        self._secondEditStatus = prj.kwargs['second_edit_status']
        self._doneStatus = prj.kwargs['done_status']

        # Customizable tags for general use.
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

        # Headings that divide the file into parts, chapters and scenes.
        # self.partHeadingPrefix = prj.kwargs['part_heading_prefix']
        # self.chapterHeadingPrefix = prj.kwargs['chapter_heading_prefix']
        # self.sceneHeadingPrefix = prj.kwargs['scene_heading_prefix']
        # self.sectionHeadingPrefix = prj.kwargs['section_heading_prefix']

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to Markdown.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if quick:
            # Just clean up a one-liner without sophisticated formatting.
            if text is None:
                return ''
            else:
                return text

        # Convert italics, bold, and strikethrough.
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
            # Remove highlighting, alignment, and underline tags
        except AttributeError:
            text = ''
        return text

    def _convert_to_yw(self, text):
        """Return text, converted from Markdown to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        Overrides the superclass method.
        """

        # Convert bold, italics, and strikethrough.
        text = re.sub('\*\*(.+?)\*\*', '[b]\\1[/b]', text)
        text = re.sub('\_([^ ].+?[^ ])\_', '[i]\\1[/i]', text)
        text = re.sub('\~\~(.+?)\~\~', '[s]\\1[/s]', text)

        # Text alignment in yWriter is more complicated than it seems
        # at first glance, so don't support it for now.
        # text = re.sub('\>\>(.+?)\<\<\n', '[c]\\1\n[/c]', text)
        # text = re.sub('\>\>(.+?)\<\<', '[c]\\1', text)
        # text = re.sub('\>\>(.+?)\n', '[r]\\1\n[/r]', text)
        # text = re.sub('\>\>(.+?)', '[r]\\1', text)
        # text = text.replace('<<', '')

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
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        Extends the superclass method.
        """

        def set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags):
            if scId is not None:
                text = '\n'.join(contentLines)
                self._prj.novel.scenes[scId].sceneContent = self._convert_to_yw(text)
                self._prj.novel.scenes[scId].desc = '\n'.join(synopsis)
                self._prj.novel.scenes[scId].characters = characters
                self._prj.novel.scenes[scId].locations = locations
                self._prj.novel.scenes[scId].items = items
                self._prj.novel.scenes[scId].tags = tags

        #--- Get chapters and scenes.
        scId = None
        super().read()

        # Determine the attibutes for all chapters and scenes included.
        elementType = None
        status = None
        if self._nwItem.nwLayout == 'DOCUMENT' and self._nwItem.nwActive:
            elementType = 0
            # Normal
        elif self._nwItem.nwLayout == 'NOTE':
            elementType = 1
            # Notes
        else:
            elementType = 3
            # Unused
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
                # Set previous scene content.
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
                # Set previous scene content.
                set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags)
                synopsis = []

                # Add a chapter.
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

                # Prepare the next scene that may be appended without a heading.
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
                # Write chapter synopsis.
                if synopsis and not inScene:
                    self._prj.novel.chapters[self._prj.chId].desc = '\n'.join(synopsis)
                    synopsis = []
                inScene = True

                # Add a scene.
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

        # Write the last scene of the file or a chapter synopsis, if there is no scene.
        if scId is not None:
            set_scene_content(scId, contentLines, characters, locations, items, synopsis, tags)
        elif synopsis:
            self._prj.novel.chapters[self._prj.chId].desc = '\n'.join(synopsis)
        return 'Chapters and scenes read in.'

    def add_scene(self, scId):
        """Add a scene to the file content.
        
        Positional arguments:
            scId -- str: scene ID.
        """
        scene = self._prj.novel.scenes[scId]
        if scene.appendToPrev:
            self._lines.append(f'#### {scene.title}\n')
        else:
            self._lines.append(f'### {scene.title}\n')

        # Set point of view and characters.
        if scene.characters is not None:
            isViewpoint = True
            for crId in scene.characters:
                if isViewpoint:
                    self._lines.append(self._POV_TAG + self._prj.novel.characters[crId].title.replace(' ', '_'))
                    isViewpoint = False
                else:
                    self._lines.append(self._CHARACTER_TAG + self._prj.novel.characters[crId].title.replace(' ', '_'))

        # Set locations.
        if scene.locations is not None:
            for lcId in scene.locations:
                self._lines.append(self._LOCATION_TAG + self._prj.novel.locations[lcId].title.replace(' ', '_'))

        # Set items.
        if scene.items is not None:
            for itId in scene.items:
                self._lines.append(self._ITEM_TAG + self._prj.novel.items[itId].title.replace(' ', '_'))

        # Set yWriter tags.
        if scene.tags is not None:
            for tag in scene.tags:
                self._lines.append(self._ywTagKeyword + tag)

        # Set synopsis.
        if scene.desc:
            synopsis = scene.desc.replace('\n', '\t')
            self._lines.append(f'\n% {self._SYNOPSIS_KEYWORD} {synopsis}')

        # Separate the text body by a blank line.
        self._lines.append('\n')

        # Set scene content.
        text = self._convert_from_yw(scene.sceneContent)
        if text:
            self._lines.append(text)

    def add_chapter(self, chId):
        """Add a chapter to the file content.
        
        Positional arguments:
            chId -- str: chapter ID.
        """
        chapter = self._prj.novel.chapters[chId]
        if chapter.chLevel == 0:
            self._lines.append(f'## {chapter.title}\n')
        else:
            self._lines.append(f'# {chapter.title}\n')

        # Set yWriter chapter description.
        if chapter.desc:
            synopsis = chapter.desc.replace('\n', '\t')
            self._lines.append(f'\n% {self._SYNOPSIS_KEYWORD} {synopsis}\n')


class NwdWorldFile(NwdFile):
    """novelWriter world file representation.
    
    Public methods:
        read() -- read a content file.
        add_element(lcId) -- add a location to the file content.
    """

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        
        
        Required keyword arguments from prj:
            ywriter_aka_keyword -- str: keyword for 'aka' pseudo tag in novelWriter, signifying an alternative name.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.

        Extends the superclass constructor.
        """
        super().__init__(prj, nwItem)

        # Customizable tags for characters and locations.
        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        Extends the superclass method.
        """
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
        """Add a location to the file content.
        
        Positional arguments:
            lcId -- str: location ID.
        """
        location = self._prj.novel.locations[lcId]

        # Set Heading.
        self._lines.append(f'# {location.title}\n')

        # Set tag.
        self._lines.append(f'@tag: {location.title.replace(" ", "_")}')

        # Set yWriter AKA.
        if location.aka:
            self._lines.append(self._ywAkaKeyword + location.aka)

        # Set yWriter tags.
        if location.tags is not None:
            for tag in location.tags:
                self._lines.append(self._ywTagKeyword + tag)

        # Set yWriter description.
        if location.desc:
            self._lines.append(f'\n{location.desc}')
        return super().write()


class NwdObjectFile(NwdFile):
    """novelWriter object file representation.
    
    Public methods:
        read() -- read a content file.
        add_element(itId) -- add an element of the story world to the file content.
    """

    def __init__(self, prj, nwItem):
        """Define instance variables.
        
        Positional arguments:
            prj -- NwxFile instance: the novelWriter project represenation.
            nwItem -- NwItem instance associated with the .nwd file.        

        Required keyword arguments from prj:
            ywriter_aka_keyword -- str: keyword for 'aka' pseudo tag in novelWriter, signifying an alternative name.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.

        Extends the superclass constructor.
        """
        super().__init__(prj, nwItem)

        # Customizable tags for characters and items.
        self._ywAkaKeyword = f'%{prj.kwargs["ywriter_aka_keyword"]}: '
        self._ywTagKeyword = f'%{prj.kwargs["ywriter_tag_keyword"]}: '

    def read(self):
        """Read a content file.
        
        Return a message beginning with the ERROR constant in case of error.
        Extends the superclass method.
        """
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
        """Add an element of the story world to the file content.
         
        Positional arguments:
            itId -- str: item ID.
       """
        item = self._prj.novel.items[itId]

        # Set Heading.
        self._lines.append(f'# {item.title}\n')

        # Set tag.
        self._lines.append(f'@tag: {item.title.replace(" ", "_")}')

        # Set yWriter AKA.
        if item.aka:
            self._lines.append(self._ywAkaKeyword + item.aka)

        # Set yWriter tags.
        if item.tags is not None:
            for tag in item.tags:
                self._lines.append(self._ywTagKeyword + tag)

        # Set yWriter description.
        if item.desc:
            self._lines.append(f'\n{item.desc}')
        return super().write()


WRITE_NEW_FORMAT = True


class NwxFile(File):
    """novelWriter project representation.
    
    Public methods:
        read_xml_file() -- read the novelWriter XML project file to the project tree.
        read() -- parse the novelWriter xml and md files and get the instance variables.
        merge(source) -- copy the yWriter project parts that can be mapped to the novelWriter project.
        write() -- write instance variables to the novelWriter files.
    
    Public class variables:
        EXTENSION -- str: file extension of the novelWriter xml file. 
        DESCRIPTION -- str: file description that can be displayed.
        SUFFIX -- str: file name suffix (not applicable).
        CONTENT_DIR -- str: relative path to the "content" directory.
        CONTENT_EXTENSION -- str: extension of the novelWriter markdown files.

    Public instance variables:
        nwHandles -- Handles instance (list of handles with methods).
        kwargs -- keyword arguments, holding settings and options.
        lcCount -- int: number of locations. 
        crCount -- int: number of characters.
        itCount -- int: number of items.
        scCount -- int: number of scenes.
        chCount -- int: number of characters.
        chId -- str: ID of the chapter currently processed.
    
    Reads and writes file format version 1.3.
    Reads file format version 1.4.
    """
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
        """Initialize instance variables.
        
        Positional arguments:
            filePath -- str: path to the yw7 file.
        
        Required keyword arguments:
            scene_status -- tuple of scene status (emulating an enumeration).    
            major_character_status -- tuple of str: novelWriter status meaning "Major" character importance in yWriter.
            character_notes_heading -- str: heading for novelWriter text that is converted to yWriter character notes.
            character_goals_heading -- str: heading for novelWriter text that is converted to yWriter character goals.
            character_bio_heading -- str: heading for novelWriter text that is converted to yWriter character bio.
            ywriter_aka_keyword -- str: keyword for 'aka' pseudo tag in novelWriter, signifying an alternative name.
            ywriter_tag_keyword -- str: keyword for 'tag' pseudo tag in novelWriter, signifying a yWriter tag.
            outline_status -- tuple of str: novelWriter status to be converted to yWriter "Outline" scene status.
            draft_status -- tuple of str: novelWriter status to be converted to yWriter "Draft" scene status.
            first_edit_status -- tuple of str: novelWriter status to be converted to yWriter "1st Edit" scene status.
            second_edit_status -- tuple of str: novelWriter status to be converted to yWriter "2nd Edit" scene status.
            done_status -- tuple of str: novelWriter status to be converted to yWriter "Done" scene status.
    
        Extends the superclass constructor.
        """
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
        """Read the novelWriter XML project file to the project tree.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        try:
            self._tree = ET.parse(self.filePath)
        except:
            raise Error(f'Can not process "{norm_path(self.filePath)}".')

    def read(self):
        """Parse the novelWriter xml and md files and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        #--- Read the XML file, if necessary.
        if self._tree is None:
            self.read_xml_file()
        root = self._tree.getroot()

        #--- Check file type and version; apply strategy pattern for the NwItem class.
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

        #--- Read project metadata from the xml element _tree.
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

        #--- Read project content from the xml element tree.
        # This is a simple variant that processes the flat XML structure
        # without evaluating the items' child/parent relations.
        # Assumptions:
        # - The NOVEL items are arranged in the correct order.
        # - ARCHIVE and TRASH sections are located at the end.
        content = root.find('content')
        for node in content.iter('item'):
            nwItem = NwItem()
            handle = nwItem.read(node, self)
            if not self.nwHandles.add_member(handle):
                raise Error(f'Invalid handle: {handle}')

            if nwItem.nwClass in self._TRAILER:
                # Discard the rest of the scenes, if any.
                break

            if nwItem.nwType != 'FILE':
                continue

            nwdFile = self._NWD_CLASSES[nwItem.nwClass](self, nwItem)
            nwdFile.read()

        # Create reference lists.
        crIdsByTitle = {}
        for crId in self.novel.characters:
            crIdsByTitle[self.novel.characters[crId].title] = crId
        lcIdsByTitle = {}
        for lcId in self.novel.locations:
            lcIdsByTitle[self.novel.locations[lcId].title] = lcId
        itIdsByTitle = {}
        for itId in self.novel.items:
            itIdsByTitle[self.novel.items[itId].title] = itId

        # Fix scene references, replacing titles by IDs.
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
        """Write instance variables to the novelWriter files.
        
        Return a message beginning with the ERROR constant in case of error.
        Override the superclass method.
        """

        def write_entry(parent, entry, red, green, blue, map):
            """Write an XML entry with RGB values as attributes.
            """
            attrib = {}
            attrib['key'] = map[entry]
            attrib['count'] = '0'
            attrib['blue'] = str(blue)
            attrib['green'] = str(green)
            attrib['red'] = str(red)
            ET.SubElement(parent, 'entry', attrib).text = entry

        root = ET.Element(self._NWX_TAG, self._NWX_ATTR_V1_5)
        NwItem = NwItemV15

        #--- Write project metadata.
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

        #--- Write settings.
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

        #--- Write content.
        content = ET.SubElement(root, 'content')
        attrCount = 0
        order = [0]
        # Use a list as a stack for the order within a level

        #--- Write novel folder.
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
        # content level
        hasPartLevel = False
        isInChapter = False

        # Add novel items to the folder.
        order.append(0)
        # Level up from content to novel
        for chId in self.novel.srtChapters:
            if self.novel.chapters[chId].chLevel == 1:
                # Begin with a new part.
                hasPartLevel = True
                isInChapter = False

                #--- Write a new folder for this part.
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
                # novel level
                order.append(0)
                # Level up from novel to part

                # Put the heading into the part folder.
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

                # Add it to the .nwd file.
                nwdFile = NwdNovelFile(self, partHeading)
                nwdFile.add_chapter(chId)
                nwdFile.write()
                attrCount += 1
                order[-1] += 1
                # part level

                order.append(0)
                # Level up from part to chapter
            else:
                # Begin with a new chapter.
                isInChapter = True

                #--- Write a new folder for this chapter.
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
                # part or novel level
                order.append(0)
                # Level up from part or novel to chapter

                # Put the heading into the folder.
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

                # Add it to the .nwd file.
                nwdFile = NwdNovelFile(self, chapterHeading)
                nwdFile.add_chapter(chId)
                nwdFile.write()
                attrCount += 1
                order[-1] += 1
                # chapter level
            for scId in self.novel.chapters[chId].srtScenes:
                #--- Put a scene into the folder.
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

                # Add it to the .nwd file.
                nwdFile = NwdNovelFile(self, scene)
                nwdFile.add_scene(scId)
                nwdFile.write()
                attrCount += 1
                order[-1] += 1
                # chapter or part level
            order.pop()
            # Level down from chapter to part or from part to novel
        order.pop()
        # Level down from novel to content

        #--- Write character folder.
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

        # Add character items to the folder.
        order.append(0)
        # Level up from world to character
        for crId in self.novel.srtCharacters:
            #--- Put a character into the folder.
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

            # Add it to the .nwd file.
            nwdFile = NwdCharacterFile(self, character)
            nwdFile.add_character(crId)
            nwdFile.write()

            attrCount += 1
            order[-1] += 1
            # character level
        order.pop()
        # Level down from character to content

        #--- Write world folder.
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
        # content level

        # Add world items to the folder.
        order.append(0)
        # Level up from content to world
        for lcId in self.novel.srtLocations:
            #--- Put a location into the folder.
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

            # Add it to the .nwd file.
            nwdFile = NwdWorldFile(self, location)
            nwdFile.add_element(lcId)
            nwdFile.write()
            attrCount += 1
            order[-1] += 1
            # world level
        order.pop()
        # Level down from world to to content

        #--- Write object folder.
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
        # content level

        # Add object items to the folder.
        order.append(0)
        # Level up from content to object
        for itId in self.novel.srtItems:
            #--- Put a item into the folder.
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

            # Add it to the .nwd file.
            nwdFile = NwdObjectFile(self, item)
            nwdFile.add_element(itId)
            nwdFile.write()
            attrCount += 1
            order[-1] += 1
            # object level
        order.pop()
        # Level down from object to to content

        # Write the content counter.
        content.set('count', str(attrCount))

        #--- Format and write the XML tree.
        indent(root)
        self._tree = ET.ElementTree(root)
        self._tree.write(self.filePath, xml_declaration=True, encoding='utf-8')
        return f'"{norm_path(self.filePath)}" written.'


from typing import Iterable


def create_id(elements: Iterable) -> str:
    """Return an unused ID for a new element.
    
    Positional arguments:
        elements -- list or dictionary containing all existing IDs
    """
    i = 1
    while str(i) in elements:
        i += 1
    return str(i)


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
        """Parse the FreeMind xml file, fetching the Novel attributes.
        
        Overrides the superclass method.
        """
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
    """A converter class for FreeMind mindmap import.

    Public methods:
        run(sourcePath, **kwargs) -- Create source and target objects and run conversion.
    """

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        Required keyword arguments: 
            (none)
        """
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
                _('Create a novelWriter project file from {0}\nNew project: "{1}"').format(sourceFile.DESCRIPTION, norm_path(targetFile.filePath)))
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
        ui = UiCmd('Converter between FreeMind and novelWriter @release')

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
