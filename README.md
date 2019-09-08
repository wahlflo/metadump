# Metadump

Metadump is a command line utility which extracts and displays embedded metadata of various types of files.

## Features

* Extracting and displaying metadata of various types of files such as:
    - EXIF
    - PDF
    - XMP
    - Microsoft Office-Documents: Word, Excel, Powerpoint  (documents in the format before 2007 are not supported)
* Filtering of the extracted metadata
* Easy expandability for other types of files

## Prerequisites / Installing

These instructions will get you a copy of the project up and running Metadump on your machine. 

1. Python3 with the package manager pip must be installed - [Download Python](https://www.python.org/downloads/)

2. Clone the project or download it as .zip and extract it

3. Install the dependencies of the project by typing `pip3 install -r requirements.txt`.

4. Install Exempi for extracting XMP metadata with your default packet manager: e.g. with pacman: `pacman -S exempi`

Now Metadump is ready for use.

## Usage

Execute the following command to display the help text:

    python3 metadump.py -h

Metadump can be run with the following parameters:


    -i or --input               Path to the file or directory which should be analysed

    -f or --filters             Select categories to be displayed

    --filteroptions             Displays the options for the filtering parameter

    --version                   Displays the version of Metadump

    -v / -vv / -vvv             Defines the level of verbosity.

    -l or --limit               Defines the maximum length of the output values (longer values will be cut off)

    -o or --order               Order key-value pairs by their category

    -r or --recursive           If the input is a path to a directory, use this flag to let metadump recursively select all files in this directory and its subdirectories 

    -c or --printcategories     Display categories of each extracted metadata key-value pair

    -s or --stream              Stream the results (the default configuration is that results are displayed only after all files have been analysed).

    --showplugins               Displays all loaded plugins

    -p or --plugins             Specify plugins to be used, other file extensions will be ignored (useful if you want to analyse only a specific type of files in a directory).

    --showemptyfiles            Include names of files for which no metadata could be extracted (the default is false)


## Examples

### Example 1: Extracting metadata from a picture with default settings

```
python3 metadump.py -i ~/Downloads/picture.jpg
```
|KEY                    |   VALUE                            |   DESCRIPTION                             |
|-----------------------|   -------------------------------- | ----------------------------------------- |
|Make                   |   Apple                            |   embedded EXIF metadata
|Model                  |   iPod touch                       |   embedded EXIF metadata
|Software               |   Microsoft Windows Photo Viewer   |   embedded EXIF metadata
|DateTime               |   2012:08:01 14:11:10              |   embedded EXIF metadata
|DateTimeOriginal       |   2012:05:30 21:23:13              |   embedded EXIF metadata
|DateTimeDigitized      |   2012:05:30 21:23:13              |   embedded EXIF metadata
|GPSInfo => Latitude    |   74.87166666666667 N              |   extracted from EXIF GPSInfo metadata
|GPSInfo => Longitude   |   12.3913888888889 W               |   extracted from EXIF GPSInfo metadata
|GPSInfo => Altitude    |   120.16254416961131 meter         |   extracted from EXIF GPSInfo metadata

### Example 2: Extracting metadata from a picture with different parameters

```
python3 metadump.py -i ~/Downloads/picture.jpg -vvv -o -p EXIF -f time location
```

#### CATEGORY: TIME
|KEY                   |   VALUE                  |   DESCRIPTION |
|---                   |   ---                    | ---- |
|GPSInfo:GPSTimeStamp  |   2012:05:30 21:23:13    |   extracted from EXIF GPSInfo metadata
|DateTimeOriginal      |   2012:05:30 21:23:13    |   embedded EXIF metadata
|DateTimeDigitized     |   2012:05:30 21:23:13    |   embedded EXIF metadata
|DateTime              |   2012:08:01 14:11:10    |   embedded EXIF metadata

#### CATEGORY: LOCATION
|KEY                       |   VALUE                            |   DESCRIPTION |
|---                       | ---                                | ---- |
|GPSInfo                   |   {1: 'N', 2: ((77, 1), (5218, 1   |   embedded EXIF metadata
|GPSInfo:GPSLatitudeRef    |   N                                |   extracted from EXIF GPSInfo metadata
|GPSInfo:GPSLatitude       |   ((77, 1), (5218, 100), (0, 1))   |   extracted from EXIF GPSInfo metadata
|GPSInfo:GPSLongitudeRef   |   W                                |   extracted from EXIF GPSInfo metadata
|GPSInfo:GPSLongitude      |   ((12, 1), (2329, 100), (0, 1))   |   extracted from EXIF GPSInfo metadata
|GPSInfo:GPSAltitudeRef    |   Above sea level                  |   extracted from EXIF GPSInfo metadata
|GPSInfo:GPSAltitude       |   (34006, 283)                     |   extracted from EXIF GPSInfo metadata
|GPSInfo => Altitude       |   120.16254416961131 meter         |   extracted from EXIF GPSInfo metadata
|GPSInfo => Latitude       |   74.87166666666667 N              |   extracted from EXIF GPSInfo metadata
|GPSInfo => Longitude      |   12.3913888888889 W               |   extracted from EXIF GPSInfo metadata


### Example 3: Extracting metadata from a word document
```
python3 metadump.py -i ~/Downloads/document.docx -vvv 
```
|KEY                    |   VALUE                            |   DESCRIPTION |
|-----------------------| -----------                        | ---- |
|title                  |   Bill 2018                        |   Microsoft Office - docProps/core.xml
|creator                |   Phantasy Company - Accounting Dept. |   Microsoft Office - docProps/core.xml
|keywords               |   Phantasy Company                 |   Microsoft Office - docProps/core.xml
|description            |   Phantasy Company - Bill 2018     |   Microsoft Office - docProps/core.xml
|lastModifiedBy         |   John Doe - Phantasy Company      |   Microsoft Office - docProps/core.xml
|revision               |   7                                |   Microsoft Office - docProps/core.xml
|lastPrinted            |   2016-02-24T13:43:00Z             |   Microsoft Office - docProps/core.xml
|created                |   2016-02-26T10:36:00Z             |   Microsoft Office - docProps/core.xml
|modified               |   2018-09-20T14:04:00Z             |   Microsoft Office - docProps/core.xml
|Template               |   Normal                           |   Microsoft Office - docProps/app.xml
|TotalTime              |   0                                |   Microsoft Office - docProps/app.xml
|Pages                  |   1                                |   Microsoft Office - docProps/app.xml
|Words                  |   59                               |   Microsoft Office - docProps/app.xml
|Characters             |   378                              |   Microsoft Office - docProps/app.xml
|Application            |   Microsoft Office Word            |   Microsoft Office - docProps/app.xml
|DocSecurity            |   0                                |   Microsoft Office - docProps/app.xml
|Lines                  |   3                                |   Microsoft Office - docProps/app.xml
|Paragraphs             |   1                                |   Microsoft Office - docProps/app.xml
|ScaleCrop              |   false                            |   Microsoft Office - docProps/app.xml
|LinksUpToDate          |   false                            |   Microsoft Office - docProps/app.xml
|CharactersWithSpaces   |   436                              |   Microsoft Office - docProps/app.xml
|SharedDoc              |   false                            |   Microsoft Office - docProps/app.xml
|HyperlinksChanged      |   false                            |   Microsoft Office - docProps/app.xml
|AppVersion             |   15.0000                          |   Microsoft Office - docProps/app.xml