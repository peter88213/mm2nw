# mm2nw

## Features

This Python script generates a [novelWriter](https://novelwriter.io/) project from a 
[FreeMind](https://freemind.sourceforge.io/wiki/index.php/Main_Page) /
[Freeplane](https://docs.freeplane.org/) outline. 

- Convert three levels of the novel structure: Parts, chapters, and scenes.
- Convert a set of main characters.
- Convert a set of minor characters.
- Convert a set of locations.
- Convert a set of items.
- Make the node label the title of the converted element.
- Make the node notes the description of the converted element.
- The chapter/scene types can be set by specified icons.

## Requirements

- [Python](https://www.python.org/) version 3.6+.

## Download link

[https://raw.githubusercontent.com/peter88213/mm2nw/main/mm2nw.py](https://raw.githubusercontent.com/peter88213/mm2nw/main/mm2nw.py)


## Instructions for use

### Command line usage

You can either

- launch the program on the command line passing the mindmap file as an argument, or
- launch the program via a batch file.

usage: `mm2nw.py [-h] [--silent] Sourcefile`

#### positional arguments:

`Sourcefile` 

The path of the .mm file. 

#### optional arguments:

`-h, --help` 

show this help message and exit

`--silent` 

suppress error messages and the request to confirm overwriting


## Conversion rules

- Converts elements on three levels of the novel structure: Parts, chapters, and scenes.
- Scene status is *Outline*.
- Converts a set of main characters.
- Converts a set of minor characters.
- Converts a set of locations.
- Converts a set of items.
- Makes the node label the title of the converted element.
- Makes the node notes the description of the converted element.


### The levels of the mindmap tree

- On the first level, a node represents either a *part*, 
  or a collection of characters, locations, or items. The conversion of "Normal type parts" 
  can be suppressed with a configuration file entry, if you just want chapters and scenes. 
- On the second level, a node represents either a *chapter*, or a character/location/item. 
- On the third level. a node represents a *scene*. 

### The use of special icons

The conversion is controlled by nodes decorated with special icons:


#### On the first level

This icon marks the *Main characters* branch: 
![Main characters icon](Screenshots/icon_main_characters.png) 

This icon marks the *Minor characters* branch: 
![Minor characters icon](Screenshots/icon_minor_characters.png)

This icon marks the *Locations* branch: 
![Locations icon](Screenshots/icon_locations.png)

This icon marks the *Items* branch: 
![Items icon](Screenshots/icon_items.png)

#### On the first, second, or third level

This icon makes a node element and its children (if any) *Note* type: 
![Notes icon](Screenshots/icon_notes.png)

This icon makes a node element and its children (if any) *Note* type:
![Todo icon](Screenshots/icon_todo.png)

### Example mindmap

![Example mindmap](Screenshots/icons01.png)

## Credits

- Frederik Lundh published the [xml pretty print algorithm](http://effbot.org/zone/element-lib.htm#prettyprint).

## License

mm2nw is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).

---

## See also


### nw_metadata

Create a cross reference table with novelWriter metadata. 

[nw_metadata](https://github.com/peter88213/nw_metadata)


### odt2nw

Generate a novelWriter project from a work in progress written with e.g. LibreOffice.

[odt2nw](https://github.com/peter88213/odt2nw/)


### md2nw

Generate a novelWriter project from a work in progress written with any text editor or Markdown word processor.

[md2nw](https://github.com/peter88213/md2nw/)


### yw2nw

Converter between yWriter and novelWriter.

[![yw2nw](img/yw2nw.png)](https://peter88213.github.io/yw2nw/)



